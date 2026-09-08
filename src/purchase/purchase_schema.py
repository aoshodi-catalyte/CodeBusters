from datetime import datetime, UTC
from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey, String
)
from sqlalchemy.orm import relationship
from database import Base


class PurchaseItemSchema(Base):
    __tablename__ = "purchase_item"

    id = Column(Integer, primary_key=True, autoincrement=True)

    purchase_id = Column(Integer, ForeignKey("purchase.id"), nullable=False)

    # Polymorphic item reference
    item_type = Column(String(20), nullable=False)  # "baked_good" or "drink_recipe"
    item_id = Column(Integer, nullable=False)

    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)

    purchase = relationship("PurchaseSchema", back_populates="items")


class PurchaseSchema(Base):
    __tablename__ = "purchase"

    id = Column(Integer, primary_key=True, autoincrement=True)

    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=True)
    promo_id = Column(Integer, ForeignKey("promotion.id"), nullable=True)

    subtotal = Column(Float, nullable=False)
    discount_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

    loyalty_points_awarded = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # Relationships
    customer = relationship("CustomerSchema")
    promotion = relationship("PromotionSchema")
    items = relationship("PurchaseItemSchema", back_populates="purchase")
