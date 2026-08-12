from fastapi import FastAPI
from vendor.vendor_router import router as vendor_router
from baked_good.baked_good_router import router as baked_good_router
from database import Base, engine
# Import models so SQLAlchemy knows about the tables
from ingredient.ingredient_schema import (IngredientSchema, AllergenSchema, ingredient_allergen)
from ingredient.ingredient_router import router as ingredient_router

app = FastAPI()

# app.include_router(vendor_router)
app.include_router(vendor_router)
app.include_router(baked_good_router)
app.include_router(ingredient_router)

# Create database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

