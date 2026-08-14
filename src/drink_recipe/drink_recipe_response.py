"""
Response schemas for drink recipe API endpoints.

This module defines Pydantic models used for serializing drink recipe data
in API responses. These models shape the JSON responses returned to clients
and include all relevant recipe information and associated ingredient details.
"""

from pydantic import BaseModel
from src.constants.DRINK_TYPES import DrinkType


class IngredientRef(BaseModel):
    """
    Reference model for an ingredient in a drink recipe response.

    Provides minimal information about an ingredient as it appears in a
    drink recipe response. This lightweight model is used within the
    DrinkRecipeResponse to list ingredients without returning all
    ingredient details.

    Attributes:
        id: The unique identifier of the ingredient.
        name: The name of the ingredient.
    """

    id: int
    name: str
    quantity_used: float
    unit_of_measure_used: str


class DrinkRecipeResponse(BaseModel):
    """
    Response model for a drink recipe.

    This model is used to serialize drink recipe data for API responses.
    It includes all recipe information, pricing details, and a list of
    associated ingredients. The response includes the database ID and
    current active status of the recipe.

    Attributes:
        id: The unique identifier of the drink recipe in the database.
        name: The name of the drink recipe.
        description: A detailed description of the drink recipe.
        active: Boolean flag indicating if the recipe is currently in use.
        type: The type/category of drink (e.g., hot, cold, blended).
        ingredients: List of ingredient references used in this recipe.
        production_cost: The cost to produce this drink.
        markup_percentage: The percentage markup applied to the production cost.
        sale_price: The price at which the drink is sold to customers.
    """

    id: int
    name: str
    description: str
    active: bool
    type: DrinkType
    ingredients: list[IngredientRef]
    production_cost: float 
    markup_percentage: float 
    sale_price: float
