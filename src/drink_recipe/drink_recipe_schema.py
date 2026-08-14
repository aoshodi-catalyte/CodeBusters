"""
SQLAlchemy ORM model for drink recipes.

This module defines the database schema for drink recipes, including their
pricing information, type, and associated ingredients. Drink recipes are
linked to drink types via a foreign key relationship and to ingredients
through a many-to-many association table.
"""
from drink_recipe.drink_ingredients_schema import DrinkRecipeIngredientSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DrinkRecipeSchema(Base):
    """
    SQLAlchemy ORM model representing a drink recipe in the database.

    This model stores comprehensive information about drink recipes, including
    their basic details (name, description), pricing information (production cost,
    markup percentage, sale price), active status, and relationships to drink types
    and ingredients.

    The model uses a many-to-many relationship with ingredients through the
    drink_recipe_ingredient association table, allowing recipes to contain
    multiple ingredients and ingredients to be used in multiple recipes.

    Attributes:
        id: The unique identifier for the drink recipe (primary key).
        name: The name of the drink recipe (required, non-null).
        description: A detailed description of the drink recipe (required, non-null).
        active: Boolean flag indicating whether the recipe is currently in use (defaults to True).
        production_cost: The cost to produce one serving of this drink (required, non-null).
        type_id: Foreign key reference to the drink_type table (required, non-null).
        markup_percentage: The percentage markup applied to the production cost (defaults to 0.0).
        sale_price: The price at which the drink is sold to customers (defaults to 0.0).
        drink_type: Relationship to the DrinkTypeSchema model representing the drink's type/category.
        ingredients: Many-to-many relationship to IngredientSchema models via the
            drink_recipe_ingredient association table.
    """

    __tablename__ = "drink_recipe"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    production_cost = Column(Float)
    type_id = Column(
        Integer,
        ForeignKey("drink_type.id"),
        nullable=False
    )
    markup_percentage = Column(Float, default=0.0)
    sale_price = Column(Float, default=0.0)

    drink_type = relationship(DrinkTypeSchema, back_populates="drink_recipes")
    # Many-to-many relationship with ingredients through association table
    recipe_ingredients = relationship(
        DrinkRecipeIngredientSchema,
        back_populates="drink_recipe",
        cascade="all, delete-orphan"
    )