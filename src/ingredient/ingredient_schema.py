from sqlalchemy import Boolean, Column, Integer, Numeric, String
from constants.INGREDIENT_TYPES import UnitOfMeasure
from database import Base
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy import Enum

# ==========================================
# SQLALCHEMY MODEL
# ==========================================


  # ASSOCIATION TABLE
ingredient_allergens = Table(
    "ingredient_allergen",
    Base.metadata,
    Column("ingredient_id", ForeignKey("ingredients.id"), primary_key=True),
    Column("allergen_id", ForeignKey("allergens.id"), primary_key=True),
)

class AllergenSchema(Base):
    __tablename__ = "allergen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

class IngredientSchema(Base):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String(255), nullable=False)
    purchasing_cost = Column(Numeric(10, 2), nullable=False)
    unit_amount = Column(Numeric(10, 2), nullable=False)
    unit_of_measure = Column(Enum(UnitOfMeasure), nullable=False)
    allergens = relationship("AllergenSchema", secondary=ingredient_allergens)
