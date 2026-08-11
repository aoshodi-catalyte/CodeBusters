from src.drink_recipe.drink_ingredients_schema import drink_recipe_ingredient
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.database import Base

class DrinkRecipeSchema(Base):
    __tablename__ = "drink_recipe"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    type_id = Column(Integer, ForeignKey("drink_type.id"), nullable=False)
    drink_type = relationship("DrinkTypeSchema", back_populates="drink_recipes")

    production_cost = Column(Float, nullable=False)

    # NEW: many-to-many with ingredients
    ingredients = relationship(
        "IngredientSchema",
        secondary=drink_recipe_ingredient,
        back_populates="drink_recipes"
    )
