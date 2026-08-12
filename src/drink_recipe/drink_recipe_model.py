from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, condecimal
from constants.DRINK_TYPES import DrinkType

ConstrainedMoney = condecimal(ge=0, decimal_places=2, strict=True)

class DrinkRecipe(BaseModel):
    name: str
    description: str
    ingredients: list[int] = Field(default_factory=list)
    active: bool
    type: DrinkType
    production_cost: ConstrainedMoney
    markup_percentage: float = Field(ge=0)
    sale_price: ConstrainedMoney

    @field_validator('type')
    def validate_drink_type(cls, drink_type):
        try:
            return DrinkType(drink_type)
        except ValueError:
            raise ValueError(
                f"Invalid drink type: {drink_type}. "
                f"Valid types are: {[dt.value for dt in DrinkType]}"
            )
