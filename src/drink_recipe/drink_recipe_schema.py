"""
SQLAlchemy ORM schema for drink recipes.

This module defines the database representation of drink recipes, including
their descriptive fields, pricing information, active status, and relational
links to drink types and ingredient usage. Drink recipes participate in a
many‑to‑many relationship with ingredients through the
drink_recipe_ingredient association table, allowing each recipe to contain
multiple ingredients and each ingredient to appear in multiple recipes.

The schema is used by the repository layer to persist recipe data, compute
production cost and sale price, and manage ingredient associations.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from drink_recipe.drink_type_schema import DrinkTypeSchema
from database import Base


class DrinkRecipeSchema(Base):
    """
    SQLAlchemy ORM model representing a drink recipe stored in the database.

    This model captures all persistent fields associated with a drink recipe,
    including its name, description, active status, pricing details, and
    relationships to drink types and ingredient usage entries. It serves as
    the authoritative database structure used by the repository layer when
    creating, retrieving, and updating drink recipes.

    Fields:
        id (int):
            Primary key identifying the drink recipe.

        name (str):
            The unique name of the drink recipe. Must be non‑null.

        description (str):
            A human‑readable description of the drink. Must be non‑null.

        active (bool):
            Indicates whether the recipe is currently available or in use.

        production_cost (float):
            The calculated cost required to produce one serving of the drink.
            Assigned by the repository during recipe creation.

        type_id (int):
            Foreign key referencing the drink_type table. Defines the drink's
            category (e.g., coffee, tea, latte).

        markup_percentage (float):
            The percentage markup applied to the production cost when
            determining the final sale price.

        sale_price (float):
            The final price of the drink after markup is applied.

    Relationships:
        drink_type:
            SQLAlchemy relationship to DrinkTypeSchema, representing the
            drink's category.

        recipe_ingredients:
            A collection of DrinkRecipeIngredientSchema entries describing
            the specific ingredients used in the recipe, including quantity
            and measurement unit. This forms the many‑to‑many relationship
            between recipes and ingredients.
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
        "DrinkRecipeIngredientSchema",
        back_populates="drink_recipe",
        cascade="all, delete-orphan"
    )
