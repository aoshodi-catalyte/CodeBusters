"""
FastAPI router for ingredient management endpoints.

This module exposes API routes for creating, retrieving, updating,
and deactivating ingredients. It coordinates request validation,
repository operations, authorization, and domain-specific exception
handling to ensure consistent HTTP responses for ingredient actions.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from constants.entity_types import EntityType
from database import get_audit_db, get_db
from deactivation_log.deactivation_schema import DeactivationRecord
from employee.employee_schema import EmployeeSchema
from exceptions.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientAlreadyInactiveError,
    IngredientConstraintError,
    IngredientNotFoundError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import Ingredient, IngredientOut
from ingredient.ingredient_schema import IngredientSchema
from repositories.ingredient_repository import IngredientRepository
from security.secure_manager_login import check_role
from utils.response import to_response

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredient"],
)

logger = logging.getLogger("codebusters")


@router.post(
    "/",
    response_model=IngredientOut,
    dependencies=[Depends(check_role(["manager"]))],
    status_code=status.HTTP_201_CREATED,
)
def create(
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    """Create a new ingredient."""
    logger.debug("POST /ingredients called — creating ingredient")
    repo = IngredientRepository(db)

    try:
        created = repo.create_ingredient(ingredient)
        logger.info("Ingredient created successfully: id=%s", created.id)
        return to_response(IngredientOut, created)

    except VendorNotFoundError as exc:
        logger.warning("Vendor %s not found", ingredient.vendor_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "vendor_not_found",
                "message": str(exc),
            },
        ) from exc

    except IngredientAlreadyExistsError as exc:
        logger.warning("Ingredient creation warning: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ingredient_already_exists",
                "message": str(exc),
            },
        ) from exc

    except IngredientConstraintError as exc:
        logger.error("Ingredient creation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "database_constraint_violation",
                "message": str(exc),
            },
        ) from exc

    except SQLAlchemyError as exc:
        logger.error("Ingredient creation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": (
                    "An unexpected database error occurred "
                    "while creating the ingredient."
                ),
            },
        ) from exc


@router.get(
    "/",
    response_model=list[IngredientOut],
)
def read_all_ingredients(
    db: Session = Depends(get_db),
):
    """Retrieve all ingredients in the inventory."""
    logger.debug("GET /ingredients called — retrieving all ingredients")
    repo = IngredientRepository(db)
    ingredients = repo.get_all_ingredients()
    logger.info("Retrieved %s ingredients", len(ingredients))
    return [
        to_response(IngredientOut, ingredient)
        for ingredient in ingredients
    ]


@router.get(
    "/deactivated",
    response_model=list[IngredientOut],
    dependencies=[Depends(check_role(["manager"]))],
)
def read_deactivated_ingredients(
    db: Session = Depends(get_db),
):
    """Retrieve all deactivated ingredients."""
    logger.debug(
        "GET /ingredients/deactivated called — "
        "retrieving deactivated ingredients"
    )

    repo = IngredientRepository(db)
    ingredients = repo.get_deactivated_ingredients()

    logger.info(
        "Retrieved %s deactivated ingredients",
        len(ingredients),
    )

    return [
        to_response(IngredientOut, ingredient)
        for ingredient in ingredients
    ]


@router.get(
    "/{ingredient_id}/deactivation-history",
    dependencies=[Depends(check_role(["manager"]))],
)
def read_ingredient_deactivation_history(
    ingredient_id: int,
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db),
):
    """
    Retrieve deactivation audit history for an ingredient.

    The audit information includes the timestamp and user responsible
    for the deactivation.
    """
    logger.debug(
        "GET /ingredients/%s/deactivation-history called",
        ingredient_id,
    )

    ingredient = (
        db.query(IngredientSchema)
        .filter(IngredientSchema.id == ingredient_id)
        .first()
    )

    if ingredient is None:
        logger.warning(
            "Ingredient %s not found when retrieving history",
            ingredient_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ingredient_not_found",
                "message": (
                    f"Ingredient with ID {ingredient_id} was not found."
                ),
            },
        )

    history = (
        audit_db.query(DeactivationRecord)
        .filter(
            DeactivationRecord.item_id == ingredient_id,
            DeactivationRecord.entity_type_id
            == EntityType.INGREDIENT.value,
        )
        .order_by(
            DeactivationRecord.deactivated_at.desc(),
            DeactivationRecord.id.desc(),
        )
        .all()
    )

    logger.info(
        "Retrieved %s deactivation history records for ingredient %s",
        len(history),
        ingredient_id,
    )

    return history


@router.get(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def read_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single ingredient by its ID."""
    logger.debug(
        "GET /ingredients/%s called — fetching ingredient",
        ingredient_id,
    )

    repo = IngredientRepository(db)
    ingredient = repo.get_ingredient_by_id(ingredient_id)

    if ingredient is None:
        logger.warning("Ingredient %s not found", ingredient_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ingredient_not_found",
                "message": (
                    f"Ingredient with ID {ingredient_id} was not found."
                ),
            },
        )

    logger.info(
        "Ingredient %s retrieved successfully",
        ingredient_id,
    )

    return to_response(IngredientOut, ingredient)


