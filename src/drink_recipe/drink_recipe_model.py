from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, condecimal
from constants.DRINK_TYPES import DrinkType

ConstrainedMoney = condecimal(ge=0, decimal_places=2)

class DrinkRecipe(BaseModel):
    name: str
    description: str
    ingredients: list[int] = Field(default_factory=list)
    active: bool
    type: DrinkType
    production_cost: ConstrainedMoney
    markup_percentage: float = Field(ge=0)
    sale_price: ConstrainedMoney

    @field_validator('type', mode='before')
    def validate_drink_type(cls, value):
        try:
            return DrinkType(value)  # Convert string to DrinkType enum
        except ValueError:
            raise ValueError(
                f"Invalid drink type: {value}. "
                f"Valid types are: {[dt.value for dt in DrinkType]}"
            )
