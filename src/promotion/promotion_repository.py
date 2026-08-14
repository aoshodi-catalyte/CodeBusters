from promotion import promotion_model
from promotion import promotion_schema
from src.promotion.promotion_response_model import PromotionResponseModel
from sqlalchemy.orm import Session
from typing import List


class PromotionRepository():
    def __init__(self) -> None:

        self.Promotion: List[PromotionResponseModel] = []


    def create_promotion(self, promotion: PromotionResponseModel) ->PromotionResponseModel:
        
        self.promotion.append(promotion)
        return promotion