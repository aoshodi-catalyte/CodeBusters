"""
SQLAlchemy schema for promotions.

This module defines the PromotionSchema database model, which represents
promotions stored in the database, including their promo codes, discount
percentages, and active date and time ranges.

discount_percentage uses Numeric(5, 2) rather than Float so that values
are stored with exact two-decimal-place precision (e.g. 12.50), instead
of the approximate binary representation floats use.
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String

from database import Base

class PromotionSchema(Base):
    """
    Represents a promotion stored in the database.

    Attributes:
        id: The unique, automatically generated identifier for the promotion.
        active: Indicates whether the promotion is currently active.
        promo_code: The unique promotional code used to apply the promotion.
        discount_percentage: The percentage discount provided by the promotion,
            stored with exactly two decimal places.
        start_datetime: The date and time when the promotion begins.
        end_datetime: The date and time when the promotion ends.
    """
    __tablename__ = "promotion"
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, nullable=False)
    promo_code = Column(String, unique=True, nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
