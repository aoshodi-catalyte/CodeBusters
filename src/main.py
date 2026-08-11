from fastapi import FastAPI
from src.customer.customer_router import router as customer_router

app = FastAPI()

app.include_router(customer_router)

@app.get("/")
def root():
    return {"message": "Customer API is running"}