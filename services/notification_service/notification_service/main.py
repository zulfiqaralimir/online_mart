""" Notification Service for Musa's Online Mart """
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from notification_service.kafka.order_consumer import consume_order_message
from notification_service.kafka.payment_consumer import consume_payments
from notification_service.kafka.user_consumer import consume_user_message
from notification_service import db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan Function, will be executed when app starts up """
    db.create_tables()
    print("Product DB App started...")
    print("Tables Created")
    loop = asyncio.get_event_loop()
    consume_payment_task = loop.create_task(consume_payments())
    consume_users_task = loop.create_task(consume_user_message())
    consume_order_task = loop.create_task(consume_order_message())
    yield
    consume_payment_task.cancel()
    consume_users_task.cancel()
    consume_order_task.cancel()
    await asyncio.gather(consume_payment_task, consume_users_task, consume_order_task, return_exceptions=True)


app: FastAPI = FastAPI(
    lifespan=lifespan, title="Notification Service", version='1.0.0')
# end-of-file (EOF)
