from promotion.promotion_repository import PromotionRepository
from promotion.promotion_response_model import PromotionResponseModel
from sqlalchemy.orm import Session
from database import Base, get_db
from fastapi import APIRouter, Depends

router = APIRouter()


class PromotionRouter():
    
    @router.post("/", promotion_response_model = PromotionResponseModel, status_code=201)
    def post_promotion(promotion_response_model: PromotionResponseModel, db: Session = Depends(get_db)) -> PromotionResponseModel:
        
        repo = PromotionRepository(db)
    