<<<<<<< HEAD
<<<<<<< HEAD
# src/utils/response.py
=======
=======
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73
"""
Utility helpers for formatting API responses.

Provides `to_response`, a small wrapper around Pydantic's `model_validate`
to ensure consistent response model validation across the application.
"""
<<<<<<< HEAD
>>>>>>> 8bb3688c86749408fa79034a4abffc034ea8909c
=======
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

from pydantic import BaseModel

def to_response(model: BaseModel, data: dict):
    """
    Convert a raw dict into a validated Pydantic response model.
    Centralizes model_validate usage.
    """
    return model.model_validate(data)