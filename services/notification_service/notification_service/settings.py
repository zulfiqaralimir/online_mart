""" Configuration values from environment variables """
from starlette.config import Config
from starlette.datastructures import Secret


try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

BOOTSTRAP_SERVER = config("KAFKA_SERVER", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str)
KAFKA_USERS_TOPIC = config("KAFKA_USERS_TOPIC", cast=str)
KAFKA_NOTIFICATION_ORDER_CONSUMER_GROUP_ID = config(
    "KAFKA_NOTIFICATION_ORDER_CONSUMER_GROUP_ID", cast=str)
KAFKA_NOTIFICATION_PAYMENT_CONSUMER_GROUP_ID = config(
    "KAFKA_NOTIFICATION_PAYMENT_CONSUMER_GROUP_ID", cast=str)
KAFKA_NOTIFICATION_USERS_CONSUMER_GROUP_ID = config(
    "KAFKA_NOTIFICATION_USERS_CONSUMER_GROUP_ID", cast=str)

SENDER_EMAIL = config("SENDER_EMAIL", cast=str)
RECEIVER_EMAIL = config("RECEIVER_EMAIL", cast=str)
EMAIL_PASSWORD = config("EMAIL_PASSWORD", cast=str)
# end-of-file (EOF)
