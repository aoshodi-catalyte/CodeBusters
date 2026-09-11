"""
Pydantic models for validating baked good data.

This module defines BakedGoodBase, the shared validation rules for baked
good data, along with BakedGood (used when creating a baked good) and
BakedGoodUpdate (used when updating an existing baked good via PUT).
Both models enforce that required fields are provided and that pricing
and text fields meet the application's validation requirements.
"""

from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, Field, field_validator, model_validator


class BakedGoodBase(BaseModel):
    """
    Defines and validates the shared data for a baked good.
    """

    active: bool
    name: str
    description: str
    purchasing_cost: Decimal = Field(gt=0, decimal_places=2)
    retail_price: Decimal = Field(gt=0, decimal_places=2)
    vendor_id: int

    @field_validator("purchasing_cost", "retail_price")
    @classmethod
    def format_money(cls, value: Decimal) -> Decimal:
        """
        Ensures monetary values have exactly two decimal places.
        """
        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """
        Validates that the baked good name is properly formatted.
        """
        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("Name cannot be empty")

        if stripped_value != value:
            raise ValueError("Name cannot begin or end with a space")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        """
        Validates that the baked good description is not empty.
        """
        if not value.strip():
            raise ValueError("Description cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_retail_price(self):
        """
        Validates that the retail price is greater than the purchasing cost.
        """
        if self.retail_price <= self.purchasing_cost:
            raise ValueError(
                "Retail price must be greater than purchasing cost"
            )

        return self


class BakedGood(BakedGoodBase):
    """
    Pydantic model used to validate data when creating a new baked good.
    """


class BakedGoodUpdate(BakedGoodBase):
    """
    Pydantic model used to validate data when updating an existing baked
    good via PUT.
    """
