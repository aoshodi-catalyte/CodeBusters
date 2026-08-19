"""
FastAPI router for promotion endpoints.

This module defines API endpoints for creating and retrieving promotions.
It uses the PromotionRepository to interact with the database and handles
duplicate promo codes by returning an appropriate HTTP error response.
"""
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from promotion.promotion_repository import PromotionRepository
from promotion.promotion_response_model import PromotionResponseModel
from promotion.promotion_model import Promotion
router = APIRouter(
    prefix="/promotions",
    tags=["promotions"]
)

@router.post("/", response_model = PromotionResponseModel, status_code=201)
def post_promotion(promotion_model: Promotion, db: Session = Depends(get_db)) -> PromotionResponseModel:
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

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Promotion with promo code "
                   f"'{promotion_model.promo_code}' already exists."
        )

    return post_promotions
    
@router.get("/", response_model= List[PromotionResponseModel], status_code=200)
def get_promotions(db: Session = Depends(get_db)) -> List[PromotionResponseModel]:
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
    get_promotions = repo.get_all_promotions()

    return get_promotions