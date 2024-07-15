import logging
from aiokafka import AIOKafkaConsumer
from notification_service import settings
from notification_service.helpers.payment_helpers import handle_payment_message
from notification_service.proto import payment_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume_payments():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_PAYMENT_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.KAFKA_NOTIFICATION_PAYMENT_CONSUMER_GROUP_ID,
        enable_auto_commit=True
        # auto_offset_reset="earliest"
    )

    await consumer.start()
    print("consumer started....")
    try:
        async for msg in consumer:
            if msg.value is not None:
                payment_message = payment_pb2.PaymentMessage()
                payment_message.ParseFromString(msg.value)
                await handle_payment_message(payment_message)
            else:
                print("Received message with no value")
    finally:
        await consumer.stop()
# end-of-file (EOF)
