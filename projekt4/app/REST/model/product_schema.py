from pydantic import BaseModel
from datetime import datetime
from typing import Any

class Category(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class Product(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    category: Category

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    category_id: int

class ProductHistoryEntry(BaseModel):
    id: int
    product_id: int
    action: str
    previous_state: dict[str, Any]
    current_state: dict[str, Any]
    changed_at: datetime

    class Config:
        from_attributes = True