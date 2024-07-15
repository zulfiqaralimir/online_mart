""" Models for Notification Service """
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    user_id: int = Field(unique=True)
    email: str = Field(unique=True)
    phone: str
    shipping_address: str
    payment_token: str
# end-of-file (EOF)
