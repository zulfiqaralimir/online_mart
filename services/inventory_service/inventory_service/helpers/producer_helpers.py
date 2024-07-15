import logging
from fastapi import HTTPException
from inventory_service.kafka.producer.inventory_producer import get_kafka_producer
from inventory_service.proto import inventory_pb2
from inventory_service.settings import KAFKA_INVENTORY_TOPIC
from inventory_service.models import Inventory


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_inventory_message(inventory_data: Inventory):
    """ Helper function to send inventory message to Kafka """

    global kafka_producer_instance
    producer = await get_kafka_producer()

    # create inventory
    inventory_message = inventory_pb2.InventoryUpdate(
        inv_id=inventory_data.inv_id,
        product_code=inventory_data.product_code,
        stock_available=inventory_data.calculate_stock_available()
    )
    serialized_message = inventory_message.SerializeToString()

    try:
        await producer.send_and_wait(KAFKA_INVENTORY_TOPIC, serialized_message)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to send message to Kafka: {e}")
