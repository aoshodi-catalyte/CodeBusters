from pydantic import BaseModel, EmailStr, Field, ConfigDict

class Customer(BaseModel):
    """
    Pydantic model used to validate Customer API data.

    Validates customer names, email format, phone number format,
    and loyalty point values before data is processed by the API.
    """

    # Allows Pydantic to create this model from SQLAlchemy objects.
    model_config = ConfigDict(from_attributes=True)

    # Generated automatically by the database when a customer is created.
    id: int | None = None

    # Indicates whether the customer is currently active.
    active: bool = True

    # Required first name with a maximum length of 50 characters.
    first_name: str = Field(min_length=1, max_length=50)

    # Optional last name with a maximum length of 50 characters.
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    # Must be provided and must follow a valid email format.
    # Uniqueness is enforced by the database.
    email: EmailStr

    # Must follow the xxx-xxx-xxxx format.
    # Uniqueness is enforced by the database.
    phone_number: str = Field(
        pattern=r"^\d{3}-\d{3}-\d{4}$"
    )

    # New customers start with zero loyalty points.
    # Loyalty points cannot be negative.
    loyalty_points: int = Field(default=0, ge=0)

