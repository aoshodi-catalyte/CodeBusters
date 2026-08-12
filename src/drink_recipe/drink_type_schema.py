"""
SQLAlchemy ORM model for drink types.

This module defines the database schema for drink types/categories, representing
the different categories or types of drinks available (e.g., hot drinks, cold drinks,
blended drinks). Drink types are used to categorize drink recipes and are linked
to recipes through a one-to-many relationship.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class DrinkTypeSchema(Base):
    """
    SQLAlchemy ORM model representing a drink type/category in the database.

    This model stores information about different drink type categories, such as
    "hot", "cold", "blended", etc. Each drink recipe must be associated with
    exactly one drink type. Drink types are reusable across multiple recipes,
    creating a one-to-many relationship.

    Attributes:
        id: The unique identifier for the drink type (primary key).
        name: The name/label of the drink type, must be unique (required, non-null, unique).
        drink_recipes: One-to-many relationship to DrinkRecipeSchema models that use this type.
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
