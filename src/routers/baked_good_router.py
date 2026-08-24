"""
FastAPI router for baked good endpoints.

This module defines API endpoints for retrieving and creating baked goods.
It uses the BakedGoodRepository to interact with the database and
provides validated request and response models for the baked good data.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from baked_good.baked_good_model import BakedGood
from baked_good.baked_good_response_model import BakedGoodResponseModel
from database import get_db
from repositories.baked_good_repository import BakedGoodRepository


router = APIRouter(
    prefix="/baked_goods",
    tags=["baked_goods"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[BakedGoodResponseModel])
def get_baked_goods(db: Session = Depends(get_db)) -> List[BakedGoodResponseModel]:
    """
    Retrieves all baked goods from the database.

    Args:
        db: The SQLAlchemy database session used to access the
            baked goods stored in the database.

    Returns:
        A list of BakedGood objects representing all baked
        goods stored in the database.
    """

    repo = BakedGoodRepository(db)
    baked_goods = repo.get_baked_goods()

    return baked_goods


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BakedGoodResponseModel)
def post_baked_good(baked_good: BakedGood, db: Session = Depends(get_db)) -> BakedGoodResponseModel:
    """
    Creates and stores a new baked good in the database.

    Passes the validated BakedGood Pydantic model to the repository,
    which converts it into a BakedGoodSchema SQLAlchemy model,
    adds it to the database, commits the transaction, and refreshes
    the object with its database-generated values.

    Args:
        baked_good: The validated baked good data received from the request.
        db: The SQLAlchemy database session provided by the get_db dependency.

    Returns:
        BakedGoodResponseModel: The newly created baked good,
            including its database-generated ID.
    """
    repo = BakedGoodRepository(db)
    try:
        created_baked_good = repo.create_baked_good(baked_good)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot create baked good because the vendor does not exist."
        ) from exc

    return created_baked_good
