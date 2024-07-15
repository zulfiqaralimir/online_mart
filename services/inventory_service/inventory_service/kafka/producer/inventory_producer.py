""" Producer to send inventory messages to Kafka Topic Inventory """
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
from inventory_service.settings import BOOTSTRAP_SERVER


async def kafka_producer() -> AsyncGenerator[AIOKafkaProducer, None]:
    """ Function to create kafka producer """
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


kafka_producer_instance: AIOKafkaProducer | None = None


async def get_kafka_producer() -> AIOKafkaProducer:
    global kafka_producer_instance
    if kafka_producer_instance is None:
        kafka_producer_instance = AIOKafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVER)
        await kafka_producer_instance.start()
    return kafka_producer_instance
# end-of-file(EOF)
