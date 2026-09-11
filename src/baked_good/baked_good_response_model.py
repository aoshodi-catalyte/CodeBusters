"""
Pydantic response model for baked goods.

Defines the structure returned by the API when retrieving baked good records.
This model ensures consistent serialization of baked good data across all
endpoints and supports ORM mode via `from_attributes=True`.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BakedGoodResponseModel(BaseModel):
    """
    Represents the validated response structure for a baked good.

    Fields:
        id (int): Unique identifier of the baked good.
        active (bool): Whether the baked good is currently active.
        name (str): Name of the baked good.
        description (str): Description of the baked good.
        purchasing_cost (Decimal): Cost to produce or purchase the baked good.
        retail_price (Decimal): Price at which the baked good is sold.
        vendor_id (int): ID of the vendor associated with the baked good.
    """

    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: Decimal = Field(decimal_places=2)
    retail_price: Decimal = Field(decimal_places=2)
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)
    