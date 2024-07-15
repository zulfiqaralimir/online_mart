""" Function to create kafka topic """
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError
from payment_service import settings


async def create_kafka_topic():
    """ Function to create kafka topic """
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=settings.BOOTSTRAP_SERVER)
    # start the admin client
    await admin_client.start()
    topic_list = [NewTopic(name=settings.KAFKA_PAYMENT_TOPIC,
                           num_partitions=1, replication_factor=1)]

    try:
        # create the topic
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{settings.KAFKA_PAYMENT_TOPIC}' created successfully")
    except TopicAlreadyExistsError as e:
        print(f"Failed to create topic '{settings.KAFKA_PAYMENT_TOPIC}': {e}")
    finally:
        await admin_client.close()
# end-of-file(EOF)
