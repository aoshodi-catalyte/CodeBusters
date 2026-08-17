# from promotion.promotion_model import Promotion
from promotion.promotion_schema import PromotionSchema
from promotion.promotion_response_model import PromotionResponseModel
from sqlalchemy import Session
from typing import List

from src.promotion.promotion_model import Promotion
from src.promotion.promotion_schema import PromotionSchema


class PromotionRepository():
    def __init__(self, session: Session) -> None:

        self.session = session 

    def create_promotion(self, promotion: PromotionSchema) ->PromotionSchema:
        new_promotion= Promotion
        self.promotion.append(promotion)
        return promotion