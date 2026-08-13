from datetime import date
from pydantic import BaseModel, field_validator


class Promotion(BaseModel):
    """
    Represents a promotion with an active status, promo code,
    discount percentage, and date range.

    Attributes:
        active: Indicates whether the promotion is currently active.
        promo_code: A promotion code containing uppercase letters.
            Numbers, spaces, and symbols are allowed.
        discount_percentage: The percentage discount applied by the promotion.
        start_date: The date when the promotion begins.
        end_date: The date when the promotion ends.
    """

    active: bool
    promo_code: str
    discount_percentage: float
    start_date: date
    end_date: date

    @field_validator("promo_code")
    @classmethod
    def validate_promo_code(cls, value: str) -> str:
        """
        Validates the format of the promotion code.

        Promo codes must contain uppercase letters. Numbers, spaces,
        and symbols are allowed. Leading and trailing spaces are not
        permitted.

        Args:
            value: The promotion code to validate.

        Raises:
            ValueError: If the promo code contains lowercase letters
                or starts or ends with a space.

        Returns:
            The validated promotion code.
        """

        if value != value.upper():
            raise ValueError(
                "Promo code letters must be uppercase."
                )
        if value != value.strip():
            raise ValueError("Promo code cannot start or end with a space")

        return value