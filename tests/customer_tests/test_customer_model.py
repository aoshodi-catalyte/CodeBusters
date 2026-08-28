import pytest
from pydantic import ValidationError

from customer.customer_model import CustomerCreate, CustomerResponse, CustomerUpdate 


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
    assert customer.email == "john.smith@example.com"
    assert customer.phone_number == "3125551234"
    assert customer.active is True
    assert customer.loyalty_points == 100


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


def test_first_name_removes_leading_whitespace():
    """Leading whitespace is removed from the first name."""

    customer = CustomerCreate(
        first_name="   Billy",
        last_name="Smith",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.first_name == "Billy"


def test_first_name_removes_trailing_whitespace():
    """Trailing whitespace is removed from the first name."""

    customer = CustomerCreate(
        first_name="Billy   ",
        last_name="Smith",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.first_name == "Billy"


def test_first_name_converts_multiple_spaces_to_single_space():
    """Multiple spaces between first-name words are converted to one space."""

    customer = CustomerCreate(
        first_name="Billy    Bob",
        last_name="Smith",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.first_name == "Billy Bob"


def test_last_name_removes_leading_whitespace():
    """Leading whitespace is removed from the last name."""

    customer = CustomerCreate(
        first_name="Billy",
        last_name="   Smith",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.last_name == "Smith"


def test_last_name_removes_trailing_whitespace():
    """Trailing whitespace is removed from the last name."""

    customer = CustomerCreate(
        first_name="Billy",
        last_name="Smith   ",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.last_name == "Smith"


def test_last_name_converts_multiple_spaces_to_single_space():
    """Multiple spaces between last-name words are converted to one space."""

    customer = CustomerCreate(
        first_name="Billy",
        last_name="Van    Buren",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.last_name == "Van Buren"


def test_name_normalization_handles_multiple_whitespace_characters():
    """Tabs and newlines are normalized to a single space."""

    customer = CustomerCreate(
        first_name="Billy\t\nBob",
        last_name="Van\t\nBuren",
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.first_name == "Billy Bob"
    assert customer.last_name == "Van Buren"


def test_last_name_can_be_none():
    """None remains None for the optional last name."""

    customer = CustomerCreate(
        first_name="Billy",
        last_name=None,
        email="billy@example.com",
        phone_number="3125551234",
    )

    assert customer.last_name is None


def test_valid_customer_update():
    """CustomerUpdate should accept valid customer data."""

    customer = CustomerUpdate(
        active=True,
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        phone_number="312-555-1234",
        loyalty_points=150
    )

    assert customer.active is True
    assert customer.first_name == "John"
    assert customer.last_name == "Smith"
    assert customer.email == "john.smith@example.com"
    assert customer.phone_number == "3125551234"
    assert customer.loyalty_points == 150


def test_customer_update_phone_number_normalizes_formatting():
    """CustomerUpdate should remove formatting characters from phone numbers."""

    customer = CustomerUpdate(
        active=True,
        first_name="John",
        email="john@example.com",
        phone_number="(312) 555-1234",
        loyalty_points=0
    )

    assert customer.phone_number == "3125551234"


def test_customer_update_phone_number_rejects_invalid_length():
    """CustomerUpdate should reject phone numbers that are not 10 digits."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="John",
            email="john@example.com",
            phone_number="312555123",
            loyalty_points=0
        )


def test_customer_update_rejects_invalid_email():
    """CustomerUpdate should reject an invalid email address."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="John",
            email="not-an-email",
            phone_number="3125551234",
            loyalty_points=0
        )


def test_customer_update_email_normalized_to_lowercase():
    """CustomerUpdate should normalize email addresses to lowercase."""

    customer = CustomerUpdate(
        active=True,
        first_name="John",
        email="JOHN@EXAMPLE.COM",
        phone_number="3125551234",
        loyalty_points=0
    )

    assert customer.email == "john@example.com"


def test_customer_update_rejects_empty_first_name():
    """CustomerUpdate should reject an empty first name."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="",
            email="john@example.com",
            phone_number="3125551234",
            loyalty_points=0
        )


def test_customer_update_rejects_first_name_too_long():
    """CustomerUpdate should reject a first name longer than 50 characters."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="A" * 51,
            email="john@example.com",
            phone_number="3125551234",
            loyalty_points=0
        )


def test_customer_update_last_name_can_be_none():
    """CustomerUpdate should allow the last name to be omitted."""

    customer = CustomerUpdate(
        active=True,
        first_name="John",
        email="john@example.com",
        phone_number="3125551234",
        loyalty_points=0
    )

    assert customer.last_name is None


def test_customer_update_rejects_negative_loyalty_points():
    """CustomerUpdate should reject negative loyalty points."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="John",
            email="john@example.com",
            phone_number="3125551234",
            loyalty_points=-1
        )


def test_customer_update_requires_active():
    """CustomerUpdate should require the active field to be explicitly provided."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            first_name="John",
            email="john@example.com",
            phone_number="3125551234",
            loyalty_points=0
        )


def test_customer_update_requires_loyalty_points():
    """CustomerUpdate should require loyalty_points to be explicitly provided."""

    with pytest.raises(ValidationError):
        CustomerUpdate(
            active=True,
            first_name="John",
            email="john@example.com",
            phone_number="3125551234"
        )


def test_customer_update_name_normalization_collapses_whitespace():
    """CustomerUpdate should normalize whitespace in names."""

    customer = CustomerUpdate(
        active=True,
        first_name="Billy    Bob",
        last_name="Van    Buren",
        email="billy@example.com",
        phone_number="3125551234",
        loyalty_points=0
    )

    assert customer.first_name == "Billy Bob"
    assert customer.last_name == "Van Buren"

    