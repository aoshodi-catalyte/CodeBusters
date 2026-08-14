"""
Association table for the many-to-many relationship between drink recipes and ingredients.

This module defines the join table that connects drink recipes to their ingredients,
allowing a single recipe to contain multiple ingredients and a single ingredient to be
used in multiple recipes.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from database import Base
from ingredient.ingredient_schema import IngredientSchema

class DrinkRecipeIngredientSchema(Base):
    __tablename__ = "drink_recipe_ingredient"

    id = Column(Integer, primary_key=True, index=True)

    drink_recipe_id = Column(Integer, ForeignKey("drink_recipe.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredient.id"), nullable=False)

    # NEW: recipe-specific usage fields
    quantity_used = Column(Numeric(10, 2), nullable=False)
    unit_of_measure_used = Column(String(50), nullable=False)

    drink_recipe = relationship("DrinkRecipeSchema", back_populates="recipe_ingredients")
    ingredient = relationship(IngredientSchema, back_populates="ingredient_recipes")
