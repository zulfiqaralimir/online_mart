""" Producer to send order messages to Kafka Topic orders """
from aiokafka import AIOKafkaProducer
from order_service.settings import BOOTSTRAP_SERVER


async def kafka_producer():
    """ Function to create kafka producer """
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
# end-of-file(EOF)
