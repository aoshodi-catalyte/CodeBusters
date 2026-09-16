"""
Shared error-handling utilities for FastAPI repository operations.

This module centralizes the logic for converting domain-specific exceptions
into appropriate HTTPException responses while ensuring that the database
session is safely rolled back. Routers can use these helpers to avoid
duplicate try/except blocks and maintain consistent API error behavior.
"""

from fastapi import HTTPException, status


def handle_repo_exception(db, exc, not_found_errors=(), conflict_errors=()):
    """
    Roll back the database session and raise an HTTPException that matches
    the type of domain exception encountered.
    """
    db.rollback()

    if isinstance(exc, not_found_errors):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    if isinstance(exc, conflict_errors):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc)
    ) from exc
