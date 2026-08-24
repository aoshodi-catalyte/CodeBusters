"""
Pydantic model for validating baked good data.

This module defines the BakedGood model, which validates baked good
information before it is stored in the database. It ensures that
required fields are provided and that pricing and text fields meet
the application's validation requirements.
"""

from pydantic import BaseModel, Field, field_validator, model_validator

class BakedGood(BaseModel):
    """
    Defines and validates the data for a baked good.

    Args:
        active: Indicates whether the baked good is currently active.
        name: The name of the baked good.
        description: A description of the baked good.
        purchasing_cost: The cost to purchase or produce the baked good.
            Must be greater than 0.
        retail_price: The price at which the baked good is sold.
            Must be greater than 0 and greater than the purchasing cost.
        vendor_id: The ID of the vendor associated with the baked good.

    Returns:
        A validated BakedGood object.
    """

    active: bool
    name: str
    description: str
    purchasing_cost: float = Field(gt=0)
    retail_price: float = Field(gt=0)
    vendor_id: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        """
        Validates that the baked good name is properly formatted.

        Args:
            value: The name of the baked good being validated.

        Raises:
            ValueError: If the name is empty, contains leading or trailing
                whitespace, or is not in title case.

        Returns:
            The validated baked good name.
        """

        if not value.strip():
            raise ValueError("Name cannot be empty")

        if value != value.strip():
            raise ValueError("Name cannot begin or end with a space")
            
        if value != value.title():
            raise ValueError("Name must be in title case")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        """
        Validates that the baked good description is not empty.

        Args:
            value: The description of the baked good being validated.

        Raises:
            ValueError: If the description is empty or contains only whitespace.

        Returns:
            The validated baked good description.
        """

        if not value.strip():
            raise ValueError("Description cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_retail_price(self):
        """
        Validates that the retail price is greater than the purchasing cost.

        Args:
            self: The BakedGood object containing the purchasing cost
                and retail price.

        Raises:
            ValueError: If the retail price is less than or equal to
                the purchasing cost.

        Returns:
            The validated BakedGood object.
        """
        if self.retail_price <= self.purchasing_cost:
            raise ValueError("Retail price must be greater than purchasing cost")
        return self
