from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.ingredient.ingredient_model import Ingredient
from src.ingredient.ingredient_repository import create_ingredient

router = APIRouter(
    prefix="/ingredient",
    tags=["ingredient"],
)
# ==========================================
# CREATE INGREDIENT
# ==========================================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def create(
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    try:
        created_ingredient = create_ingredient(
            db=db,
            ingredient_data=ingredient,
        )
        return created_ingredient
    # ======================================
    # DATABASE CONSTRAINT ERROR
    # ======================================
    except IntegrityError as exc:
        db.rollback()
        constraint = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )
        # ----------------------------------
        # Duplicate ingredient
        # ----------------------------------
        if constraint == "uq_ingredient_name":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "ingredient_already_exists",
                    "message": ("An ingredient with this name already exists."),
                },
            ) from exc
        # ----------------------------------
        # Ingredient database constraints
        # ----------------------------------
        if constraint == "ck_ingredient_name_not_blank":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "invalid_ingredient_name",
                    "message": ("Ingredient name cannot be blank."),
                },
            ) from exc

        if constraint == "ck_ingredient_purchasing_cost_non_negative":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "invalid_purchasing_cost",
                    "message": ("Purchasing cost cannot be negative."),
                },
            ) from exc

        if constraint == "ck_ingredient_unit_amount_positive":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "invalid_unit_amount",
                    "message": ("Unit amount must be greater than zero."),
                },
            ) from exc
        # ----------------------------------
        # Other database constraint
        # ----------------------------------
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "database_constraint_violation",
                "message": ("The ingredient could not be created because of a database constraint."),
            },
        ) from exc
    # ======================================
    # UNEXPECTED DATABASE ERROR
    # ======================================
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "database_error",
                "message": ("An unexpected database error occurred while creating the ingredient."),
            },
        ) from exc