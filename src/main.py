from fastapi import FastAPI
from vendor.vendor_router import router as vendor_router
from baked_good.baked_good_router import router as baked_good_router
from database import Base, engine
# Import models so SQLAlchemy knows about the tables
from ingredient.ingredient_schema import (IngredientSchema, AllergenSchema, ingredient_allergen)
from ingredient.ingredient_router import router as ingredient_router


# from customer.customer_schema import CustomerSchema
from customer.customer_router import router as customer_router


app = FastAPI(
    title="Customer API"
)


# Importing the SQLAlchemy model above registers it with
# Base.metadata before the database tables are created.
# create_db()


app.include_router(customer_router)


@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "Customer API is running"}
# app.include_router(vendor_router)
app.include_router(vendor_router)
app.include_router(baked_good_router)
app.include_router(ingredient_router)
app.include_router(customer_router)

# Create database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

