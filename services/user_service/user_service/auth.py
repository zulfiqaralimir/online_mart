""" Authentication for User Management Service """
from datetime import datetime, timezone, timedelta
from typing import Annotated
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from user_service.models import RefreshTokenData, TokenData, User, Token
from user_service.db import get_session


SECRET_KEY = 'ed60732905aeb0315e2f77d05a6cb57a0e408eaf2cb9a77a5a2667931c50d4e0'
ALGORITHYM = 'HS256'
EXPIRY_TIME = 30
REFRESH_EXPIRY_DAYS = 7


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes="bcrypt")


def hash_password(password) -> str:
    """ function to create password hash """
    return pwd_context.hash(password)


def verify_password(password, password_hash) -> bool:
    """ function to verify password hash """
    return pwd_context.verify(password, password_hash)


def get_user_from_db(
        session: Annotated[Session, Depends(get_session)],
        username: str | None = None,
        email: str | None = None
) -> User | None:
    """ function to get user from db """
    statement = select(User).where(User.username == username)
    user: User | None = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == email)
        user: User | None = session.exec(statement).first()
        if user:
            return user
    return user


def authenticate_user(
        username,
        password,
        session: Annotated[Session, Depends(get_session)]
) -> User | None:
    """ function to authenticate user with username and password """
    db_user = get_user_from_db(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


def create_access_token(
        data: dict,
        expiry_time: timedelta | None
):
    """ function to generate access token """
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encode, SECRET_KEY, algorithm=ALGORITHYM, )
    return encoded_jwt


def current_user(
        token: Annotated[str, Depends(oauth_scheme)],
        session: Annotated[Session, Depends(get_session)]
) -> User:
    """ function to verify access token """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
        username: str | None = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    user = get_user_from_db(session, username=token_data.username)
    if not user:
        raise credential_exception
    return user


def create_refresh_token(
        data: dict,
        expiry_time: timedelta | None
) -> str:
    """ function to create refresh token """
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encode, SECRET_KEY, algorithm=ALGORITHYM, )
    return encoded_jwt


def validate_refresh_token(
        token: str,
        session: Annotated[Session, Depends(get_session)]
):
    """ function to validate refresh token """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
        email: str | None = payload.get("sub")
        if email is None:
            raise credential_exception
        token_data = RefreshTokenData(email=email)

    except:
        raise JWTError
    user = get_user_from_db(session, email=token_data.email)
    if not user:
        raise credential_exception
    return user


def token_service(user: User) -> Token:
    """ function to generate access token and refresh token upon successful login """
    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token(
        {"sub": user.username}, expire_time)
    refresh_expire_time = timedelta(days=REFRESH_EXPIRY_DAYS)
    refresh_token = create_refresh_token(
        {"sub": user.email}, refresh_expire_time)
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)
