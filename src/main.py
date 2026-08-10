from fastapi import FastAPI
from src.vendor.vendor_router import router as vendor_router

app = FastAPI()

app.include_router(vendor_router)