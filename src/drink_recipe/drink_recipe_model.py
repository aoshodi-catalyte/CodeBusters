"""
Pydantic model for drink recipe data validation and serialization.

This module defines the data structures for drink recipes, including validation
rules for pricing and drink types. It handles conversion of drink type values
from various formats (string, int) to the DrinkType enum.
"""

from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, condecimal
from constants.DRINK_TYPES import DrinkType

# Type constraint: monetary values must be non-negative with 2 decimal places
ConstrainedMoney = condecimal(ge=0, decimal_places=2)


class DrinkRecipe(BaseModel):
    """
    Data model for a drink recipe.

    This model represents a drink recipe with its basic information, ingredients,
    pricing details, and type. It includes validation for drink types and price
    constraints.

    Attributes:
        name: The name of the drink recipe (non-empty string).
        description: A detailed description of the drink recipe.
        ingredients: List of ingredient IDs that compose this recipe. Defaults to empty list.
        active: Boolean flag indicating if the recipe is currently in use.
        type: The type/category of drink (e.g., hot, cold, blended).
        production_cost: The cost to produce this drink. Must be non-negative with 2 decimal places.
        markup_percentage: The percentage markup applied to the production cost. Must be non-negative.
        sale_price: The price at which the drink is sold. Must be non-negative with 2 decimal places.
    """

    name: str = Field(..., description="The name of the drink recipe")
    description: str = Field(..., description="A detailed description of the drink")
    ingredients: list[int] = Field(
        default_factory=list,
        description="List of ingredient IDs used in this recipe"
    )
    active: bool = Field(..., description="Whether this recipe is currently active/in use")
    type: DrinkType = Field(..., description="The type/category of the drink")
    production_cost: ConstrainedMoney
    markup_percentage: float = Field(ge=0)
    sale_price: ConstrainedMoney

    @field_validator("type", mode="before")
    def validate_drink_type(cls, value):
        """
        Validate and convert drink type values to DrinkType enum.

        Accepts string or integer values and converts them to the appropriate
        DrinkType enum member. Raises ValueError if the value is not a valid
        drink type.

        Args:
            value: The drink type value to validate (string or int).

        Returns:
            The converted DrinkType enum member.

        Raises:
            ValueError: If the value is not a valid drink type.
        """
        try:
            return DrinkType(value)  # Convert string/int to DrinkType enum
        except ValueError:
            raise ValueError(
                f"Invalid drink type: {value}. "
                f"Valid types are: {[dt.value for dt in DrinkType]}"
            )
