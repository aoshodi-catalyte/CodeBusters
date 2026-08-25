"""
FastAPI application entry point.

Initializes the API, seeds required database values, and registers all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from constants.drink_types import DrinkType
from constants.employee_roles import EmployeeRole
from database import SessionLocal, create_db
from routers.drink_recipe_router import router as drink_recipe_router

from drink_recipe.drink_type_schema import DrinkTypeSchema
from employee.employee_role_schema import EmployeeRoleSchema
from health.health_router import router as health_router
from routers.baked_good_router import router as baked_good_router
from routers.customer_router import router as customer_router
from routers.drink_recipe_router import router as drink_recipe_router
from routers.employee_router import router as employee_router
from routers.ingredient_router import router as ingredient_router
from routers.promotion_router import router as promotion_router
from vendor.vendor_router import router as vendor_router
from secure_login.secure_login_router import router as secure_login_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application startup and shutdown lifecycle handler.

    Seeds initial drink type and employee role data and ensures
    database tables exist.
    """
    # --- Startup logic ---
    db = SessionLocal()
    create_db()

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

    # Yield control to the application
    yield

    # --- Shutdown logic ---
    # e.g., close global resources, flush logs, etc.


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    """
    Root endpoint.
    """
    return {"message": "API is running"}


app.include_router(health_router)
app.include_router(drink_recipe_router)
app.include_router(vendor_router)
app.include_router(baked_good_router)
app.include_router(ingredient_router)
app.include_router(customer_router)
app.include_router(employee_router)
app.include_router(promotion_router)
app.include_router(secure_login_router)
