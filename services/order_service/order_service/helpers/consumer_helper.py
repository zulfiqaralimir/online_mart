import logging
import json
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from order_service.proto import order_pb2, payment_pb2
from order_service import models
from order_service.db import add_order_to_db, get_order_from_db, delete_order_in_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def protobuf_timestamp_to_datetime(proto_timestamp: Timestamp) -> datetime:
    """Convert Protobuf Timestamp to Python datetime."""
    return datetime.fromtimestamp(proto_timestamp.seconds + proto_timestamp.nanos / 1e9)


# helper for kafka order consumer
async def handle_order_message(order_message: order_pb2.OrderMessage):
    """ Function to handle order message """
    try:
        if order_message.message_type == order_pb2.MessageType.create_order:
            order_data = order_message.order_data
            order = await generate_order(order_data)
            await add_order_to_db(order)

        elif order_message.message_type == order_pb2.MessageType.edit_order:
            order_data = order_message.order_data
            order = await generate_order(order_data)

            # get existing order
            existing_order = await get_order_from_db(order_data.order_id)
            if existing_order:
                existing_order.user_id = order.user_id
                existing_order.order_date = order.order_date
                existing_order.order_value = order.order_value
                existing_order.currency = order.currency
                existing_order.order_items = order.order_items
                await add_order_to_db(existing_order)

        elif order_message.message_type == order_pb2.MessageType.cancel_order:
            order_id = order_message.order_id
            existing_order = await get_order_from_db(order_id)
            if existing_order:
                existing_order.order_status = models.OrderStatusEnum.cancelled
                await add_order_to_db(existing_order)

        elif order_message.message_type == order_pb2.MessageType.delete_order:
            order_id = order_message.order_id
            await delete_order_in_db(order_id)

        else:
            raise HTTPException(
                status_code=500, detail="Invalid order message type")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
    except KeyError as e:
        logger.error(f"Missing key in order data: {e}")
    except ValueError as e:
        logger.error(f"Value error in order data: {e}")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {e}")


# helper functions for handle_order_message function
async def generate_order(order_data: order_pb2.Order):
    order_date = protobuf_timestamp_to_datetime(order_data.order_date)
    order = models.Orders(
        order_id=order_data.order_id,
        user_id=order_data.user_id,
        order_date=order_date,
        order_value=order_data.order_value,
        currency=order_data.currency,
        order_status=models.order_status_proto_to_sqlmodel[order_data.order_status],
        payment_status=models.payment_status_proto_to_sqlmodel[order_data.payment_status],
        shipping_status=models.shipping_status_proto_to_sqlmodel[order_data.shipping_status]
    )

    for item in order_data.order_items:
        order_item = models.OrderItems(
            product_code=item.product_code,
            product_name=item.product_name,
            product_description=item.product_description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        order.order_items.append(order_item)
    return order


# helper for payment consumer
async def handle_payment_message(payment_message: payment_pb2.PaymentMessage):
    """ Function to handle payment message """
    try:
        order_id = payment_message.order_id
        existing_order = await get_order_from_db(order_id)
        if existing_order:
            if payment_message.payment_status == "success":
                existing_order.payment_status = models.PaymentStatusEnum.success
            else:
                existing_order.payment_status = models.PaymentStatusEnum.failed
            await add_order_to_db(existing_order)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
    except KeyError as e:
        logger.error(f"Missing key in order data: {e}")
    except ValueError as e:
        logger.error(f"Value error in order data: {e}")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {e}")
# end of file (EOF)
