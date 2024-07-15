from aiokafka import AIOKafkaProducer
from fastapi import Depends, HTTPException
from typing import Annotated
from payment_service.proto import payment_pb2
from payment_service.kafka.producers.payment_producer import create_payment_producer
from payment_service.settings import KAFKA_PAYMENT_TOPIC


async def send_payment_message(
        payment_message,
        producer: Annotated[AIOKafkaProducer, Depends(create_payment_producer)]
):
    """ send payment message """
    payment_message = payment_pb2.PaymentMessage(
        order_id=payment_message.order_id,
        user_id=payment_message.user_id,
        payment_status=payment_message.payment_status
    )
    serialized_message = payment_message.SerializeToString()
    try:
        await producer.send_and_wait(topic=KAFKA_PAYMENT_TOPIC, value=serialized_message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send message to Kafka: {e}")
# end-of-file (EOF)
