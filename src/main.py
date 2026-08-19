from contextlib import asynccontextmanager
from fastapi import FastAPI
from constants.employee_roles import EmployeeRole
from employee.employee_role_schema import EmployeeRoleSchema
from database import SessionLocal, create_db
from constants.drink_types import DrinkType
from database import SessionLocal
from drink_recipe.drink_type_schema import DrinkTypeSchema
from drink_recipe.drink_recipe_router import router as drink_recipe_router
from vendor.vendor_router import router as vendor_router
from baked_good.baked_good_router import router as baked_good_router
from ingredient.ingredient_router import router as ingredient_router
from customer.customer_router import router as customer_router
from employee.employee_router import router as employee_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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


app = FastAPI(lifespan=lifespan)

app.include_router(customer_router)


@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "Customer API is running"}


app.include_router(drink_recipe_router)
app.include_router(vendor_router)
app.include_router(baked_good_router)
app.include_router(ingredient_router)
app.include_router(customer_router)
app.include_router(employee_router)
