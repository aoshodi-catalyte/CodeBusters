"""
SQLAlchemy ORM models for purchases and purchase items.

Defines the database tables used to store purchase records and their
associated line items. These models support polymorphic item references
(baked goods and drink recipes) and integrate with the purchase service
and repository layers.
"""

from datetime import datetime, UTC
from sqlalchemy import (
    Column, Integer, Float, DateTime, ForeignKey, String
)
from sqlalchemy.orm import relationship
from database import Base


class PurchaseItemSchema(Base):
    """
    ORM model representing a single line item within a purchase.

    Fields:
        id (int): Primary key.
        purchase_id (int): Foreign key linking to the parent purchase.
        item_type (str): Type of item ("baked_good" or "drink_recipe").
        item_id (int): ID of the referenced item.
        quantity (int): Quantity purchased.
        price_at_sale (float): Price of the item at the time of sale.
    """
    __tablename__ = "purchase_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey("purchase.id"), nullable=False)

    item_type = Column(String(20), nullable=False)
    item_id = Column(Integer, nullable=False)

    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)

    purchase = relationship("PurchaseSchema", back_populates="items")


class PurchaseSchema(Base):
    """
    ORM model representing a complete purchase transaction.

    Fields:
        id (int): Primary key.
        customer_id (int | None): Optional customer reference.
        promo_id (int | None): Optional promotion reference.
        subtotal (float): Total before discounts and tax.
        discount_amount (float): Discount applied from promotion.
        tax_amount (float): Calculated tax amount.
        total (float): Final total after tax and discounts.
        loyalty_points_awarded (int): Loyalty points earned.
        created_at (datetime): Timestamp of purchase creation.
        items (list[PurchaseItemSchema]): Line items included in the purchase.
    """
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
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    customer = relationship("CustomerSchema")
    promotion = relationship("PromotionSchema")
    items = relationship("PurchaseItemSchema", back_populates="purchase")
