import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base


# Separate SQLite database used only for tests.
TEST_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    """
    Creates a fresh test database before each test
    and removes it after the test completes.
    """

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


"""
Tests for the Customer repository layer.
"""

from customer.customer_schema import CustomerSchema
from customer.customer_repository import (
    create_customer,
    get_customers
)


def test_create_customer(db):
    """
    Tests that create_customer() persists a customer
    and generates an ID.
    """

    customer = CustomerSchema(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    result = create_customer(db, customer)

    assert result.id is not None
    assert result.first_name == "John"
    assert result.last_name == "Smith"
    assert result.email == "john@example.com"
    assert result.phone_number == "312-555-1234"
    assert result.active is True
    assert result.loyalty_points == 0
    assert result.created_at is not None


def test_get_customers(db):
    """
    Tests that get_customers() returns all customers
    currently stored in the database.
    """

    customer1 = CustomerSchema(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    customer2 = CustomerSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="773-555-1234"
    )

    db.add(customer1)
    db.add(customer2)
    db.commit()

    customers = get_customers(db)

    assert len(customers) == 2
    assert customers[0].first_name == "John"
    assert customers[1].first_name == "Jane"


def test_get_customers_returns_empty_list_when_no_customers(db):
    """
    Tests that get_customers() returns an empty list
    when no customers exist.
    """

    customers = get_customers(db)

    assert customers == []


