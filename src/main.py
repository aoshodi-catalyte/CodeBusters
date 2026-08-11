from fastapi import FastAPI
# from src.vendor.vendor_router import router as vendor_router
from src.baked_good.baked_good_router import router as baked_good_router
app = FastAPI()

# app.include_router(vendor_router)
app.include_router(baked_good_router)