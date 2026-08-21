"""
FastAPI router for ingredient management endpoints.

This module exposes API routes for creating, retrieving, and listing
ingredients. It coordinates request validation, repository operations,
and domain‑specific exception handling to ensure consistent and meaningful
HTTP responses for ingredient‑related actions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import (
    Ingredient,
    IngredientListResponse,
    IngredientOut,
)
from ingredient.ingredient_repository import (
    create_ingredient,
    get_all_ingredients,
    get_ingredient_by_id,
)


router = APIRouter(
    prefix="/ingredients",
    tags=["ingredient"],
)


@router.post(
    "/",
    response_model=IngredientOut,
    status_code=status.HTTP_201_CREATED,
)
def create(
    ingredient: Ingredient,
    db: Session = Depends(get_db),
) -> IngredientOut:
    """Create a new ingredient.

    Args:
        ingredient: Validated ingredient data.
        db: Database session provided by FastAPI.

    Returns:
        The newly created ingredient.

    Raises:
        HTTPException: If the vendor does not exist, the ingredient
            already exists, a database constraint is violated, or
            an unexpected database error occurs.
    """
    try:
        return create_ingredient(
            db=db,
            ingredient_data=ingredient,
        )

    except VendorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "vendor_not_found",
                "message": str(exc),
            },
        ) from exc

    except IngredientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ingredient_already_exists",
                "message": str(exc),
            },
        ) from exc

    except IngredientConstraintError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "database_constraint_violation",
                "message": str(exc),
            },
        ) from exc

    except SQLAlchemyError as exc:
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
    "/all",
    response_model=IngredientListResponse,
)
def read_all_ingredients(
    db: Session = Depends(get_db),
) -> IngredientListResponse:
    """Retrieve all ingredients in the inventory.

    Args:
        db: Database session provided by FastAPI.

    Returns:
        A response containing a message and a list of all ingredients.
    """
    ingredients = get_all_ingredients(db)

    return {
        "message": "These are all the ingredients in your inventory!",
        "ingredients": ingredients,
    }


@router.get(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def read_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
) -> IngredientOut:
    """Retrieve a single ingredient by its ID.

    Args:
        ingredient_id: ID of the ingredient to retrieve.
        db: Database session provided by FastAPI.

    Returns:
        The ingredient matching the specified ID.

    Raises:
        HTTPException: If the ingredient does not exist.
    """
    ingredient = get_ingredient_by_id(
        db=db,
        ingredient_id=ingredient_id,
    )

    if ingredient is None:
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

    return ingredient