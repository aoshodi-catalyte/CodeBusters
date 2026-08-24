"""
Utility helpers for formatting API responses.

Provides `to_response`, a small wrapper around Pydantic's `model_validate`
to ensure consistent response model validation across the application.
"""

from pydantic import BaseModel

def to_response(model: BaseModel, data: dict):
    """
    Convert a raw dict into a validated Pydantic response model.
    Centralizes model_validate usage.
    """
    return model.model_validate(data)