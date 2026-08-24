"""
Pydantic model for drink recipe data validation and serialization.

This module defines the data structures for drink recipes, including validation
rules for pricing and drink types. It handles conversion of drink type values
from various formats (string, int) to the DrinkType enum.
"""

from pydantic import BaseModel, Field, field_validator
from constants.drink_types import DrinkType
from utils.validators import round_float


class RecipeIngredient(BaseModel):
    """
    Represents a single ingredient used within a drink recipe.

    This model describes how much of a specific ingredient is used and in
    what unit of measurement. It does not define the ingredient itself—
    only its usage within the context of a recipe.

    Fields:
        id (int):
            The database ID of the ingredient being referenced. This must
            correspond to an existing Ingredient record.

        quantity_used (float):
            The amount of the ingredient used in the recipe. Must be greater
            than zero. This value is later converted into the ingredient's
            purchase unit for cost calculation.

        unit_of_measure_used (str):
            The unit describing how the recipe measures this ingredient
            (e.g., "oz", "g", "tsp"). Must be a non‑empty string between
            1 and 50 characters. This unit is used during cost conversion
            and must exist in the unit conversion table.
    """

    id: int
    quantity_used: float = Field(gt=0)
    unit_of_measure_used: str = Field(min_length=1, max_length=50)


class DrinkRecipe(BaseModel):
    """
    Represents a drink recipe submitted through the API.

    This model defines the core data required to create a drink recipe,
    including its descriptive information, ingredient usage, activity status,
    drink category, and markup percentage. It is used for request validation
    and passed into the repository layer where production cost and sale price
    are calculated.

    Fields:
        name (str):
            The name of the drink recipe. Must be a non-empty string.

        description (str):
            A human-readable description of the drink, such as flavor notes
            or preparation details.

        ingredients (list[RecipeIngredient]):
            A list of ingredient usage entries describing which ingredients
            are used and in what quantities. Defaults to an empty list.

        active (bool):
            Indicates whether the recipe is currently available or in use.

        type (str):
            The drink category (e.g., "coffee", "tea", "latte"). Must match
            a valid DrinkType enum value.

        markup_percentage (float):
            The percentage markup applied to the production cost when
            calculating the final sale price. Must be non-negative.
    """

    name: str = Field(min_length=1, description="The name of the drink recipe")
    description: str = Field(
        min_length=1, description="A detailed description of the drink"
    )
    ingredients: list[RecipeIngredient] = Field(
        default_factory=list, description="List of ingredients used in this recipe"
    )
    active: bool = Field(
        ..., description="Whether this recipe is currently active/in use"
    )
    type: DrinkType = Field(..., description="The type/category of the drink")
    markup_percentage: float = Field(ge=0)

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
        except ValueError as exc:
            raise ValueError(
                f"Invalid drink type: {value}. "
                f"Valid types are: {[dt.value for dt in DrinkType]}"
            ) from exc

    @field_validator("name", "description")
    @classmethod
    def validate_not_blank(cls, value):
        """Ensure name and description are not blank or whitespace."""
        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")

        return value

    @field_validator("markup_percentage")
    def round_values(cls, v):
        """Round markup percentage using shared rounding utility."""
        return round_float(v)