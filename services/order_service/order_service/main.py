""" Order Service for Musa's Online Mart """
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from typing import Annotated
from aiokafka import AIOKafkaProducer
from order_service.kafka.producers.order_producer import kafka_producer
from order_service.kafka.producers.create_topic import create_kafka_topic
from order_service.helpers.helpers import send_order_message, convert_order_to_pydantic
from order_service.proto import order_pb2
from order_service.models import OrderCreate, OrderMessage, OrderResponse, Orders, generate_order_id
from order_service.db import create_tables, get_order_from_db, get_all_orders_from_db
from order_service.kafka.consumers.order_consumer import consume_order_message
from order_service.kafka.consumers.payment_consumer import consume_payment_message


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan Function, will be executed when app starts up """
    print("Order Management Service started...")
    create_tables()
    await create_kafka_topic()
    print("Tables Created")
    loop = asyncio.get_event_loop()
    consume_task_order = loop.create_task(consume_order_message())
    consume_task_payment = loop.create_task(consume_payment_message())
    yield
    consume_task_order.cancel()
    consume_task_payment.cancel()
    await asyncio.gather(consume_task_order, consume_task_payment, return_exceptions=True)


app = FastAPI(
    lifespan=lifespan,
    title="Order Management Service",
    version='1.0.0'
)


@app.get("/")
async def root():
    """ Root Path for Order Management Service """
    return {"message": "Welcome to Order Management Service"}


# Create Order
@app.post("/orders")
async def create_order(order: OrderCreate, producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]):
    """ send add new order message to kafka """

    order_id = generate_order_id()
    order = OrderMessage(**order.model_dump(), order_id=order_id)
    await send_order_message(
        producer,
        order_pb2.MessageType.create_order,
        order_data=order.model_dump(),
    )
    return {"message": f"Create order request submitted successfully", "order_id": order_id}


# Read single order
@app.get("/orders/{order_id}", response_model=OrderResponse)
async def read_single_order(order_id: str):
    """ read order from db """
    db_order = await get_order_from_db(order_id)
    order_read = await convert_order_to_pydantic(db_order)
    return order_read


# Read all orders
@app.get("/orders", response_model=list[OrderResponse])
async def read_all_order():
    """ read order from db """
    db_orders = await get_all_orders_from_db()
    all_orders: list[OrderResponse] = []
    for order in db_orders:
        order_read = await convert_order_to_pydantic(order)
        all_orders.append(order_read)
    return all_orders


# Edit Order
@app.put("/orders/{order_id}")
async def edit_order(
    order: OrderCreate,
    order_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    """ send edit order message to kafka"""
    order_data = order.model_dump()
    order_data['order_id'] = order_id
    await send_order_message(
        producer,
        order_pb2.MessageType.edit_order,
        order_data=order_data
    )
    return {"message": "order edit request submitted successfully"}

# cancel order


@app.patch("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    """ send edit order message to kafka"""

    await send_order_message(
        producer,
        order_pb2.MessageType.cancel_order,
        order_id=order_id
    )
    return {"message": "Cancel Order request submitted successfully"}


# delete order
@app.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)]
):
    """ send delete order message to kafka"""
    await send_order_message(
        producer,
        order_pb2.MessageType.delete_order,
        order_id=order_id
    )
    return {"message": "delete order request submitted successfully"}
# end-of-file (EOF)
