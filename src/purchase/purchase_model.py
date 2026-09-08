from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseItemCreate(BaseModel):
    item_type: str = Field(min_length=1)  # "baked_good" or "drink_recipe"
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class PurchaseCreate(BaseModel):
    customer_id: int | None = None
    promo_id: int | None = None
    items: list[PurchaseItemCreate] = Field(min_length=1)


class PurchaseItemResponse(BaseModel):
    id: int
    item_type: str
    item_id: int
    quantity: int
    price_at_sale: Decimal

    model_config = ConfigDict(from_attributes=True)


class PurchaseResponse(BaseModel):
    id: int
    customer_id: int | None
    promo_id: int | None

    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total: Decimal

    loyalty_points_awarded: int
    created_at: datetime

    items: list[PurchaseItemResponse]

    model_config = ConfigDict(from_attributes=True)