"""
Pydantic models for purchase creation and response.

Defines the request and response schemas used by the purchase API.
These models validate incoming purchase payloads, structure outgoing
purchase data, and support ORM mode via `from_attributes=True`.
"""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_serializer

class DecimalSerializerModel(BaseModel):
    """
    Base model providing shared Decimal-to-float serialization for monetary fields.

    Any subclass can declare Decimal fields and they will automatically be
    serialized as floats in JSON responses.
    """

    @field_serializer("*")
    def serialize_decimal_fields(self, value):
        """
        Convert Decimal values into floats for JSON serialization.

        Args:
            value (Any): A field value that may be a Decimal.

        Returns:
            Any: A float if the value is a Decimal, otherwise the original value.
        """
        if isinstance(value, Decimal):
            return float(value)
        return value


class PurchaseItemCreate(BaseModel):
    """
    Represents a single item included in a purchase request.

    Fields:
        item_type (str): The type of item ("baked_good" or "drink_recipe").
        item_id (int): The ID of the item being purchased.
        quantity (int): The quantity of the item being purchased.
    """
    item_type: str = Field(min_length=1)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class PurchaseCreate(BaseModel):
    """
    Represents the payload for creating a new purchase.

    Fields:
        customer_id (int | None): Optional customer ID for loyalty tracking.
        promo_id (int | None): Optional promotion ID to apply discounts.
        items (list[PurchaseItemCreate]): List of items included in the purchase.
    """
    customer_id: int | None = None
    promo_id: int | None = None
    items: list[PurchaseItemCreate] = Field(min_length=1)


class PurchaseItemResponse(DecimalSerializerModel):
    """
    Represents a single item returned in a purchase response.

    Fields:
        id (int): Unique identifier of the purchase item record.
        item_type (str): The type of item purchased.
        item_id (int): The ID of the purchased item.
        quantity (int): Quantity purchased.
        price_at_sale (Decimal): Price of the item at the time of sale.
    """
    id: int
    item_type: str
    item_id: int
    quantity: int
    price_at_sale: Decimal


class PurchaseResponse(DecimalSerializerModel):
    """
    Represents the full purchase returned by the API.

    Fields:
        id (int): Unique purchase identifier.
        customer_id (int | None): Customer associated with the purchase.
        promo_id (int | None): Promotion applied to the purchase.
        subtotal (Decimal): Total before discounts and tax.
        discount_amount (Decimal): Discount applied from promotion.
        tax_amount (Decimal): Calculated tax amount.
        total (Decimal): Final total after tax and discounts.
        loyalty_points_awarded (int): Loyalty points earned.
        created_at (datetime): Timestamp of purchase creation.
        items (list[PurchaseItemResponse]): Line items included in the purchase.
    """
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
