import logging
from aiokafka import AIOKafkaProducer
from payment_service.settings import BOOTSTRAP_SERVER

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_payment_producer():
    """ Function to create kafka producer """
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
# end-of-file(EOF)
