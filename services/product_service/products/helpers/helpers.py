from aiokafka import AIOKafkaProducer
from fastapi import HTTPException
from products.setting import KAFKA_PRODUCT_TOPIC
from products.proto import product_pb2


async def send_product_message(
        producer: AIOKafkaProducer,
        message_type: product_pb2.MessageType,
        product_data=None,
        product_id=None
):
    """ Helper function to send product message to Kafka """
    if product_data is not None:
        product_proto = product_pb2.Product(
            product_id=product_data.get('product_id', None),
            product_title=product_data['product_title'],
            product_description=product_data['product_description'],
            price=product_data['price'],
            currency=product_data['currency'],
            category=product_data['category'],
            brand=product_data['brand'],
            product_code=product_data['product_code']
        )

        product_message = product_pb2.ProductMessage(
            message_type=message_type,
            product_data=product_proto
        )

    else:
        product_message = product_pb2.ProductMessage(
            message_type=message_type,
            product_id=product_id
        )
    serialized_message = product_message.SerializeToString()

    try:
        await producer.send_and_wait(KAFKA_PRODUCT_TOPIC, serialized_message)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send message to Kafka: {e}")
# end-of-file
