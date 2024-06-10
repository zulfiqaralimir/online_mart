""" Database functionality for Product Database Service """
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import create_engine, SQLModel, Session, select, desc, asc
from products import setting
from products.models import Product


connection_string: str = str(setting.DATABASE_URL).replace(
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

async def get_products (session: Annotated[Session, Depends(get_session)]):
    """ Function to get all products from database """
    products = session.exec(select(Product).order_by(asc(Product.product_id)))
    if products:
        return products.all()
    else:
        raise HTTPException(status_code=404, detail="No Product found")

async def get_single_product (session: Annotated[Session, Depends(get_session)], id: int | None = None):
    """ Function to get all products from database """
    if id:
        product = session.exec(select(Product).where(Product.product_id == id)).first()
        if product:
            return product
        else:
            raise HTTPException(status_code=404, detail = f"No Product found with id:{id}")
    else:
        product = session.exec(
            select(Product).order_by(desc(Product.product_id))
        ).first()
        if product:
            return product
        else:
            raise HTTPException (status_code=404, detail = "No Product found")