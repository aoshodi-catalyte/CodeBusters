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
from baked_good.baked_good_exceptions import (
    DuplicateBakedGoodError,
    VendorNotFoundError,
)

router = APIRouter(prefix="/baked_goods", tags=["baked_goods"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=BakedGoodResponseModel
)
def post_baked_good(
    baked_good: BakedGood, db: Session = Depends(get_db)
) -> BakedGoodResponseModel:
    """
    Creates and stores a new baked good in the database.

    Args:
        baked_good: The validated baked good data received from the request.
        db: The SQLAlchemy database session provided by the get_db dependency.

    Returns:
        BakedGoodResponseModel: The newly created baked good.

    Raises:
        HTTPException: If the vendor does not exist or the baked good
            already exists for the vendor.
    """
    repo = BakedGoodRepository(db)
    try:
        created_baked_good = repo.create_baked_good(baked_good)

    except VendorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot create baked good because the vendor does not exist.",
        ) from exc

    except DuplicateBakedGoodError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A baked good with name '{baked_good.name}' already exists",
        ) from exc

    return created_baked_good


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[BakedGoodResponseModel]
)
def get_all_baked_goods(db: Session = Depends(get_db)) -> List[BakedGoodResponseModel]:
    """
    Retrieves all baked goods from the database.

    Args:
        db: The SQLAlchemy database session used to access the
            baked goods stored in the database.

    Returns:
        A list of BakedGoodResponseModel objects representing all
        baked goods stored in the database.
    """

    repo = BakedGoodRepository(db)
    baked_goods = repo.get_all_baked_goods()

    return baked_goods


@router.get(
    "/{baked_good_id}",
    status_code=status.HTTP_200_OK,
    response_model=BakedGoodResponseModel,
)
def get_baked_good_by_id(
    baked_good_id: int, db: Session = Depends(get_db)
) -> BakedGoodResponseModel:
    """
    Retrieves a baked good by its ID.

    Args:
        baked_good_id: The unique ID of the baked good.
        db: The database session.

    Returns:
        The baked good matching the provided ID.

    Raises:
        HTTPException: If the baked good does not exist.
    """
    repository = BakedGoodRepository(db)
    baked_good = repository.get_baked_good_by_id(baked_good_id)

    if baked_good is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Baked Good ID"
        )
    return baked_good
