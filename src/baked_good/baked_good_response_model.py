from pydantic import BaseModel, ConfigDict

class BakedGoodResponseModel(BaseModel):
    """
    Defines the data returned when retrieving a baked good.

    Args:
        id: The unique identifier of the baked good.
        active: Indicates whether the baked good is currently active.
        name: The name of the baked good.
        description: A description of the baked good.
        purchasing_cost: The cost to purchase or produce the baked good.
        retail_price: The price at which the baked good is sold.
        vendor_id: The ID of the vendor associated with the baked good.

    Returns:
        A validated BakedGoodResponseModel object.
    """

    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: float
    retail_price: float
    vendor_id: int

    model_config = ConfigDict(from_attributes=True)