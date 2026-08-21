<<<<<<< HEAD
# src/utils/response.py
=======
"""
Utility helpers for formatting API responses.

Provides `to_response`, a small wrapper around Pydantic's `model_validate`
to ensure consistent response model validation across the application.
"""
>>>>>>> 752f2f1a4ffc90eff888836022669e8b0aabd549

from pydantic import BaseModel

def to_response(model: BaseModel, data: dict):
    """
    Convert a raw dict into a validated Pydantic response model.
    Centralizes model_validate usage.
    """
    return model.model_validate(data)
