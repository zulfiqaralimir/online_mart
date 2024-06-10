""" Models for Database Service"""
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    """ Product Model """
    product_id: int | None = Field(default=None, primary_key=True)
    product_title: str = Field(index=True, min_length=3, max_length=25)
    product_description: str = Field()
    price: float = Field()
    currency: str = Field()
    stock: int = Field()
    category: str = Field()
    brand: str = Field()


class Test(SQLModel, table=True):
    title: str = Field(primary_key=True)