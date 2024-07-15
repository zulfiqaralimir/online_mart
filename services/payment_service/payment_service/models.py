from sqlmodel import SQLModel, Field


class Orders(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str
    user_id: int
    order_value: float
    currency: str


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    user_id: int = Field(unique=True)
    email: str = Field(unique=True)
    phone: str
    shipping_address: str
    payment_token: str


class Payments(SQLModel, table=True):
    payment_id: int | None = Field(default=None, primary_key=True)
    order_id: str
    user_id: int
    amount: float
    currency: str
    payment_status: str


class PaymentRequest(SQLModel):
    amount: float
    currency: str
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str
    order_id: str
    user_id: int


class PaymentResponse(SQLModel):
    payment_status: str
    message: str
# end-of-file(EOF)
