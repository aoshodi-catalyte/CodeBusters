"""
FastAPI router for ingredient management endpoints.

This module exposes API routes for creating, retrieving, and listing
ingredients. It coordinates request validation, repository operations,
and domain‑specific exception handling to ensure consistent and meaningful
HTTP responses for ingredient‑related actions.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from exceptions.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    IngredientNotFoundError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import Ingredient, IngredientOut
from repositories.ingredient_repository import IngredientRepository
from utils.response import to_response

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredient"],
)
logger = logging.getLogger("codebusters")


@router.post(
    "/",
    response_model=IngredientOut,
    status_code=status.HTTP_201_CREATED,
)
def create(
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    """Create a new ingredient.

    Args:
        ingredient: Validated ingredient information.
        db: Database session provided by FastAPI.

    Returns:
        The newly created ingredient.

    Raises:
        HTTPException:
            404 if the vendor does not exist.
        HTTPException:
            409 if the ingredient already exists or violates
            a database constraint.
        HTTPException:
            500 if an unexpected database error occurs.
    """
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
    """Retrieve all ingredients in the inventory.

    Args:
        db: Database session provided by FastAPI.

    Returns:
        A response containing a message and a list of all ingredients.
    """
    logger.debug("GET /ingredients called — retrieving all ingredients")
    repo = IngredientRepository(db)
    ingredients = repo.get_all_ingredients()
    logger.info("Retrieved %s ingredients", len(ingredients))
    return [to_response(IngredientOut, ingredient) for ingredient in ingredients]


@router.get(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def read_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single ingredient by its ID.

    Args:
        ingredient_id: ID of the ingredient to retrieve.
        db: Database session provided by FastAPI.

    Returns:
        The ingredient matching the specified ID.

    Raises:
        HTTPException:
            404 if the ingredient does not exist.
    """
    logger.debug("GET /ingredients/%s called — fetching ingredient", ingredient_id)
    repo = IngredientRepository(db)
    ingredient = repo.get_ingredient_by_id(ingredient_id)

    if ingredient is None:
        logger.warning("Ingredient %s not found", ingredient_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ingredient_not_found",
                "message": (
                    "Ingredient with ID %s was not found." % ingredient_id
                ),
            },
        )

    logger.info("Ingredient %s retrieved successfully", ingredient_id)
    return to_response(IngredientOut, ingredient)


@router.put(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def update(
    ingredient_id: int,
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    """Update an existing ingredient.

    Args:
        ingredient_id: ID of the ingredient to update.
        ingredient: Validated ingredient information.
        db: Database session provided by FastAPI.

    Returns:
        The updated ingredient.

    Raises:
        HTTPException:
            404 if the ingredient or vendor does not exist.
        HTTPException:
            409 if the update violates a database constraint.
        HTTPException:
            500 if an unexpected database error occurs.
    """
    logger.debug("PUT /ingredients/%s called — updating ingredient", ingredient_id)
    repo = IngredientRepository(db)

    try:
        result = repo.update_ingredient(ingredient_id, ingredient)
        logger.info("Ingredient %s updated successfully", ingredient_id)
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
    db: Session = Depends(get_db),
):
    """Soft delete an ingredient by its ID.

    Args:
        ingredient_id: ID of the ingredient to deactivate.
        db: Database session provided by FastAPI.

    Returns:
        A confirmation message and the ID of the deactivated ingredient.

    Raises:
        HTTPException:
            404 if the ingredient does not exist.
        HTTPException:
            500 if a database error occurs.
    """
    logger.debug("DELETE /ingredients/%s called — deleting ingredient", ingredient_id)
    repo = IngredientRepository(db)

    try:
        ingredient = repo.soft_delete_ingredient(ingredient_id)

        if ingredient is None:
            logger.warning("Ingredient %s not found for deletion", ingredient_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "ingredient_not_found",
                    "message": (
                        "Ingredient with ID %s was not found." % ingredient_id
                    ),
                },
            )

        logger.info("Ingredient %s deleted successfully", ingredient_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError as exc:
        logger.error("Ingredient deletion failed: %s", exc)
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
