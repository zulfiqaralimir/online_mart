import logging
from aiokafka import AIOKafkaProducer
from fastapi import HTTPException
from user_service.proto import user_pb2
from user_service.setting import KAFKA_USERS_TOPIC


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_user_message(
        producer: AIOKafkaProducer,
        message_type: user_pb2.MessageT,
        user_data=None,
        user_id=None
):
    """ Helper function to send user message to Kafka """
    if user_data is not None:
        user_proto = user_pb2.UserProfile(
            user_id=user_data.get('user_id', None),
            username=user_data['username'],
            email=user_data['email'],
            name=user_data['name'],
            phone=user_data['phone'],
            shipping_address=user_data['shipping_address'],
            payment_token=user_data['payment_token'],
        )

        user_message = user_pb2.UserMessage(
            message_type=message_type,
            profile_data=user_proto
        )

    else:
        user_message = user_pb2.UserMessage(
            message_type=message_type,
            user_id=user_id
        )
    serialized_message = user_message.SerializeToString()

    try:
        await producer.send_and_wait(KAFKA_USERS_TOPIC, serialized_message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send message to Kafka: {e}")
# end-of-file (EOF)
