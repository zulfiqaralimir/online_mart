""" Database functionality for Inventory Database Service """
import logging
from typing import Annotated
from fastapi import Depends, HTTPException
from inventory_service.helpers.producer_helpers import send_inventory_message
from sqlmodel import create_engine, SQLModel, Session, select
from inventory_service import settings, models


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


def add_inventory_in_db(
        session: Annotated[Session, Depends(get_session)],
        create_inventory: models.Inventory,
):
    """ Function to add inventory in database """
    statement = select(models.Inventory).where(
        create_inventory.product_code == models.Inventory.product_code)
    existing_inventory = session.exec(statement).first()
    if existing_inventory is not None:
        raise HTTPException(
            status_code=400, detail="Product already exists! Try editing")
    session.add(create_inventory)
    session.commit()
    session.refresh(create_inventory)
    return create_inventory


async def edit_inventory_in_db(
        edit_inventory: models.OrderInventory,
):
    """ Function to edit inventory in database """
    try:
        with Session(engine) as session:
            statement = select(models.Inventory).where(
                edit_inventory.product_code == models.Inventory.product_code)
            existing_inv = session.exec(statement).first()
            if existing_inv is None:
                raise HTTPException(
                    status_code=404, detail="Product not found")
        if existing_inv.stock_in_orders is not None:
            existing_inv.stock_in_orders += edit_inventory.ordered_quantity
        with Session(engine) as session:
            session.add(existing_inv)
            session.commit()
            session.refresh(existing_inv)
        return existing_inv

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_invetory_of_single_product(
        product_code: str,
        session: Annotated[Session, Depends(get_session)]
) -> models.Inventory:
    """ Function to get inventory of single product """
    statement = select(models.Inventory).where(
        product_code == models.Inventory.product_code)
    result = session.exec(statement).first()
    if result is None:
        raise HTTPException(
            status_code=404, detail="Product Data not found, Add again")
    return result


async def get_orders_inv(
        order_id: str,
) -> list[models.OrderInventory]:
    """ Function to get inventory of single product """

    with Session(engine) as session:
        statement = select(models.OrderInventory).where(
            models.OrderInventory.order_id == order_id)
        result = session.exec(statement).all()
        if result is None:
            raise HTTPException(status_code=404, detail="No data found")
        inv_list = list(result)
        for item in inv_list:
            session.delete(item)
        session.commit()
        return inv_list


async def adjust_ordered_inventory_in_db(
        ordered_inv_list: list[models.OrderInventory]
):
    """ Function to ordered edit inventory in database """
    for product in ordered_inv_list:
        with Session(engine) as session:
            statement = select(models.Inventory).where(
                models.Inventory.product_code == product.product_code)
            existing_inv = session.exec(statement).first()
            if existing_inv is None:
                raise HTTPException(
                    status_code=404, detail="Product not found")
            if existing_inv.stock_in_orders is not None:
                existing_inv.stock_in_orders -= product.ordered_quantity
            session.add(existing_inv)
            session.commit()
            session.refresh(existing_inv)
            try:
                await send_inventory_message(existing_inv)
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                return HTTPException(status_code=500, detail=str(e))
