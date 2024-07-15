""" Models for Inventory Service"""
from sqlmodel import SQLModel, Field
from typing import Optional


class InventoryUpdate(SQLModel):
    product_code: str
    total_stock: int
    damaged: int


class Inventory(SQLModel, table=True):
    inv_id: int | None = Field(default=None, primary_key=True)
    product_code: str = Field(index=True)
    total_stock: int
    stock_in_orders: int | None = Field(default=0)
    damaged: int | None = Field(default=0)
    delivered: int | None = Field(default=0)
    returned: int | None = Field(default=0)

    def calculate_stock_available(self) -> int:
        return (
            (self.total_stock or 0)
            + (self.returned or 0)
            - (self.damaged or 0)
            - (self.delivered or 0)
            - (self.stock_in_orders or 0)
        )


class OrderInventory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str
    product_code: str
    ordered_quantity: int
