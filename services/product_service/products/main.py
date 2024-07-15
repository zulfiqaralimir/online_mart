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


@app.post("/product")
async def add_product(
    product: ProductAdd,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)]
):
    """ Receive Product from User and send it to Kafka Topic """
    try:
        await helpers.send_product_message(
            producer,
            product_pb2.MessageType.add_product,
            product_data=product.model_dump()
        )
        return {"message": "Product added message sent successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add product: {e}")


# edit product
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

        try:
            await helpers.send_product_message(
                producer,
                product_pb2.MessageType.edit_product,
                product_data=product_data
            )
            return {"message": "Product edited message sent successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to edit product: {e}")
    else:
        raise HTTPException(
            status_code=404, detail=f"No Product found with id:{product_id}")


@app.delete("/product/{product_id}")
async def delete_product(
    product_id: int,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)]
):
    """ Receive Product Id from User to delete the product and send it to Kafka Topic """
    existing_product = await get_single_product(session, id=product_id)
    if existing_product:
        try:
            await helpers.send_product_message(
                producer,
                product_pb2.MessageType.delete_product,
                product_id=product_id
            )
            return {"message": "Delete Product message sent successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete product: {e}")
    else:
        raise HTTPException(
            status_code=404, detail=f"No Product found with id:{product_id}")


@app.get("/product", response_model=list[Product])
async def get_all_products(session: Annotated[Session, Depends(get_session)]):
    """ Function to get all products from database """
    return await get_products(session)


@app.get("/product/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Function to get all products from database """
    return await get_single_product(session, id=product_id)
# end-of-file(EOF)
