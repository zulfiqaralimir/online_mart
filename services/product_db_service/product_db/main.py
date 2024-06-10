import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiokafka import AIOKafkaConsumer
from product_db import db
from product_db import setting
from product_db.proto import product_pb2
from product_db.helpers import helpers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan Function, will be executed when app starts up """
    db.create_tables()
    print("Product DB App started...")
    print("Tables Created")
    loop = asyncio.get_event_loop()
    consume_task = loop.create_task(consume_products())
    yield
    consume_task.cancel()
    await consume_task

app: FastAPI = FastAPI(
    lifespan=lifespan, title="Product Db Service", version='1.0.0')


async def consume_products():
    consumer = AIOKafkaConsumer(
        setting.KAFKA_PRODUCT_TOPIC,
        bootstrap_servers=setting.BOOTSTRAP_SERVER,
        group_id=setting.KAFKA_CONSUMER_GROUP_ID,
        enable_auto_commit=True
        # auto_offset_reset="earliest"
    )

    await consumer.start()
    print("consumer started....")
    try:
        async for msg in consumer:
            if msg.value is not None:
                product_message = product_pb2.ProductMessage()
                product_message.ParseFromString(msg.value)
                print(product_message)
                await helpers.handle_product_message(product_message)
            else:
                print("Received message with no value")
    finally:
        await consumer.stop()
