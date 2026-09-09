"""
FastAPI router for promotion endpoints.

This module defines API endpoints for creating, retrieving, updating,
and deactivating promotions. It uses the PromotionRepository to interact
with the database and translates typed repository exceptions into the
appropriate HTTP responses.
"""
from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from exceptions.promotion_exceptions import (
    PromotionCodeAlreadyExistsError,
    PromotionConstraintError,
    PromotionNotFoundError,
)
from repositories.promotion_repository import PromotionRepository
from promotion.promotion_response_model import PromotionResponseModel
from promotion.promotion_model import Promotion
from security.secure_manager_login import check_role
router = APIRouter(
    prefix="/promotions",
    tags=["promotions"]
)


@router.post("/", dependencies=[Depends(check_role(["manager"]))],
             response_model=PromotionResponseModel, status_code=201)
def post_promotion(
    promotion_model: Promotion,
    db: Session = Depends(get_db)
) -> PromotionResponseModel:
    """
    Create a new promotion.

    Receives promotion data from the client, passes it to the
    PromotionRepository for database creation, and returns the
    newly created promotion.

    Args:
        promotion_model (Promotion): The promotion data provided
            by the client.
        db (Session): The database session provided by the
            get_db dependency.

    Returns:
        PromotionResponseModel: The newly created promotion.

    Raises:
        HTTPException: If the promo code already exists.
    """
    repo = PromotionRepository(db)

    try:
        post_promotions = repo.create_promotion(promotion_model)

    except PromotionCodeAlreadyExistsError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Promotion with promo code '{promotion_model.promo_code}' already exists."
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Promotion with promo code '{promotion_model.promo_code}' already exists."
        ) from exc

    return post_promotions


@router.get("/", response_model=List[PromotionResponseModel], status_code=200)
def get_all_promotions(db: Session = Depends(get_db)) -> List[PromotionResponseModel]:
    """
    Retrieve all promotions.

    Queries the PromotionRepository for all promotion records
    currently stored in the database and returns them to the client.

    Args:
        db (Session): The database session provided by the
            get_db dependency.

    Returns:
        List[PromotionResponseModel]: A list of all promotions
            retrieved from the database.
    """
    repo = PromotionRepository(db)
    get_promos = repo.get_all_promotions()

    return get_promos


@router.get(
    "/{promotion_id}",
    status_code=status.HTTP_200_OK,
    response_model=PromotionResponseModel)
def get_promotion_by_id(promotion_id: int, db: Session = Depends(get_db)) -> PromotionResponseModel:
    """
    Retrieves a promotion by its unique ID.

    Args:
        promotion_id: The unique identifier of the promotion to retrieve.
        db: The database session used to retrieve the promotion.

    Returns:
        The promotion matching the provided ID.

    Raises:
        HTTPException: Raised with a 404 status code when the promotion ID
        does not exist.
    """
    repo = PromotionRepository(db)

    try:
        return repo.get_promotion_by_id(promotion_id)
    except PromotionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{promotion_id}",
    response_model=PromotionResponseModel,
    status_code=status.HTTP_200_OK,
)
def update_promotion(
    promotion_id: int,
    promotion_model: Promotion,
    db: Session = Depends(get_db),
) -> PromotionResponseModel:
    """
    Update an existing promotion.

    Args:
        promotion_id: The unique identifier of the promotion to
            update.
        promotion_model: The updated promotion data provided by
            the client.
        db: The database session provided by the get_db dependency.

    Returns:
        PromotionResponseModel: The updated promotion.

    Raises:
        HTTPException: If the promotion does not exist, the update
            uses a promo code that already exists, or the record
            violates another database constraint.
    """
    repo = PromotionRepository(db)

    try:
        return repo.update_promotion(promotion_id, promotion_model)

    except PromotionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        PromotionCodeAlreadyExistsError,
        PromotionConstraintError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{promotion_id}",
    dependencies=[Depends(check_role(["manager"]))],
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
):
    """
    Deactivates a promotion (soft delete) by setting active to False.

    The promotion's record is preserved for historical purposes.

    Args:
        promotion_id: The unique identifier of the promotion to
            deactivate.
        db: The database session used to deactivate the promotion.

    Raises:
        HTTPException: Raised with a 404 status code when the promotion
        ID does not exist.
    """
    repo = PromotionRepository(db)

    try:
        repo.deactivate_promotion(promotion_id)
    except PromotionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
