from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db

from ingredient.ingredient_exceptions import IngredientAlreadyExistsError, IngredientConstraintError, VendorNotFoundError
from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_repository import create_ingredient, get_all_ingredients, get_ingredient_by_id, update_ingredient
from ingredient.ingredient_model import IngredientOut, IngredientListResponse


router = APIRouter(
    prefix="/ingredients",
    tags=["ingredient"],
)


@router.post("/", response_model=IngredientOut, status_code=status.HTTP_201_CREATED,)
def create(ingredient: Ingredient,db: Session = Depends(get_db),):
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
            409 if the ingredient already exists or
            violates a database constraint.
        HTTPException:
            500 if an unexpected database error occurs.
    """
    try:
        return create_ingredient(db=db, ingredient_data=ingredient,)
    # VENDOR NOT FOUND
    except VendorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "vendor_not_found",
                "message": str(exc),
            },
        ) from exc
    # DUPLICATE INGREDIENT
    except IngredientAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ingredient_already_exists",
                "message": str(exc),
            },
        ) from exc
    # DATABASE CONSTRAINT
    except IngredientConstraintError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "database_constraint_violation",
                "message": str(exc),
            },
        ) from exc
    # UNEXPECTED DATABASE ERROR
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": ("An unexpected database error occurred while creating the ingredient.")
            },
        ) from exc

@router.get("/all", response_model=IngredientListResponse)
def read_all_ingredients(db: Session = Depends(get_db)):
    """
    Retrieve all ingredients in the inventory.

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

@router.get("/{ingredient_id}", response_model=IngredientOut)
def read_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single ingredient by its ID.

    Args:
        ingredient_id: ID of the ingredient to retrieve.
        db: Database session provided by FastAPI.

    Returns:
        The ingredient matching the specified ID.

    Raises:
        HTTPException:
            404 if the ingredient does not exist.
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
                "message": f"Ingredient with ID {ingredient_id} was not found.",
            },
        )

    return ingredient
    
@router.put(
    "/{ingredient_id}",
    response_model=IngredientOut,
)
def update(
    ingredient_id: int,
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    """
    Update an existing ingredient.

    Args:
        ingredient_id: ID of the ingredient to update.
        ingredient: Validated ingredient information.
        db: Database session provided by FastAPI.

    Returns:
        The updated ingredient.

    Raises:
        HTTPException:
            404 if the ingredient does not exist or the vendor
            does not exist.
        HTTPException:
            409 if the update violates a database constraint.
        HTTPException:
            500 if an unexpected database error occurs.
    """
    try:
        result = update_ingredient(
            db=db,
            ingredient_id=ingredient_id,
            ingredient_data=ingredient,
        )

        if result is None:
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

        return result

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
                    "while updating the ingredient."
                ),
            },
        ) from exc