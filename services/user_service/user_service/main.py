""" User Management Service for Musa's Online Martb"""
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from user_service import auth
from user_service.db import get_session, create_tables
from user_service.models import Register_User, Token, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Creating Tables')
    create_tables()
    print("Tables Created")
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan, title="User Management Service", version='1.0.0')


@app.get('/')
async def root():
    return {"message": "User Management Service"}


# login . username, password
@app.post('/token', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
)->Token:
    user:User|None = auth.authenticate_user(
        form_data.username, form_data.password, session)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    else:
        return auth.token_service(user)


@app.post("/token/refresh", response_model=Token)
def refresh_token(
    old_refresh_token: str,
    session: Annotated[Session, Depends(get_session)]
    )->Token:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"}
    )
    user:User = auth.validate_refresh_token(old_refresh_token, session)
    if not user:
        raise credential_exception
    return auth.token_service(user)


@app.post("/register")
async def regiser_user(
    new_user: Annotated[Register_User, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    db_user = auth.get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(
            status_code=409, detail="User with these credentials already exists")
    user = User(username=new_user.username,
                email=new_user.email,
                password=auth.hash_password(new_user.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f""" User with {user.username} successfully registered """}


@app.get('/profile', response_model=User)
async def user_profile(current_user: Annotated[User, Depends(auth.current_user)])->User:
    return current_user
