from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import engine
# from src.vendor.vendor_router import router as vendor_router
from src.constants.DRINK_TYPES import DrinkType
from src.database import Base, SessionLocal
from src.drink_recipe.drink_type_schema import DrinkTypeSchema
from src.drink_recipe.drink_recipe_router import router as drink_recipe_router
# from src.vendor.vendor_router import router as vendor_router
from src.baked_good.baked_good_router import router as baked_good_router
app = FastAPI()

# app.include_router(vendor_router)
app.include_router(baked_good_router)

from src.database import Base, engine
from src.ingredient.ingredient_schema import IngredientSchema, AllergenSchema, ingredient_allergen
from src.ingredient.ingredient_router import router as ingredient_router


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