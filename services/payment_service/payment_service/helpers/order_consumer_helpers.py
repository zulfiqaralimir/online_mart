import logging
import json
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from payment_service.proto import order_pb2
from payment_service.db import add_order_to_db
from payment_service import models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_order_message(order_message: order_pb2.OrderMessage):
    """ Function to handle order message """
    try:
        if order_message.message_type == order_pb2.MessageType.create_order:
            order_data = order_message.order_data
            order_payment = await create_order(order_data)
            await add_order_to_db(order_payment)
        else:
            pass

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


# create order payment
async def create_order(order_data):
    """ Function to create order payment """
    order_payment = models.Orders(
        order_id=order_data.order_id,
        user_id=order_data.user_id,
        order_value=order_data.order_value,
        currency=order_data.currency,
    )
    return order_payment
