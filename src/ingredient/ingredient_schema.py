from dataclasses import dataclass
from decimal import Decimal
from sqlalchemy import Boolean, Column, Integer, Numeric, String
from enum import Enum
from constants.INGREDIENT_TYPES import UnitOfMeasure
from app.database import Base


# ==========================================
# SQLALCHEMY MODEL
# ==========================================


  # ASSOCIATION TABLE
ingredient_allergens = Table(
    "ingredient_allergens",
    Base.metadata,
    Column("ingredient_id", ForeignKey("ingredients.id"), primary_key=True),
    Column("allergen_id", ForeignKey("allergens.id"), primary_key=True),
)

class Allergens(Base):
    __tablename__ = "allergens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String(255), nullable=False)
    purchasing_cost = Column(Numeric(10, 2), nullable=False)
    unit_amount = Column(Numeric(10, 2), nullable=False)
    unit_of_measure: UnitOfMeasure
    allergens = relationship("Allergens", secondary=ingredient_allergens,)
