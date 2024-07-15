""" Inventory Service for Musa's Online Mart """
import logging
import asyncio
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated, AsyncGenerator
from inventory_service.db import add_inventory_in_db, create_tables, get_invetory_of_single_product, get_session
from inventory_service.kafka.producer.create_topic import create_kafka_topic
from inventory_service.models import Inventory, InventoryUpdate
from inventory_service.helpers.producer_helpers import send_inventory_message
from inventory_service.kafka.producer.inventory_producer import get_kafka_producer, kafka_producer
from inventory_service.kafka.consumers.order_consumer import consume_order_message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """ Lifespan Function, will be executed when app starts up """

    global kafka_producer_instance
    print("Inventory Service started...")
    await create_kafka_topic()
    kafka_producer_instance = await get_kafka_producer()
    create_tables()
    loop = asyncio.get_event_loop()
    consume_task = loop.create_task(
        consume_order_message())
    yield
    consume_task.cancel()
    await consume_task
    if kafka_producer_instance is not None:
        await kafka_producer_instance.stop()
        kafka_producer_instance = None
    print("Inventory Service shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="Inventory Service",
    version='1.0.0'
)

app.router.lifespan_context = lifespan


@app.get("/")
async def root():
    return {"message": "Inventory Service"}


@app.post("/inventory", response_model=Inventory)
async def create_inventory(
    inventory: InventoryUpdate,
    session: Annotated[Session, Depends(get_session)]
):

    create_inventory = Inventory(**inventory.model_dump())
    try:
        created_inventory = add_inventory_in_db(session, create_inventory)
        result = get_invetory_of_single_product(
            inventory.product_code, session)
        if result:
            await send_inventory_message(result)
        return created_inventory
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.patch("/inventory", response_model=Inventory)
async def edit_inventory(
    inventory: InventoryUpdate,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        existing_product = get_invetory_of_single_product(
            inventory.product_code, session)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        if existing_product.damaged is not None:
            existing_product.damaged += inventory.damaged
            session.add(existing_product)
            session.commit()
            session.refresh(existing_product)
        result = get_invetory_of_single_product(
            inventory.product_code, session)
        if result:
            await send_inventory_message(result)
        return existing_product
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
