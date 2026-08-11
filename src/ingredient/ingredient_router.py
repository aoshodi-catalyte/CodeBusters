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

@router.post( "/", status_code=status.HTTP_201_CREATED )
def create(
    ingredient: Ingredient,
    db: Session = Depends(get_db),
):
    try:
        # Pydantic has already validated the ingredient
        # before this function runs.
        created_ingredient = create_ingredient( db=db, ingredient_data=ingredient,)
        return created_ingredient

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient or allergen already exists.",
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NotWorking",
        )