""" Producer to send messages to Kafka Topic """
from aiokafka import AIOKafkaProducer
from products.setting import BOOTSTRAP_SERVER


async def kafka_producer():
    """ Function to create kafka producer """
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
# end-of-file(EOF)
