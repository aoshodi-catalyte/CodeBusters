from decimal import Decimal
from pydantic import BaseModel
from src.constants.DRINK_TYPES import DrinkType

class IngredientRef(BaseModel):
    id: int
    name: str

class DrinkRecipeResponse(BaseModel):
    id: int
    name: str
    description: str
    active: bool
    type: DrinkType
    ingredients: list[IngredientRef]
    production_cost: Decimal
    markup_percentage: float
    sale_price: Decimal

    class Config:
        from_attributes = True

