from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from database import Base

class PromotionSchema(Base):

    __tablename__ = "Promotion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, nullable=False)
    promo_code = Column(String, unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True),nullable=False)