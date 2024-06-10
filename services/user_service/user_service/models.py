from typing import Annotated
from sqlmodel import SQLModel, Field
from fastapi import Form


class User (SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    # is_verified: bool | None = Field(default=False)


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
