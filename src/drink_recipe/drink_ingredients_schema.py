"""
Association table for the many-to-many relationship between drink recipes and ingredients.

This module defines the join table that connects drink recipes to their ingredients,
allowing a single recipe to contain multiple ingredients and a single ingredient to be
used in multiple recipes.
"""

from sqlalchemy import Column, ForeignKey, Table
from database import Base

drink_recipe_ingredient = Table(
    "drink_recipe_ingredient",
    Base.metadata,
    Column(
        "drink_recipe_id",
        ForeignKey("drink_recipe.id"),
        primary_key=True,
    ),
    Column(
        "ingredient_id",
        ForeignKey("ingredient.id"),
        primary_key=True,
    )
)
