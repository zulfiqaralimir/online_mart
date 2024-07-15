""" Database functionality for Order Database Service """
import logging
from fastapi import HTTPException
from sqlmodel import create_engine, SQLModel, Session, select
from payment_service import settings, models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection_string: str = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")
engine = create_engine(connection_string, connect_args={},
                       pool_recycle=300, pool_size=10)


def create_tables() -> None:
    """ Function to create tables in database """
    SQLModel.metadata.create_all(engine)


def get_session():
    """ Function to get session """
    with Session(engine) as session:
        yield session


async def add_user_to_db(user: models.Users):
    """ Add user to the database """
    try:
        logger.info(f"Add_user in db {user}")
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
    except Exception as http_excep:
        raise http_excep


# get single user from db
async def get_user_from_db(user_id: int) -> models.Users | None:
    """ Get user from db """
    try:
        with Session(engine) as session:
            statement = select(models.Users).where(
                models.Users.user_id == user_id)
            user = session.exec(statement).first()
            session.add(user)
            session.commit()
            session.refresh(user)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except Exception as http_excep:
        raise http_excep


# edit user in db
async def edit_user_in_db(user_data: models.Users):
    """ Edit user in the database """
    try:
        with Session(engine) as session:
            # get existing user from db
            logger.info(f"inside db edit_user_in_db {user_data.user_id}")
            existing_user = await get_user_from_db(user_data.user_id)
            if existing_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            # update existing user in db
            existing_user.email = user_data.email
            existing_user.phone = user_data.phone
            existing_user.shipping_address = user_data.shipping_address
            existing_user.payment_token = user_data.payment_token
            session.add(existing_user)
            session.commit()
            session.refresh(existing_user)
            return existing_user

    except HTTPException as http_excep:
        raise http_excep
    except Exception as e:
        raise e

# delete order from db
async def delete_user_in_db(user_id: int):
    """ Delete existing order in the database """
    with Session(engine) as session:
        session.delete(session.get(models.Users, user_id))
        session.commit()


# add order for payment to db
async def add_order_to_db(order: models.Orders):
    """ Add new payment to the database """
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)
        return order

# get existing order from db
async def get_order_from_db(order_id: str) -> models.Orders | None:
    """ Get order from db """
    with Session(engine) as session:
        statement = select(models.Orders).where(
            models.Orders.order_id == order_id)
        order = session.exec(statement).first()
        return order


async def add_payment_to_db(payment: models.Payments):
    """ Add new payment to the database """
    with Session(engine) as session:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment


async def get_payment_from_db(order_id: str) -> models.Payments | None:
    """ Get payment from db """
    with Session(engine) as session:
        statement = select(models.Payments).where(
            models.Payments.order_id == order_id)
        payment = session.exec(statement).first()
        return payment


async def edit_payment_in_db(existing_payment: models.Payments):
    """ Edit payment in the database """
    with Session(engine) as session:
        session.add(existing_payment)
        session.commit()
        session.refresh(existing_payment)
        return existing_payment
# end-of-file(EOF)
