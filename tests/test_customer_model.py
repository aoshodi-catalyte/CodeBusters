import pytest
from pydantic import ValidationError

from customer.customer_model import Customer 


def test_customer_valid():
    customer = Customer(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.first_name == "John"
    assert customer.last_name == "Smith"
    assert customer.email == "john@example.com"
    assert customer.phone_number == "312-555-1234"
    assert customer.loyalty_points == 0
    assert customer.active is True
    assert customer.id is None


def test_last_name_is_optional():
    customer = Customer(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.last_name is None


def test_loyalty_points_default_to_zero():
    customer = Customer(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    assert customer.loyalty_points == 0


def test_loyalty_points_cannot_be_negative():
    with pytest.raises(ValidationError):
        Customer(
            first_name="John",
            email="john@example.com",
            phone_number="312-555-1234",
            loyalty_points=-1
        )


def test_invalid_email():
    with pytest.raises(ValidationError):
        Customer(
            first_name="John",
            email="not-an-email",
            phone_number="312-555-1234"
        )


def test_invalid_phone_number():
    with pytest.raises(ValidationError):
        Customer(
            first_name="John",
            email="john@example.com",
            phone_number="3125551234"
        )


def test_first_name_cannot_be_empty():
    with pytest.raises(ValidationError):
        Customer(
            first_name="",
            email="john@example.com",
            phone_number="312-555-1234"
        )


def test_first_name_max_length():
    with pytest.raises(ValidationError):
        Customer(
            first_name="A" * 51,
            email="john@example.com",
            phone_number="312-555-1234"
        )