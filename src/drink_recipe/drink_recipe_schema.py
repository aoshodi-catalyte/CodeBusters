from ingredient.ingredient_schema import IngredientSchema

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class DrinkRecipeSchema(Base):
    __tablename__ = 'drink_recipe'

    ingredient = relationship(
        IngredientSchema,
        back_populates="drink_recipe"
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    type = Column(Integer, nullable=False)
    production_cost = Column(Float, nullable=False)

    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), nullable=False)