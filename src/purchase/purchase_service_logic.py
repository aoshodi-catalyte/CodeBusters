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


    def _build_line_items_and_subtotal(self, purchase_create):
        """
        Build line items and compute the subtotal.

        Args:
            purchase_create (PurchaseCreate): Incoming purchase payload.

        Returns:
            tuple[list[dict], float]: Line items and subtotal.
        """
        line_items = []
        subtotal = 0.0

        for item in purchase_create.items:
            price = self.repo.get_item_price(item.item_type, item.item_id)
            line_items.append(
                {
                    "item_type": item.item_type,
                    "item_id": item.item_id,
                    "quantity": item.quantity,
                    "price_at_sale": price,
                }
            )
            subtotal += price * item.quantity

        return line_items, subtotal

    def _apply_promotion(self, promo_id, subtotal):
        """
        Validate and apply a promotion to compute the discount amount.

        Args:
            promo_id (int | None): Promotion ID.
            subtotal (float): Current subtotal.

        Returns:
            float: Discount amount.
        """
        if promo_id is None:
            return 0.0

        promo = self.repo.get_promotion(promo_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Promotion ID {promo_id} not found",
            )

        if not promo.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promotion is not active",
            )

        now = datetime.now(UTC)
        start = promo.start_datetime.replace(tzinfo=UTC)
        end = promo.end_datetime.replace(tzinfo=UTC)

        if start > now or now > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promotion is not within valid date range",
            )

        return subtotal * (promo.discount_percentage / 100)

    def _compute_totals(self, subtotal, discount):
        """
        Compute taxable amount, tax, total, and loyalty points.

        Args:
            subtotal (float): Subtotal before discount.
            discount (float): Discount amount.

        Returns:
            tuple[float, float, float, int]: tax_amount, total, loyalty_points
        """
        taxable = subtotal - discount
        tax_amount = taxable * 0.07
        total = taxable + tax_amount

        tax_amount = round(tax_amount, 2)
        total = round(total, 2)
        loyalty_points = floor(total)

        return tax_amount, total, loyalty_points

    def _update_loyalty_points(self, customer_id, loyalty_points):
        """
        Update loyalty points for a customer if applicable.

        Args:
            customer_id (int | None): Customer ID.
            loyalty_points (int): Points to award.
        """
        if customer_id is None:
            return

        customer = (
            self.db.query(CustomerSchema)
            .filter(CustomerSchema.id == customer_id)
            .first()
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer ID {customer_id} not found",
            )

        customer.loyalty_points += loyalty_points
        self.db.add(customer)


    def create_purchase(self, purchase_create):
        """
        Create a purchase transaction.

        Args:
            purchase_create (PurchaseCreate): Incoming purchase payload.

        Returns:
            PurchaseSchema: The persisted purchase record.
        """
        line_items, subtotal = self._build_line_items_and_subtotal(purchase_create)
        discount = self._apply_promotion(purchase_create.promo_id, subtotal)

        subtotal = round(subtotal, 2)
        discount = round(discount, 2)

        tax_amount, total, loyalty_points = self._compute_totals(subtotal, discount)
        self._update_loyalty_points(purchase_create.customer_id, loyalty_points)

        purchase_data = {
            "subtotal": subtotal,
            "discount_amount": discount,
            "tax_amount": tax_amount,
            "total": total,
            "loyalty_points_awarded": loyalty_points,
            "customer_id": purchase_create.customer_id,
            "promo_id": purchase_create.promo_id,
        }

        return self.repo.create_purchase(purchase_data, line_items)
