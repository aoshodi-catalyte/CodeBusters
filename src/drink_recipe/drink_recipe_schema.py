from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class DrinkRecipeSchema(Base):
    __tablename__ = 'drink_recipe'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    type = Column(String, nullable=False)
    production_cost = Column(Float, nullable=False)

    ingredients = relationship("IngredientSchema", back_populates="drink_recipe")