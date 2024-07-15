from typing import Annotated
from sqlmodel import SQLModel, Field
from fastapi import Form


# user model to store credentials
class User (SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str


# user profile data in database
class Profile (SQLModel, table=True):
    username: str | None = Field(default = None, primary_key=True)
    user_id: int | None = Field(default = None, foreign_key="user.id")
    name: str
    email: str
    phone: str
    shipping_address: str
    payment_token: str | None = Field(default = None, unique=True)


# response model when user requests for profile data
class ProfileResponse (SQLModel):
    username: str | None = Field(default = None, primary_key=True)
    user_id: int | None = Field(default = None, foreign_key="user.id")
    name: str
    email: str
    phone: str
    shipping_address: str


# user profile data model for validation: when user creates profile
class ProfileData (SQLModel):
    name: str
    phone: str
    shipping_address: str


# register user validation model
class Register_User (SQLModel):
    username: Annotated[
        str,
        Form(),
    ]
    email: Annotated[
        str,
        Form(),
    ]
    password: Annotated[
        str,
        Form(),
    ]


class Token (SQLModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData (SQLModel):
    username: str


class RefreshTokenData (SQLModel):
    email: str
# end-of-file (EOF)