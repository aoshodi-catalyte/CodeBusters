from contextlib import asynccontextmanager
from fastapi import FastAPI
from vendor.vendor_router import router as vendor_router
from baked_good.baked_good_router import router as baked_good_router
from database import Base, engine
# Import models so SQLAlchemy knows about the tables
from ingredient.ingredient_schema import (IngredientSchema, AllergenSchema, ingredient_allergen)
from ingredient.ingredient_router import router as ingredient_router
from src.database import create_db
from src.customer.customer_schema import CustomerSchema
from src.customer.customer_router import router as customer_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup logic ---
    db = SessionLocal()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        for drink_type in DrinkType:
            existing = db.query(DrinkTypeSchema).filter_by(name=drink_type.value).first()
            if not existing:
                db.add(DrinkTypeSchema(name=drink_type.value))
        db.commit()
    finally:
        db.close()

    # Yield control to the app
    yield

    # --- Shutdown logic (optional) ---
    # e.g., close global resources, flush logs, etc.

app = FastAPI(lifespan=lifespan)

app.include_router(drink_recipe_router)
# app.include_router(vendor_router)
app.include_router(ingredient_router)
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

# Create database tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

