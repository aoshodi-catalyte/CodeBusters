"""
FastAPI application entry point.

Initializes the API, seeds required database values, and registers all routers.
"""

from contextlib import asynccontextmanager

import logging
import time

from fastapi import FastAPI, Request

from utils.logging_config import configure_logging
from constants.drink_types import DrinkType
from constants.employee_roles import EmployeeRole
from constants.entity_types import EntityType
from database import AuditSessionLocal, SessionLocal, create_db
from deactivation_log.entity_type_schema import EntityTypeSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
from employee.employee_role_schema import EmployeeRoleSchema
from health.health_router import router as health_router
from routers.purchase_router import router as purchase_router
from routers.baked_good_router import router as baked_good_router
from routers.customer_router import router as customer_router
from routers.drink_recipe_router import router as drink_recipe_router
from routers.employee_router import router as employee_router
from routers.ingredient_router import router as ingredient_router
from routers.promotion_router import router as promotion_router
from routers.secure_login_router import router as secure_login_router
from routers.secure_logout_router import router as secure_logout_router
from routers.vendor_router import router as vendor_router
from routers.password_reset_router import router as password_reset_router

from routers.deactivation_log_router import router as deactivation_log_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Application startup and shutdown lifecycle handler.

    Seeds initial drink type and employee role data and ensures
    database tables exist.
    """
    # --- Startup logic ---
    db = SessionLocal()
    audit_db = AuditSessionLocal()
    create_db()

    try:
        for drink_type in DrinkType:
            existing = (
                db.query(DrinkTypeSchema).filter_by(
                    name=drink_type.value).first()
            )

            if not existing:
                db.add(DrinkTypeSchema(name=drink_type.value))

        for role in EmployeeRole:
            existing = db.query(EmployeeRoleSchema).filter_by(
                role=role.value).first()

            if not existing:
                db.add(EmployeeRoleSchema(role=role.value))

        for entity in EntityType:
            existing = audit_db.query(EntityTypeSchema).filter_by(id=entity.value).first()

            if not existing:
                audit_db.add(
                    EntityTypeSchema(
                        id=entity.value,
                        name=entity.label()
                    )
                )

        db.commit()
        audit_db.commit()

    finally:
        db.close()
        audit_db.close()

    # Yield control to the application
    yield

    # --- Shutdown logic ---
    # e.g., close global resources, flush logs, etc.


configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log each HTTP request with its method, path, status code, and duration.

    Unhandled exceptions are logged with their traceback before being
    re-raised so FastAPI can handle them normally.
    """
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "Unhandled exception during %s %s (%.2f ms)",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response

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
app.include_router(secure_logout_router)
app.include_router(password_reset_router)
app.include_router(deactivation_log_router)
app.include_router(purchase_router)
