"""
Custom exception classes used for promotion-related operations.

These exceptions allow the repository layer to raise clear, typed errors
that the router can catch and translate into appropriate HTTP responses,
rather than relying on generic Exception handling or building HTTPException
objects directly in business logic.
"""


class PromotionNotFoundError(Exception):
    """Raised when a promotion with the given ID does not exist."""

    def __init__(self, promotion_id: int) -> None:
        self.promotion_id = promotion_id
        super().__init__(
            f"Promotion with ID {promotion_id} was not found."
        )


class PromotionCodeAlreadyExistsError(Exception):
    """Raised when a promotion with the given promo code already exists."""

    def __init__(self, promo_code: str) -> None:
        self.promo_code = promo_code
        super().__init__(
            f"Promotion with promo code '{promo_code}' already exists."
        )


class PromotionConstraintError(Exception):
    """Raised when a promotion record violates a database constraint."""

    def __init__(self, constraint: str | None = None) -> None:
        self.constraint = constraint
        super().__init__(
            "The promotion record violates a database constraint."
        )