@router.put(
    "/{ingredient_id}",
    dependencies=[Depends(check_role(["manager"]))],
    response_model=IngredientOut,
)
def update(
    ingredient_id: int,
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    """Update an existing ingredient."""
    logger.debug(
        "PUT /ingredients/%s called — updating ingredient",
        ingredient_id,
    )

    repo = IngredientRepository(db)

    try:
        result = repo.update_ingredient(ingredient_id, ingredient)

        logger.info(
            "Ingredient %s updated successfully",
            ingredient_id,
        )

        return to_response(IngredientOut, result)

    except IngredientNotFoundError as exc:
        logger.warning("Ingredient %s not found", ingredient_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ingredient_not_found",
                "message": str(exc),
            },
        ) from exc

    except VendorNotFoundError as exc:
        logger.warning("Vendor %s not found", ingredient.vendor_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "vendor_not_found",
                "message": str(exc),
            },
        ) from exc

    except IngredientAlreadyExistsError as exc:
        logger.error("Ingredient update failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ingredient_already_exists",
                "message": str(exc),
            },
        ) from exc

    except IngredientConstraintError as exc:
        logger.error("Ingredient update failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "database_constraint_violation",
                "message": str(exc),
            },
        ) from exc

    except SQLAlchemyError as exc:
        logger.error("Ingredient update failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": (
                    "An unexpected database error occurred "
                    "while updating the ingredient."
                ),
            },
        ) from exc


class IngredientDeleteResponse(BaseModel):
    """Schema used when confirming an ingredient soft delete."""

    message: str
    id: int


@router.delete(
    "/{ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ingredient_endpoint(
    ingredient_id: int,
    current_user: dict = Depends(check_role(["manager"])),
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db),
):
    """
    Soft delete an ingredient by its ID.

    The authenticated manager's employee ID is read from the token and
    used to look up their email, which is passed to the repository so
    that the deactivation is recorded in the audit database.
    """
    logger.debug(
        "DELETE /ingredients/%s called — deleting ingredient",
        ingredient_id,
    )

    employee_id = current_user.get("employee_id")

    if employee_id is None:
        logger.error(
            "Authenticated user does not contain employee_id"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "employee_not_identified",
                "message": (
                    "The authenticated employee could not be identified."
                ),
            },
        )

    employee = (
        db.query(EmployeeSchema)
        .filter(EmployeeSchema.id == employee_id)
        .first()
    )

    if employee is None:
        logger.error(
            "Authenticated employee %s not found in employee table",
            employee_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "employee_not_identified",
                "message": (
                    "The authenticated employee could not be identified."
                ),
            },
        )

    repo = IngredientRepository(
        db=db,
        audit_db=audit_db,
    )

    try:
        ingredient = repo.soft_delete_ingredient(
            ingredient_id=ingredient_id,
            employee_email=employee.email,
        )

        if ingredient is None:
            logger.warning(
                "Ingredient %s not found for deletion",
                ingredient_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ingredient_not_found",
                    "message": (
                        f"Ingredient with ID {ingredient_id} "
                        "was not found."
                    ),
                },
            )

        logger.info(
            "Ingredient %s deactivated successfully",
            ingredient_id,
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except IngredientAlreadyInactiveError as exc:
        logger.warning(
            "Ingredient %s is already inactive",
            ingredient_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ingredient_already_inactive",
                "message": str(exc),
            },
        ) from exc

    except SQLAlchemyError as exc:
        logger.error(
            "Ingredient deletion failed: %s",
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": (
                    "An unexpected database error occurred "
                    "while deactivating the ingredient."
                ),
            },
        ) from exc
