from fastapi import FastAPI

from src.database import Base, engine

# Import models so SQLAlchemy knows about the tables
from src.ingredient.ingredient_schema import (IngredientSchema, AllergenSchema, ingredient_allergen)

from src.ingredient.ingredient_router import router as ingredient_router


# Create database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(ingredient_router)