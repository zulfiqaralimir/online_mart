import logging
from aiokafka import AIOKafkaProducer
from fastapi import HTTPException
from google.protobuf.timestamp_pb2 import Timestamp
from order_service.proto import order_pb2
from order_service.settings import KAFKA_ORDER_TOPIC
from order_service import models


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_order_message(
        producer: AIOKafkaProducer,
        message_type: order_pb2.MessageType,
        order_data=None,
        order_id=None
):
    """ Helper function to send order message to Kafka """
    order_message = None
    if order_data is not None:
        try:
            # create order items
            order_items_data = order_data.get('order_items', [])
            order_items = []
            for item in order_items_data:
                order_item = order_pb2.OrderItem(
                    order_item_id=item.get('order_item_id', None),
                    order_id=item.get('order_id', None),
                    product_code=item['product_code'],
                    product_name=item['product_name'],
                    product_description=item['product_description'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    total_price=item['total_price'],
                )
                order_items.append(order_item)

            # create order
            order = order_pb2.Order(
                order_id=order_data.get('order_id'),
                user_id=order_data['user_id'],
                order_date=None if order_data.get('order_date') is None else Timestamp(
                    seconds=int(order_data['order_date'].timestamp())),
                order_value=order_data['order_value'],
                currency=order_data['currency'],
                order_items=order_items
            )
            order_message = order_pb2.OrderMessage(
                message_type=message_type,
                order_data=order
            )

        except KeyError as e:
            logger.error(f"Missing key in order data: {e}")
        except ValueError as e:
            logger.error(f"Value error in order data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    else:
        order_message = order_pb2.OrderMessage(
            message_type=message_type,
            order_id=order_id
        )

    if order_message:
        serialized_message = order_message.SerializeToString()
        try:
            await producer.send_and_wait(KAFKA_ORDER_TOPIC, serialized_message)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to send message to Kafka: {e}")
    else:
        raise HTTPException(
            status_code=500, detail="Failed to create order message")


async def convert_order_to_pydantic(order: models.Orders) -> models.OrderResponse:
    """Function to convert received order to pydantic model"""
    return models.OrderResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        order_date=order.order_date,
        order_value=order.order_value,
        currency=order.currency,
        order_status=order.order_status,
        payment_status=order.payment_status,
        shipping_status=order.shipping_status,
        order_items=[models.OrderItemRead.model_validate(
            item) for item in order.order_items] if order.order_items else []
    )
# end-of-file(EOF)
