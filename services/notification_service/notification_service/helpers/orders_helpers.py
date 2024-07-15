import logging
import json
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from notification_service.db import get_user_from_db
from notification_service.proto import order_pb2
from notification_service import models
from notification_service.helpers.notification_helpers import send_email


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_order_message(order_message: order_pb2.OrderMessage):
    """ Function to handle order message """
    try:
        order_data = order_message.order_data
        user = await get_user_from_db(order_data.user_id)
        if user:
            user_email = user.email

        if order_message.message_type == order_pb2.MessageType.create_order:
            body: str = f"""
            Your Order with Order Id: {order_data.order_id}
            has been created successfully. Thank you for shopping with us.
            """
            subject: str = "Order Created"
            await send_email(body, subject, user_email)

        elif order_message.message_type == order_pb2.MessageType.edit_order:
            body: str = f"""
            Your Order with Order Id: {order_data.order_id} has been edited successfully.
            """
            subject: str = "Order Updated"
            await send_email(body, subject, user_email)

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
