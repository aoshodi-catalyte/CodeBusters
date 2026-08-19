from sqlalchemy import Boolean, CheckConstraint, Column, Enum, ForeignKey, Integer, Numeric, String, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from constants.INGREDIENT_TYPES import UnitOfMeasure
from database import Base

# ASSOCIATION TABLE
ingredient_allergen = Table("ingredient_allergen",
    Base.metadata,
    Column( "ingredient_id", ForeignKey("ingredient.id",ondelete="CASCADE"), primary_key=True,),
    Column( "allergen_id",  ForeignKey("allergen.id",ondelete="CASCADE"), primary_key=True,),
)

# SQLALCHEMY MODEL
class AllergenSchema(Base):
    __tablename__ = "allergen"
    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_allergen_name_not_blank"),
        UniqueConstraint("name", name="uq_allergen_name",),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    ingredients = relationship("IngredientSchema", secondary=ingredient_allergen, back_populates="allergens")

class IngredientSchema(Base):
    __tablename__ = "ingredient"

    __table_args__ = (
        CheckConstraint("length(trim(name)) > 0", name="ck_ingredient_name_not_blank"),
        CheckConstraint("purchasing_cost >= 0", name="ck_ingredient_purchasing_cost_non_negative"),
        CheckConstraint("unit_amount > 0", name="ck_ingredient_unit_amount_positive"),
        UniqueConstraint("name", name="uq_ingredient_name",),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False, default=True)
    name = Column(String(255), nullable=False) 
    purchasing_cost = Column(Numeric(10, 2), nullable=False) 
    unit_amount = Column(Numeric(10, 2), nullable=False) 
    unit_of_measure = Column(Enum(UnitOfMeasure), nullable=False)

    ingredient_recipes = relationship(
        "DrinkRecipeIngredientSchema", back_populates="ingredient"
    )
    allergens = relationship("AllergenSchema", secondary=ingredient_allergen, back_populates="ingredients")
    vendor_id = Column(Integer, ForeignKey("vendor.id", ondelete="RESTRICT",), nullable=False)
    vendor = relationship("Vendor", back_populates="ingredients")
