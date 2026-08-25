"""
API routes for application health and readiness checks.

This module provides liveness and readiness endpoints used to
determine whether the application process is running and whether
the application can successfully connect to the database.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db


router = APIRouter(
    tags=["Health"]
)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK
)
def health_check():
    """
    Liveness endpoint.

    Returns 200 as long as the application process is running,
    regardless of database availability.
    """
    return {"status": "ok"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK
)
def readiness_check(
    db: Session = Depends(get_db)
):
    """
    Readiness endpoint.

    Returns 200 when the application can successfully reach the
    database. Returns 503 when the database is unavailable.
    """
    try:
        db.execute(text("SELECT 1"))

        return {"status": "ready"}

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable."
        ) from exc
