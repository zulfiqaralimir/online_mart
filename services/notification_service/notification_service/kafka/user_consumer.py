import logging
from aiokafka import AIOKafkaConsumer
from notification_service import settings
from notification_service.proto import user_pb2
from notification_service.helpers.user_helpers import handle_user_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume_user_message():
    """ Consumer to consume messages from Kafka Users Topic """
    consumer = AIOKafkaConsumer(
        settings.KAFKA_USERS_TOPIC,
        bootstrap_servers=settings.BOOTSTRAP_SERVER,
        group_id=settings.KAFKA_NOTIFICATION_USERS_CONSUMER_GROUP_ID,
        enable_auto_commit=True,
        auto_offset_reset="earliest"
    )
    await consumer.start()
    print("consumer started....")
    try:
        async for msg in consumer:
            if msg.value is not None:
                user_message = user_pb2.UserMessage()
                user_message.ParseFromString(msg.value)
                await handle_user_message(user_message)
            else:
                logger.info("Received message with no value")
    finally:
        await consumer.stop()
# end-of-file (EOF)
