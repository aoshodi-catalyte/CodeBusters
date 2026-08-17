import pytest
from pydantic import ValidationError

from customer.customer_model import CustomerCreate, CustomerResponse


def test_valid_customer_create():
    """CustomerCreate should accept valid customer data."""

    customer = CustomerCreate(
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        phone_number="312-555-1234",
        active=True,
        loyalty_points=100
    )

    assert customer.first_name == "John"
    assert customer.last_name == "Smith"
    assert str(customer.email) == "john.smith@example.com"
    assert customer.phone_number == "3125551234"
    assert customer.active is True
    assert customer.loyalty_points == 100


def test_first_name_strips_surrounding_whitespace():
    """CustomerCreate should remove surrounding whitespace from first names."""

    customer = CustomerCreate(
        first_name="  Adeyemi  ",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.first_name == "Adeyemi"


def test_last_name_strips_surrounding_whitespace():
    """CustomerCreate should remove surrounding whitespace from last names."""

    customer = CustomerCreate(
        first_name="John",
        last_name="  Smith  ",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.last_name == "Smith"


def test_first_name_rejects_whitespace_only():
    """CustomerCreate should reject a whitespace-only first name."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="   ",
            email="john@example.com",
            phone_number="312-555-1234"
        )


def test_last_name_rejects_whitespace_only():
    """CustomerCreate should reject a whitespace-only last name."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            last_name="   ",
            email="john@example.com",
            phone_number="312-555-1234"
        )


def test_phone_number_normalizes_hyphens():
    """CustomerCreate should remove hyphens from phone numbers."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.phone_number == "3125551234"


def test_phone_number_normalizes_parentheses_and_spaces():
    """CustomerCreate should remove common phone formatting characters."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="(312) 555-1234"
    )

    assert customer.phone_number == "3125551234"


def test_phone_number_accepts_digits_only():
    """CustomerCreate should accept an already-normalized phone number."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="3125551234"
    )

    assert customer.phone_number == "3125551234"


def test_phone_number_rejects_invalid_characters():
    """CustomerCreate should reject unexpected characters in phone numbers."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="abc312-555-1234"
        )


def test_phone_number_rejects_invalid_length():
    """CustomerCreate should reject phone numbers that are not 10 digits."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="312555123"
        )


def test_phone_number_rejects_too_many_digits():
    """CustomerCreate should reject phone numbers containing more than 10 digits."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="31255512345"
        )


def test_invalid_email():
    """CustomerCreate should reject an invalid email address."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            email="not-an-email",
            phone_number="3125551234"
        )


def test_email_is_normalized():
    """CustomerCreate should strip whitespace and lowercase email addresses."""

    customer = CustomerCreate(
        first_name="John",
        email="  TEST@EXAMPLE.COM  ",
        phone_number="3125551234"
    )

    assert str(customer.email) == "test@example.com"


def test_empty_first_name():
    """CustomerCreate should reject an empty first name."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="",
            email="john@example.com",
            phone_number="3125551234"
        )


def test_first_name_too_long():
    """CustomerCreate should reject a first name longer than 50 characters."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="A" * 51,
            email="john@example.com",
            phone_number="3125551234"
        )


def test_last_name_is_optional():
    """CustomerCreate should allow the last name to be omitted."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="3125551234"
    )

    assert customer.last_name is None


def test_default_active():
    """CustomerCreate should default active to True."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="3125551234"
    )

    assert customer.active is True


def test_default_loyalty_points():
    """CustomerCreate should default loyalty points to zero."""

    customer = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="3125551234"
    )

    assert customer.loyalty_points == 0


def test_negative_loyalty_points():
    """CustomerCreate should reject negative loyalty points."""

    with pytest.raises(ValidationError):
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="3125551234",
            loyalty_points=-1
        )


def test_customer_response_formats_phone_number():
    """CustomerResponse should format a stored phone number for API responses."""

    customer = CustomerResponse(
        id=1,
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
        active=True,
        loyalty_points=100
    )

    response = customer.model_dump()

    assert response["phone_number"] == "312-555-1234"


def test_customer_response_from_attributes():
    """CustomerResponse should support SQLAlchemy-style objects."""

    class CustomerObject:
        id = 1
        first_name = "John"
        last_name = "Smith"
        email = "john@example.com"
        phone_number = "3125551234"
        active = True
        loyalty_points = 100

    customer = CustomerResponse.model_validate(CustomerObject())

    assert customer.id == 1
    assert customer.first_name == "John"
    assert customer.phone_number == "3125551234"

    response = customer.model_dump()

    assert response["phone_number"] == "312-555-1234"