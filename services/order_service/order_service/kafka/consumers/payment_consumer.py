from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException
from order_service import settings
from order_service.proto import payment_pb2
from order_service.helpers.consumer_helper import handle_payment_message


async def consume_payment_message():
    """ Consumer to consume messages from Kafka Payment Topic """
    consumer = AIOKafkaConsumer(
        settings.KAFKA_PAYMENT_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.KAFKA_ORDER_PAYMENT_CONSUMER_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest"
    )
    await consumer.start()
    print("consumer started....")
    try:
        async for msg in consumer:
            if msg.value is not None:
                payment_message = payment_pb2.PaymentMessage()
                payment_message.ParseFromString(msg.value)
                await handle_payment_message(payment_message)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {e}")
    finally:
        await consumer.stop()
# end-of-file (EOF)
