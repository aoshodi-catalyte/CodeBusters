"""
Business logic for creating purchases.
"""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from math import floor

from fastapi import HTTPException, status

from repositories.customer_repository import CustomerRepository
from repositories.purchase_repository import PurchaseRepository

TWO_PLACES = Decimal("0.01")
TAX_RATE = Decimal("0.07")


class PurchaseService:
    """
    Service layer responsible for executing the business rules
    required to create a purchase transaction.
    """

    def __init__(self, db):
        self.db = db
        self.repo = PurchaseRepository(db)
        self.customer_repo = CustomerRepository(db)

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        """Round a Decimal to exactly two decimal places, half-up."""
        return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    def _build_line_items_and_subtotal(self, purchase_create):
        """
        Build line items and compute the subtotal.

        Returns:
            tuple[list[dict], Decimal]: Line items and subtotal.
        """
        line_items = []
        subtotal = Decimal("0")

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

        Returns:
            Decimal: Discount amount.
        """
        if promo_id is None:
            return Decimal("0")

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

        discount_percentage = promo.discount_percentage
        if not isinstance(discount_percentage, Decimal):
            discount_percentage = Decimal(str(discount_percentage))

        return subtotal * (discount_percentage / Decimal("100"))

    def _compute_totals(self, subtotal: Decimal, discount: Decimal):
        """
        Compute tax, total, and loyalty points.

        Returns:
            tuple[Decimal, Decimal, int]: tax_amount, total, loyalty_points
        """
        taxable = subtotal - discount
        tax_amount = self._quantize(taxable * TAX_RATE)
        total = self._quantize(taxable + tax_amount)
        loyalty_points = floor(total)

        return tax_amount, total, loyalty_points

    def _update_loyalty_points(self, customer_id, loyalty_points):
        if customer_id is None:
            return

        customer = self.customer_repo.get_customer_or_404(customer_id)
        customer.loyalty_points += loyalty_points
        self.db.add(customer)

    def create_purchase(self, purchase_create):
        """
        Create a purchase transaction.

        Returns:
            PurchaseSchema: The persisted purchase record.
        """
        line_items, subtotal = self._build_line_items_and_subtotal(purchase_create)
        discount = self._apply_promotion(purchase_create.promo_id, subtotal)

        subtotal = self._quantize(subtotal)
        discount = self._quantize(discount)

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
