"""
Pydantic response model for promotion data.

This module defines the PromotionResponseModel used to validate and
serialize promotion data returned by the API.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class PromotionResponseModel(BaseModel):
    """
    Represents the promotion data returned by the API.

    Attributes:
        id: The unique, automatically generated identifier for the promotion.
        active: Indicates whether the promotion is currently active.
        promo_code: The unique promotional code.
        discount_percentage: The percentage discount applied by the promotion.
        start_datetime: The date and time when the promotion begins.
        end_datetime: The date and time when the promotion ends.

    Config:
        from_attributes: Allows the response model to be created from
            attributes of a SQLAlchemy model instance.
    """

    id: int
    active: bool
    promo_code: str
    discount_percentage: float
    start_datetime: datetime
    end_datetime: datetime

    model_config = ConfigDict(from_attributes=True)