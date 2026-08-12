from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class DrinkTypeSchema(Base):
    __tablename__ = "drink_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # Back reference
    drink_recipes = relationship("DrinkRecipeSchema", back_populates="drink_type")
