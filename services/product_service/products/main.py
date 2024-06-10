""" Product Management Service for Musa's Online Mart"""
import asyncio
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from aiokafka import AIOKafkaProducer
from products.models import ProductAdd, ProductEdit, Product
from products.kafka.create_topic import create_kafka_topic
from products.kafka.producer import kafka_producer
from products.proto import product_pb2
from products.helpers import helpers
from products.db import get_products, get_session, get_single_product
from sqlmodel import Session, select

# Current Issue is, how we send response after confirmation.
# Option:1- asynio.sleep(). This migh add latency. And it is also not working in edit_product
# Opption:2- Creating a kafka topic of response, but this will add more latecny and what if consumer is down?
# Option:3- Version number approach. A new field in product table with version number can be added and retries mechanism
# but again this would add latency.


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan Function, will be executed when app starts up """
    print("Product Management Service started...")
    await create_kafka_topic()
    yield
    print("Product Management Service shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="Producer for Product Management Service",
    version='1.0.0'
)


@app.get("/")
async def root():
    """ Root Path for Product Management Service """
    return {"message": "Product Management Service"}


@app.post("/product", response_model=Product)
async def add_product(
    product: ProductAdd,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)]
):
    """ Receive Product from User and send it to Kafka Topic """
    await helpers.send_product_message(
        producer,
        product_pb2.MessageType.add_product,
        product_data=product.model_dump()
    )
    await asyncio.sleep(.5)  # working with .5 second delay
    response = await get_single_product(session)
    if response:
        return response
    else:
        raise HTTPException(
            status_code=404, detail ="Failed to add the product")


@app.put("/product/{product_id}", response_model=Product)
async def edit_product(
    product: ProductEdit,
    product_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)]
):
    """ Receive Product data from User to edit existing product and send it to Kafka Topic """
    existing_product = await get_single_product(session, id=product_id)
    if existing_product:
        product_data = product.model_dump()
        product_data['product_id'] = product_id
        await helpers.send_product_message(producer, product_pb2.MessageType.edit_product, product_data=product_data)
        await asyncio.sleep(3)  # not working with 2 second delay
        try:
            return await get_single_product(session, id=product_id)
        except HTTPException:
            return {"message": "Failed to edit the product"}
    else:
        raise HTTPException(
            status_code=404, detail =f"No Product found with id:{product_id}")


@app.delete("/product/{product_id}")
async def delete_product(
    product_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)]
):
    """ Receive Product Id from User to delete the product and send it to Kafka Topic """
    existing_product = await get_single_product(session, id=product_id)
    if existing_product:
        await helpers.send_product_message(producer, product_pb2.MessageType.delete_product, product_id=product_id)
        await asyncio.sleep(.5)  # working with .5
        try:
            deleted_product = await get_single_product(session, id=product_id)
        except HTTPException:
            return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(
            status_code=404, detail =f"No Product found with id:{product_id}")


@app.get("/product", response_model=list[Product])
async def get_all_products(session: Annotated[Session, Depends(get_session)]):
    """ Function to get all products from database """
    return await get_products(session)


@app.get("/product/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Function to get all products from database """
    return await get_single_product(session, id=product_id)
