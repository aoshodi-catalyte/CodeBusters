from promotion.promotion_repository import PromotionRepository
from promotion.promotion_response_model import PromotionResponseModel
from promotion.promotion_model import Promotion
from sqlalchemy.orm import Session
from database import Base, get_db
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix ="/promotions",
    tags=["promotions"]
)

@router.post("/", response_model = PromotionResponseModel, status_code=201)
def post_promotion(promotion_model: Promotion, db: Session = Depends(get_db)) -> PromotionResponseModel:
    
    repo = PromotionRepository(db)
    create_promotions = repo.create_promotion(promotion_model)

    return create_promotions
    
@router.get("/", response_model= PromotionResponseModel, status_code=200)
def get_promotion(promotion_model: Promotion, db: Session = Depends(get_db)) -> PromotionResponseModel:

    repo = PromotionRepository
    get_promotions = repo.get_promotion(promotion_model)

    return get_promotions