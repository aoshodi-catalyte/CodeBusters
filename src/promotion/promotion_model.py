"""
Pydantic model for validating promotion data.

This module defines the Promotion model, which validates promotion
information before it is stored in the database. It ensures that
promo codes, discount percentages, and promotion date/time ranges
meet the application's validation requirements.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator, model_validator

class Promotion(BaseModel):
    """
    Represents a promotion with an active status, promo code,
    discount percentage, and date/time range.

    Attributes:
        active: Indicates whether the promotion is currently active.
        promo_code: A promotion code containing uppercase letters.
            Numbers, spaces, and symbols are allowed. Promo code
            uniqueness is enforced by the database.
        discount_percentage: The percentage discount applied by
            the promotion. Must be greater than zero.
        start_datetime: The date and time when the promotion begins.
            The expected input format is MM/DD/YYYY HH:MM AM/PM.
        end_datetime: The date and time when the promotion ends.
            The expected input format is MM/DD/YYYY HH:MM AM/PM.
            The end datetime must be the same as or later than the
            start datetime.
    """

    active: bool
    promo_code: str = Field(min_length=1)
    discount_percentage: float = Field(ge=0)
    start_datetime: datetime
    end_datetime: datetime

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

    @field_validator("discount_percentage")
    @classmethod
    def validate_discount_percentage(cls, value: float) -> float:
        """
        Validates that the discount percentage is within the
        allowed range.

        The discount must be greater than zero and cannot exceed
        100 percent.

        Args:
            value (float): The discount percentage to validate.

        Raises:
            ValueError: If the discount percentage exceeds 100.

        Returns:
            float: The validated discount percentage.
        """
        if value < 0 or value > 100:
            raise ValueError("Discount percentage must be between 0% and 100%.")

        return value

    @field_validator("start_datetime", "end_datetime", mode="before")
    @classmethod
    def convert_datetimes(cls, value: str | datetime) -> str | datetime:
        """
        Converts a user-friendly date/time string into a datetime.

        Accepts values in MM/DD/YYYY HH:MM AM/PM format.

        Args:
            value: The date/time value provided by the user.

        Raises:
            ValueError: If the date/time does not use the expected
                MM/DD/YYYY HH:MM AM/PM format.

        Returns:
            A datetime object or the original value if it is
            already a datetime.
        """

        if isinstance(value, str):
            try:
                return datetime.strptime(
                value,
                "%m/%d/%Y %I:%M %p"
            )
            except ValueError as exc:
                raise ValueError(
                    "Invalid date/time format. Please use MM/DD/YYYY HH:MM AM/PM."
                ) from exc
        return value

    @field_validator("start_datetime", "end_datetime")
    @classmethod
    def add_timezone(cls, value: datetime) -> datetime:
        """
        Adds the America/Chicago timezone to a datetime when
        timezone information is not provided.

        Args:
            value: The datetime value to validate.

        Returns:
            A timezone-aware datetime using the America/Chicago timezone.
        """

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=ZoneInfo("America/Chicago")
            )
        return value

    @model_validator(mode="after")
    def validate_dates(self):
        """
        Validates that the end datetime is the same as or later
        than the start datetime.

        Raises:
            ValueError: If the end datetime occurs before the
                start datetime.

        Returns:
            The validated Promotion object.
        """

        if self.end_datetime <= self.start_datetime:
            raise ValueError("End datetime must be after start datetime.")

        return self