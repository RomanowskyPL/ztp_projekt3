from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel
from datetime import datetime


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    line_total: Decimal


class CartResponse(BaseModel):
    id: int
    operator_id: int
    items: list[CartItemResponse]
    total_price: Decimal


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    line_total: Decimal


class OrderResponse(BaseModel):
    id: int
    operator_id: int
    order_number: str
    status: str
    total_price: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


class OrderListItemResponse(BaseModel):
    id: int
    order_number: str
    status: str
    total_price: Decimal
    created_at: datetime

class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    name: str | None = None
    price: float | None = None

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    operator_id: int
    created_at: datetime
    updated_at: datetime
    items: list[CartItemResponse]

    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int


class CheckoutResponse(BaseModel):
    order_id: int
    order_number: str
    total_price: float