from decimal import Decimal

from pydantic import BaseModel, Field, condecimal, field_validator
from src.constants.DRINK_TYPES import DrinkType

class DrinkRecipe(BaseModel):
    name: str
    description: str
    ingredients: list[int]
    active: bool
    type: DrinkType
    production_cost: Decimal = condecimal(ge=0, decimal_places=2)
    markup_percentage: float = Field(ge=0)
    sale_price: Decimal = condecimal(ge=0, decimal_places=2)

    @field_validator('type')
    def validate_drink_type(drink_type: str) -> DrinkType:
        try:
            return DrinkType(drink_type)
        except ValueError:
            raise ValueError(f"Invalid drink type: {drink_type}. Valid types are: {[dt.value for dt in DrinkType]}")
