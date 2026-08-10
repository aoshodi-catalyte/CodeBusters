from pydantic import BaseModel

class BakedGoodModel(BaseModel):
    id: int
    active: bool
    name: str
    description: str
    purchasing_cost: float
    retail_price: float