import logging
import json
from fastapi import HTTPException
from inventory_service.kafka.producer.inventory_producer import get_kafka_producer
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from inventory_service.proto import order_pb2
from inventory_service import models
from inventory_service.db import adjust_ordered_inventory_in_db, edit_inventory_in_db, get_orders_inv, engine
from inventory_service.helpers.producer_helpers import send_inventory_message


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# helper for kafka order consumer
async def handle_order_message(order_message: order_pb2.OrderMessage):
    """ Function to handle order message """

    try:
        if order_message.message_type == order_pb2.MessageType.create_order:
            order_data = order_message.order_data
            await generate_order_inventory(order_data, "create")

        elif order_message.message_type == order_pb2.MessageType.edit_order:
            order_data = order_message.order_data
            await generate_order_inventory(order_data, "edit")

        elif order_message.message_type == order_pb2.MessageType.cancel_order:
            order_id = order_message.order_id
            await manage_order_inventory(order_id)

        elif order_message.message_type == order_pb2.MessageType.delete_order:
            order_id = order_message.order_id
            await manage_order_inventory(order_id)

        else:
            raise HTTPException(
                status_code=500, detail="Invalid order message type")
    except HTTPException as http_exc:
        raise http_exc
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
    except KeyError as e:
        logger.error(f"Missing key in order data: {e}")
    except ValueError as e:
        logger.error(f"Value error in order data: {e}")
    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {e}")


# helper functions for handle_order_message function
async def generate_order_inventory(
        order_data: order_pb2.Order,
        message_type: str
):

    if message_type == "edit":
        order_inv_list = await get_orders_inv(order_data.order_id)
        await adjust_ordered_inventory_in_db(order_inv_list)

    for item in order_data.order_items:
        order_item = models.OrderInventory(
            order_id=order_data.order_id,
            product_code=item.product_code,
            ordered_quantity=item.quantity,
        )

        # session to update in database
        with Session(engine) as session:
            session.add(order_item)
            session.commit()
            session.refresh(order_item)

        try:
            created_inventory = await edit_inventory_in_db(order_item)
            logger.info(f"created inventory: {created_inventory}")
            await send_inventory_message(created_inventory)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return HTTPException(status_code=500, detail=str(e))


async def manage_order_inventory(order_id: str):
    try:
        order_inv_list = await get_orders_inv(order_id)
        await adjust_ordered_inventory_in_db(order_inv_list)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
# end of file (EOF)
