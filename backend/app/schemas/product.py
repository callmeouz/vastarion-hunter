from pydantic import BaseModel
from datetime import datetime


class ProductCreate(BaseModel):
    url: str
    name: str
    target_price: float | None = None


class ProductResponse(BaseModel):
    id: int
    url: str
    name: str
    current_price: float | None
    target_price: float | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    checked_at: datetime

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True