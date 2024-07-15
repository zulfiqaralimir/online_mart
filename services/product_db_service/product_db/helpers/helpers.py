import logging
import json
from fastapi import HTTPException
from sqlmodel import Session, select
from product_db import db
from product_db.proto import product_pb2
from product_db import models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_product_message(product_message: product_pb2.ProductMessage):
    """ Handle product message by adding or editing product """
    try:
        if product_message.message_type == product_pb2.MessageType.add_product:
            product_data = product_message.product_data
            product = models.Product(
                product_title=product_data.product_title,
                product_description=product_data.product_description,
                price=product_data.price,
                currency=product_data.currency,
                category=product_data.category,
                brand=product_data.brand,
                product_code=product_data.product_code
            )
            await add_product_to_db(product)

        elif product_message.message_type == product_pb2.MessageType.edit_product:
            product_data = product_message.product_data
            await edit_product_in_db(product_data)

        elif product_message.message_type == product_pb2.MessageType.delete_product:
            product_id = product_message.product_id
            await delete_product_in_db(product_id)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON message: {e}")
    except KeyError as e:
        print(f"Missing expected key in message: {e}")


async def add_product_to_db(product: models.Product):
    """ Add new product to the database """
    with Session(db.engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)


async def edit_product_in_db(edit_product_data: product_pb2.Product):
    """ Edit existing product in the database """
    with Session(db.engine) as session:
        existing_product = session.exec(
            select(models.Product).where(
                models.Product.product_id == edit_product_data.product_id
            )).first()

        if existing_product:
            existing_product.product_title = edit_product_data.product_title
            existing_product.product_description = edit_product_data.product_description
            existing_product.price = edit_product_data.price
            existing_product.currency = edit_product_data.currency
            existing_product.category = edit_product_data.category
            existing_product.brand = edit_product_data.brand
            existing_product.product_code = edit_product_data.product_code

            session.add(existing_product)
            session.commit()
            session.refresh(existing_product)


async def delete_product_in_db(product_id: int):
    """ Delete existing product in the database """
    with Session(db.engine) as session:
        session.delete(session.get(models.Product, product_id))
        session.commit()


async def handle_inventory_message(inventory_message):
    with Session(db.engine) as session:
        existing_product = session.exec(
            select(models.Product).where(
                models.Product.product_code == inventory_message.product_code
            )).first()
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")

        existing_product.stock = inventory_message.stock_available
        session.add(existing_product)
        session.commit()
        session.refresh(existing_product)
# end-of-file(EOF)
