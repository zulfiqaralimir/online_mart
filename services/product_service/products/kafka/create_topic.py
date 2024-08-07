""" Function to create kafka topic """
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError
from products.setting import BOOTSTRAP_SERVER, KAFKA_PRODUCT_TOPIC


async def create_kafka_topic():
    """ Function to create kafka topic """
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVER)
    # start the admin client
    await admin_client.start()
    topic_list = [NewTopic(name=KAFKA_PRODUCT_TOPIC,
                           num_partitions=1, replication_factor=1)]

    try:
        # create the topic
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{KAFKA_PRODUCT_TOPIC}' created successfully")
    except TopicAlreadyExistsError as e:
        print(f"Failed to create topic '{KAFKA_PRODUCT_TOPIC}': {e}")
    finally:
        await admin_client.close()
# end-of-file(EOF)
