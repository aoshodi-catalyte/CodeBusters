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
    def validate_name(cls, value):
        """
        Validates that the baked good name is not empty.

        Args:
            value: The name of the baked good being validated.

        Raises:
            ValueError: If the name is empty or contains only whitespace.

        Returns:
            The validated baked good name.
        """
        
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value


    @field_validator("description")
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

