import logging
import json
from sqlite3 import IntegrityError
from fastapi import HTTPException
from payment_service.proto import user_pb2
from payment_service import db
from payment_service.models import Users


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_user_message(user_message):
    try:
        if user_message.message_type == user_pb2.MessageT.add_user:
            user_data = user_message.profile_data
            logger.info(
                f"user data in payment user consumer add user: {user_data}")
            user = Users(
                username=user_data.username,
                user_id=user_data.user_id,
                email=user_data.email,
                phone=user_data.phone,
                shipping_address=user_data.shipping_address,
                payment_token=user_data.payment_token,
            )
            await db.add_user_to_db(user)

        elif user_message.message_type == user_pb2.MessageT.edit_user:
            user_data = user_message.profile_data
            user = await db.edit_user_in_db(user_data)

        elif user_message.message_type == user_pb2.MessageT.delete_user:
            user_id = user_message.user_id
            await db.delete_user_in_db(user_id)

        else:
            raise HTTPException(
                status_code=500, detail="Invalid user message type")

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
    except KeyError as e:
        logger.error(f"Missing key in user data: {e}")
    except ValueError as e:
        logger.error(f"Value error in user data: {e}")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {e}")
# end-of-file (EOF)
