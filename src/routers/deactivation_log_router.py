# pylint: disable=duplicate-code
"""
FastAPI router for deactivation relationship logs.

Provides read-only endpoints for staff to review relationships
that remained active when an entity was deactivated.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from deactivation_log.deactivation_log_model import DeactivationLog
from repositories.deactivation_log_repository import DeactivationLogRepository


router = APIRouter(
    prefix="/deactivation-logs",
    tags=["deactivation-log"],
)


@router.get(
    "/",
    response_model=list[DeactivationLog],
)
def get_deactivation_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Retrieve all deactivation relationship logs.

    Returns:
        A list of deactivation logs ordered from newest to oldest.

    Raises:
        HTTPException:
            500 if a database error occurs.
    """
    repo = DeactivationLogRepository(db)

    try:
        logs = repo.get_all(skip=skip, limit=limit)

        return [
            DeactivationLog.model_validate(log)
            for log in logs
        ]

    except SQLAlchemyError as exc:
        raise HTTPException(  # pylint: disable=duplicate-code
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": (
                    "An unexpected database error occurred "
                    "while retrieving deactivation logs."
                ),
            },
        ) from exc


@router.get(
    "/{log_id}",
    response_model=DeactivationLog,
)
def get_deactivation_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single deactivation relationship log.

    Args:
        log_id: ID of the deactivation log.

    Returns:
        The requested deactivation log.

    Raises:
        HTTPException:
            404 if the log does not exist.
        HTTPException:
            500 if a database error occurs.
    """
    repo = DeactivationLogRepository(db)

    try:
        log = repo.get_by_id(log_id)

        if log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "deactivation_log_not_found",
                    "message": (
                        f"Deactivation log with ID {log_id} "
                        "was not found."
                    ),
                },
            )

        return DeactivationLog.model_validate(log)

    except SQLAlchemyError as exc:
        raise HTTPException(  # pylint: disable=duplicate-code
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": (
                    "An unexpected database error occurred "
                    "while retrieving the deactivation log."
                ),
            },
        ) from exc
