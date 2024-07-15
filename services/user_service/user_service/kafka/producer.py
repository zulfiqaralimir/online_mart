""" Producer to send user messages to Kafka Topic orders """
from aiokafka import AIOKafkaProducer
from user_service.setting import BOOTSTRAP_SERVER


async def kafka_producer():
    """ Function to create kafka producer """
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
# end-of-file(EOF)