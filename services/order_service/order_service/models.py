''' Models for Order Service '''
from enum import Enum
import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, func, Relationship
from sqlalchemy import DateTime
from sqlalchemy.types import Enum as SQLAlchemyEnum
from pydantic import BaseModel
from typing import List, Optional


def generate_order_id() -> str:
    return str(uuid.uuid4())


def get_current_time():
    ''' function to get current time '''
    return datetime.now(timezone.utc)


class PaymentStatusEnum(str, Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


payment_status_proto_to_sqlmodel = {
    0: PaymentStatusEnum.pending,
    1: PaymentStatusEnum.success,
    2: PaymentStatusEnum.failed
}


class OrderStatusEnum(str, Enum):
    created = 'created'
    in_progress = 'in_progress'
    shipped = 'shipped'
    completed = 'completed'
    cancelled = 'cancelled'
    disputed = 'disputed'


order_status_proto_to_sqlmodel = {
    0: OrderStatusEnum.created,
    1: OrderStatusEnum.in_progress,
    2: OrderStatusEnum.shipped,
    3: OrderStatusEnum.completed,
    4: OrderStatusEnum.cancelled,
    5: OrderStatusEnum.disputed,
}


class ShippingStatusEnum(str, Enum):
    processing = 'processing'
    in_transit = 'in transit'
    delivered = 'delivered'
    returned = 'returned'


shipping_status_proto_to_sqlmodel = {
    0: ShippingStatusEnum.processing,
    1: ShippingStatusEnum.in_transit,
    2: ShippingStatusEnum.delivered,
    3: ShippingStatusEnum.returned,
}


class Orders(SQLModel, table=True):
    order_id: str = Field(primary_key=True)
    user_id: int = Field()
    order_date: datetime = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=True), default=func.now())
    )
    order_value: float = Field()
    currency: str = Field()
    order_status: OrderStatusEnum = Field(default=OrderStatusEnum.created)
    payment_status: PaymentStatusEnum = Field(
        default=PaymentStatusEnum.pending)
    shipping_status: ShippingStatusEnum = Field(
        default=ShippingStatusEnum.processing)

    order_items: list["OrderItems"] = Relationship(
        back_populates="orders",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class OrderItems(SQLModel, table=True):
    order_item_id: int | None = Field(default=None, primary_key=True)
    order_id: str | None = Field(default=None, foreign_key="orders.order_id")
    product_code: str
    product_name: str
    product_description: str | None = None
    quantity: int
    unit_price: float
    total_price: float

    orders: Orders = Relationship(back_populates="order_items")


# pydantic models for API request and response
class OrderItemBase(BaseModel):
    product_code: str
    product_name: str
    product_description: str | None = None
    quantity: int
    unit_price: float
    total_price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    order_item_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    order_value: float
    order_date: datetime | None
    currency: str


class OrderCreate(OrderBase):
    order_items: list[OrderItemCreate]


class OrderMessage(OrderCreate):
    order_id: str


class OrderResponse(BaseModel):
    order_id: str
    user_id: int
    order_value: float
    order_date: datetime
    currency: str
    order_status: str | None
    payment_status: str | None
    shipping_status: str | None
    order_items: list[OrderItemRead]

    class Config:
        from_attributes = True
