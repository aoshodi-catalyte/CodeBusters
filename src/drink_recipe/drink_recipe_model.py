from pydantic import BaseModel, Field, field_validator
# from ingredient.ingredient_model import Ingredient
from constants.DRINK_TYPES import DrinkType

class DrinkRecipe(BaseModel):
    name: str
    description: str
    ingredients: list[str] = Field(default_factory=list)
    active: bool
    type: DrinkType
    production_cost: float
    markup_percentage: float
    sale_price: float

    @field_validator('type')
    def validate_drink_type(drink_type: str) -> DrinkType:
        try:
            return DrinkType(drink_type)
        except ValueError:
            raise ValueError(f"Invalid drink type: {drink_type}. Valid types are: {[dt.value for dt in DrinkType]}")
