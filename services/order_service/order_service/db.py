""" Database functionality for Order Database Service """
import logging
import uuid
from fastapi import HTTPException
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.orm import joinedload, selectinload
from order_service import settings, models


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


async def add_order_to_db(order: models.Orders):
    """ Add new order to the database """
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)


# get single order from db
async def get_order_from_db(order_id: str):
    """ Get order from db """
    with Session(engine) as session:
        """ Eager Loading (joinedload or selectinload): Fetches related data in a single query, 
        reducing the number of database round-trips.
        joinedload: Joins the related tables in the same query, 
        which can be efficient but may result in more complex queries.
        selectinload: Executes a separate query for each relationship, 
        which can be more readable and sometimes more efficient, especially for large data sets."""

        result = session.exec(
            select(models.Orders)
            .options(
                joinedload(models.Orders.order_items),
            )
            .where(models.Orders.order_id == order_id)
        ).first()
        if result is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return result


# delete order from db
async def delete_order_in_db(order_id: str):
    """ Delete existing order in the database """
    with Session(engine) as session:
        session.delete(session.get(models.Orders, order_id))
        session.commit()


# get single order from db
async def order_from_db(order_id: str):
    """ Get order from db """
    with Session(engine) as session:
        result = session.exec(select(models.Orders).where(
            models.Orders.order_id == order_id))
        db_order = result.one()

        response_order = models.Orders(
            order_id=db_order.order_id,
            user_id=db_order.user_id,
            order_date=db_order.order_date,
            order_value=db_order.order_value,
            currency=db_order.currency,
            order_status=db_order.order_status,
            payment_status=db_order.payment_status,
            shipping_status=db_order.shipping_status,
            order_items=[item for item in db_order.order_items],
        )
        return response_order


# get all orders from db
async def get_all_orders_from_db():
    """ Get all orders from db """
    with Session(engine) as session:
        statement = select(models.Orders).options(
            joinedload(models.Orders.order_items),
        )
        result = session.exec(statement)
        orders = result.unique().all()

        if orders is None:
            raise HTTPException(status_code=404, detail="Order not found")
        # order_list = [models.OrderResponse.model_validate(order) for order in orders]
        return orders
