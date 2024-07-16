""" Payment Service for Musa's Online Mart """
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from aiokafka import AIOKafkaProducer
from payment_service.db import create_tables, get_order_from_db, add_payment_to_db, get_payment_from_db
from payment_service.kafka.consumers.order_consumer import consume_order_message
from payment_service.kafka.consumers.user_consumer import consume_user_message
from payment_service import models
from payment_service.stripe.stripe_service import create_payment
from payment_service.helpers.producer_helpers import send_payment_message
from payment_service.kafka.producers.payment_producer import create_payment_producer
from payment_service.kafka.producers.payment_topic import create_kafka_topic


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan Function, will be executed when app starts up """
    print("Payment Service started...")
    create_tables()
    await create_kafka_topic()
    print("Tables Created")
    loop = asyncio.get_event_loop()
    consume_order_task = loop.create_task(consume_order_message())
    consume_user_task = loop.create_task(consume_user_message())
    yield
    consume_order_task.cancel()
    consume_user_task.cancel()
    await asyncio.gather(consume_order_task, consume_user_task, return_exceptions=True)


app = FastAPI(
    lifespan=lifespan,
    title="Payment Service",
    version='1.0.0'
)


@app.get("/")
async def root():
    """ Root Path for Payment Service """
    return {"message": "Welcome to Payment Service"}


@app.post("/payments", response_model=models.PaymentResponse)
async def process_payment(
    payment_request: models.PaymentRequest,
    producer: Annotated[AIOKafkaProducer, Depends(create_payment_producer)]
):
    try:
        # create payment with stripe
        payment_request_result = await create_payment(payment_request)
        # add payment to database
        payment = models.Payments(
            order_id=payment_request.order_id,
            user_id=payment_request.user_id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            payment_status=payment_request_result.payment_status
        )
        await add_payment_to_db(payment)
        logger.info(f"payment in producer {payment}")
        await send_payment_message(payment, producer)
        return payment_request_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payments/retry_payment", response_model=models.PaymentResponse | dict[str, str])
async def retry_payment(
    payment: models.PaymentRequest,
    producer: Annotated[AIOKafkaProducer, Depends(create_payment_producer)]
):
    try:
        existing_payment = await get_payment_from_db(payment.order_id)
        if existing_payment is None:
            raise HTTPException(
                status_code=404, detail="Payment Record not found")

        if existing_payment.payment_status == "success":
            return {"message": "Payment Already Successfull"}
        
        if existing_payment.payment_status == "failed":
            payment_request_result = await create_payment(payment)
            existing_payment.payment_status = payment_request_result.payment_status
            await add_payment_to_db(existing_payment)
            await send_payment_message(existing_payment, producer)
            return payment_request_result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# end-of-file(EOF)