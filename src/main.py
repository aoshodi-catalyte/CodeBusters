from fastapi import FastAPI

from src.database import create_db
from src.customer.customer_schema import CustomerSchema
from src.customer.customer_router import router as customer_router


app = FastAPI(
    title="Customer API"
)


# Importing the SQLAlchemy model above registers it with
# Base.metadata before the database tables are created.
create_db()


app.include_router(customer_router)


@app.get("/")
def root():
    """
    Health check endpoint.
    """
    return {"message": "Customer API is running"}