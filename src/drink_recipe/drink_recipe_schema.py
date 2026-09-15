"""
SQLAlchemy ORM schema for drink recipes.

This module defines the database representation of drink recipes, including
their descriptive fields, pricing information, active status, and relational
links to drink types and ingredient usage. Drink recipes participate in a
many-to-many relationship with ingredients through the
drink_recipe_ingredient association table.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from database import Base


class DrinkRecipeSchema(Base):
    """
    SQLAlchemy ORM model representing a drink recipe stored in the database.

    This model captures all persistent fields associated with a drink recipe,
    including its name, description, active status, pricing details, and
    relationships to drink types and ingredient usage entries.

    Fields:
        id (int):
            Primary key identifying the drink recipe.

        name (str):
            The unique name of the drink recipe.

        description (str):
            A human-readable description of the drink.

        active (bool):
            Indicates whether the recipe is currently available or in use.

        production_cost (Decimal):
            The calculated cost required to produce one serving of the drink.

        type_id (int):
            Foreign key referencing the drink_type table.

        markup_percentage (float):
            The percentage markup applied to the production cost.

        sale_price (Decimal):
            The final price of the drink after markup is applied.

    Relationships:
        drink_type:
            SQLAlchemy relationship to DrinkTypeSchema.

        recipe_ingredients:
            Collection of DrinkRecipeIngredientSchema entries describing
            the ingredients used in the recipe.
    """

    __tablename__ = "drink_recipe"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    # Monetary values use fixed-point decimal precision.
    production_cost = Column(Numeric(10, 2))
    sale_price = Column(Numeric(10, 2), default=0.00)

    type_id = Column(Integer, ForeignKey("drink_type.id"), nullable=False)
    markup_percentage = Column(Numeric(5, 2), default=0.00)

    drink_type = relationship("DrinkTypeSchema", back_populates="drink_recipes")

    recipe_ingredients = relationship(
        "DrinkRecipeIngredientSchema",
        back_populates="drink_recipe",
        cascade="all, delete-orphan",
    )
