"""
Business logic for creating purchases.

Handles price lookup, promotion validation, discount calculation,
tax computation, loyalty point awarding, and persistence through
the PurchaseRepository. This service contains all domain rules
for the checkout process.
"""

from datetime import UTC, datetime
from math import floor

from fastapi import HTTPException, status

from customer.customer_schema import CustomerSchema
from repositories.purchase_repository import PurchaseRepository


class PurchaseService:
    """
    Service layer responsible for executing the business rules
    required to create a purchase transaction.
    """

    def __init__(self, db):
        """
        Initialize the purchase service with a database session.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db
        self.repo = PurchaseRepository(db)

    def create_purchase(self, purchase_create):
        """
        Create a purchase transaction.

        Args:
            purchase_create (PurchaseCreate): Incoming purchase payload.

        Returns:
            PurchaseSchema: The persisted purchase record.
        """

        line_items = []
        subtotal = 0.0

        for item in purchase_create.items:
            price = self.repo.get_item_price(item.item_type, item.item_id)
            line_total = price * item.quantity

            line_items.append(
                {
                    "item_type": item.item_type,
                    "item_id": item.item_id,
                    "quantity": item.quantity,
                    "price_at_sale": price,
                }
            )

            subtotal += line_total

        discount_amount = 0.0

        if purchase_create.promo_id is not None:
            promo = self.repo.get_promotion(purchase_create.promo_id)
            if promo is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Promotion ID {purchase_create.promo_id} not found",
                )

            if not promo.active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Promotion is not active",
                )

            now = datetime.now(UTC)

            # Fix C0325: remove unnecessary parentheses
            if promo.start_datetime > now or now > promo.end_datetime:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Promotion is not within valid date range",
                )

            # Convert whole-number percentage (e.g., 20) → decimal (0.20)
            discount_percentage = promo.discount_percentage / 100
            discount_amount = subtotal * discount_percentage

        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * 0.07
        total = taxable_amount + tax_amount

        # Round values
        subtotal = round(subtotal, 2)
        discount_amount = round(discount_amount, 2)
        tax_amount = round(tax_amount, 2)
        total = round(total, 2)

        loyalty_points_awarded = floor(total)

        if purchase_create.customer_id is not None:
            customer = (
                self.db.query(CustomerSchema)
                .filter(CustomerSchema.id == purchase_create.customer_id)
                .first()
            )

            if customer is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer ID {purchase_create.customer_id} not found",
                )

            customer.loyalty_points += loyalty_points_awarded
            self.db.add(customer)

        purchase = self.repo.create_purchase(
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total=total,
            loyalty_points_awarded=loyalty_points_awarded,
            customer_id=purchase_create.customer_id,
            promo_id=purchase_create.promo_id,
            items=line_items,
        )

        return purchase
