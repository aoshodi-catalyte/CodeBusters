"""
Response schemas for drink recipe API endpoints.

This module defines Pydantic models used for serializing drink recipe data
in API responses. These models shape the JSON responses returned to clients
and include all relevant recipe information and associated ingredient details.
"""

from decimal import Decimal

from pydantic import BaseModel, Field

from constants.drink_types import DrinkType


class IngredientRef(BaseModel):
    """
    Lightweight representation of an ingredient as it appears in a drink
    recipe API response.

    This model provides recipe-specific ingredient usage details without
    exposing the full ingredient record. It is used inside
    DrinkRecipeResponse to show which ingredients a recipe uses and in
    what quantities.

    Fields:
        id (int):
            The unique identifier of the ingredient.

        name (str):
            The human-readable name of the ingredient.

        quantity_used (float):
            The amount of the ingredient used in the recipe, expressed in
            the recipe's measurement unit.

        unit_of_measure_used (str):
            The unit describing how the recipe measures this ingredient
            (e.g., "oz", "g", "ml"). This may differ from the ingredient's
            purchase unit and is used during cost conversion.
    """

    id: int
    name: str
    quantity_used: float
    unit_of_measure_used: str


class DrinkRecipeResponse(BaseModel):
    """
    Serialized API response model for a drink recipe.

    This model defines the structure of drink recipe data returned to
    clients. It includes descriptive information, ingredient usage,
    pricing details, and drink classification.

    Fields:
        id (int):
            The unique identifier of the drink recipe in the database.

        name (str):
            The name of the drink recipe.

        description (str):
            A human-readable description of the drink.

        active (bool):
            Indicates whether the recipe is currently available or in use.

        type (DrinkType):
            The drink category.

        ingredients (list[IngredientRef]):
            A list of ingredient usage entries.

        production_cost (Decimal):
            The calculated cost required to produce the drink, represented
            with exactly two decimal places.

        markup_percentage (float):
            The percentage markup applied to the production cost.

        sale_price (Decimal):
            The final price of the drink after markup is applied, represented
            with exactly two decimal places.
    """

    id: int
    name: str
    description: str
    active: bool
    type: DrinkType
    ingredients: list[IngredientRef]

    production_cost: Decimal = Field(decimal_places=2)
    markup_percentage: float
    sale_price: Decimal = Field(decimal_places=2)
    