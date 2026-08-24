"""
Pydantic response model for baked goods.

Defines the structure returned by the API when retrieving baked good records.
This model ensures consistent serialization of baked good data across all
endpoints and supports ORM mode via `from_attributes=True`.
"""

from pydantic import BaseModel, ConfigDict


class BakedGoodResponseModel(BaseModel):
    """
    Represents the validated response structure for a baked good.

    Fields:
        id (int): Unique identifier of the baked good.
        active (bool): Whether the baked good is currently active.
        name (str): Name of the baked good.
        description (str): Description of the baked good.
        purchasing_cost (float): Cost to produce or purchase the baked good.
        retail_price (float): Price at which the baked good is sold.
        vendor_id (int): ID of the vendor associated with the baked good.
    """

    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: float
    retail_price: float
    vendor_id: int

<<<<<<< HEAD
    model_config = ConfigDict(from_attributes=True)
=======
    model_config = ConfigDict(from_attributes=True)
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
