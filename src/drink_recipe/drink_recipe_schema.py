from drink_recipe.drink_ingredients_schema import drink_recipe_ingredient
from drink_recipe.drink_type_schema import DrinkTypeSchema
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DrinkRecipeSchema(Base):
    __tablename__ = "drink_recipe"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    production_cost = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("drink_type.id"), nullable=False)
    markup_percentage = Column(Float, default=0.0)
    sale_price = Column(Float, default=0.0)

    drink_type = relationship(DrinkTypeSchema, back_populates="drink_recipes")
    # NEW: many-to-many with ingredients
    ingredients = relationship(
        "IngredientSchema",
        secondary=drink_recipe_ingredient,
        back_populates="drink_recipes"
    )
