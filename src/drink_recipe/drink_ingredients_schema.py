from sqlalchemy import Column, ForeignKey, Table
from src.database import Base

drink_recipe_ingredient = Table(
    "drink_recipe_ingredient",
    Base.metadata,
    Column("drink_recipe_id", ForeignKey("drink_recipe.id"), primary_key=True),
    Column("ingredient_id", ForeignKey("ingredient.id"), primary_key=True)
)
