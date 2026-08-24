"""
FastAPI application entry point.

Initializes the API, seeds required database values, and registers all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from baked_good.baked_good_router import router as baked_good_router
from constants.drink_types import DrinkType
from constants.employee_roles import EmployeeRole
from customer.customer_router import router as customer_router
from database import SessionLocal, create_db
from drink_recipe.drink_recipe_router import router as drink_recipe_router
from drink_recipe.drink_type_schema import DrinkTypeSchema
from employee.employee_role_schema import EmployeeRoleSchema
from employee.employee_router import router as employee_router
from ingredient.ingredient_router import router as ingredient_router
from promotion.promotion_router import router as promotion_router
from vendor.vendor_router import router as vendor_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application startup and shutdown lifecycle handler.

    Seeds initial drink type data and ensures database tables exist.
    """
    # --- Startup logic ---
    db = SessionLocal()
    create_db()  # Ensure tables are created before seeding data
    try:
        for drink_type in DrinkType:
            existing = (
                db.query(DrinkTypeSchema).filter_by(name=drink_type.value).first()
            )
            if not existing:
                db.add(DrinkTypeSchema(name=drink_type.value))

        for role in EmployeeRole:
            existing = db.query(EmployeeRoleSchema).filter_by(role=role.value).first()
            if not existing:
                db.add(EmployeeRoleSchema(role=role.value))

        db.commit()
    finally:
        db.close()

    # Yield control to the app
    yield

    # --- Shutdown logic (optional) ---
    # e.g., close global resources, flush logs, etc.

<<<<<<< HEAD
=======

>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
app = FastAPI(lifespan=lifespan)

app.include_router(customer_router)

@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "API is running"}


app.include_router(drink_recipe_router)
app.include_router(vendor_router)
app.include_router(baked_good_router)
app.include_router(ingredient_router)
app.include_router(customer_router)
app.include_router(employee_router)
<<<<<<< HEAD
app.include_router(promotion_router)
=======
app.include_router(promotion_router)
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
