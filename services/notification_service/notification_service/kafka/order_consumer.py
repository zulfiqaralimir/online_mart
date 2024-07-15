import logging
from aiokafka import AIOKafkaConsumer
from notification_service import settings
from notification_service.helpers.orders_helpers import handle_order_message
from notification_service.proto import order_pb2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume_order_message():
    """ Consumer to consume messages from Kafka Order Topic """
    consumer = AIOKafkaConsumer(
        settings.KAFKA_ORDER_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.KAFKA_NOTIFICATION_ORDER_CONSUMER_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest"
    )
    await consumer.start()
    print("consumer started....")
    try:
        async for msg in consumer:
            if msg.value is not None:
                order_message = order_pb2.OrderMessage()
                order_message.ParseFromString(msg.value)
                await handle_order_message(order_message)
            else:
                logger.info("Received message with no value")
    finally:
        await consumer.stop()
