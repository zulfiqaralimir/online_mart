import logging
import json
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from notification_service.db import get_user_from_db
from notification_service.proto import payment_pb2
from notification_service import models
from notification_service.helpers.notification_helpers import send_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_payment_message(payment_message: payment_pb2.PaymentMessage):
    """ Function to handle payment message """
    try:
        user = await get_user_from_db(payment_message.user_id)
        if user:
            user_email = user.email

        if payment_message.payment_status == 'success':
            body: str = f"""
            Your payment for Order Id: {payment_message.order_id}
            has been successfull. Thank you for shopping with us.
            """
            subject: str = "Payment Update"
            await send_email(body, subject, user_email)

        elif payment_message.payment_status == 'failed':
            body: str = f"""
            Your payment for Order Id: {payment_message.order_id}
            has been failed. Please try again!
            """
            subject: str = "Payment Update"
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
