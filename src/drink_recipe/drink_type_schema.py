"""
SQLAlchemy ORM schema for drink types.

This module defines the database representation of drink categories used to
classify drink recipes. Drink types provide a reusable way to group recipes
(e.g., "coffee", "tea", "soda") and are referenced by drink recipes through
a one‑to‑many relationship. Each recipe must belong to exactly one drink type,
ensuring consistent categorization across the system.
"""


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class DrinkTypeSchema(Base):
    """
    SQLAlchemy ORM model representing a drink type or category.

    Drink types define the classification for drink recipes, such as
    "coffee", "tea", "cold brew", or "blended". Each drink recipe must be
    associated with exactly one drink type, forming a one‑to‑many
    relationship where a single type can be shared across multiple recipes.

    Fields:
        id (int):
            Primary key identifying the drink type.

        name (str):
            The unique name of the drink type. Must be non‑null and unique
            to prevent duplicate categories.

    Relationships:
        drink_recipes:
            A collection of DrinkRecipeSchema records that reference this
            drink type. Represents the one‑to‑many relationship between
            drink types and drink recipes.
    """

    __tablename__ = "drink_type"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    name = Column(
        String,
        unique=True,
        nullable=False
    )

    # One-to-many back reference to drink recipes using this type
    drink_recipes = relationship("DrinkRecipeSchema", back_populates="drink_type")
