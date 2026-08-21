import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from customer.customer_model import CustomerCreate
from customer.customer_repository import CustomerRepository
from customer.customer_schema import CustomerSchema


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
    """Create a fresh in-memory database for each test."""

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repository(db):
    """Create a CustomerRepository using the test database session."""

    return CustomerRepository(db)


def test_create_customer(repository):
    """Repository should create and persist a customer."""

    customer = CustomerCreate(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="312-555-1234",
        active=True,
        loyalty_points=100
    )

    created_customer = repository.create_customer(customer)

    assert created_customer.id is not None
    assert created_customer.first_name == "John"
    assert created_customer.last_name == "Smith"
    assert created_customer.email == "john@example.com"
    assert created_customer.phone_number == "3125551234"
    assert created_customer.active is True
    assert created_customer.loyalty_points == 100


def test_create_customer_persists_to_database(repository, db):
    """Created customer should actually be persisted in the database."""

    customer = CustomerCreate(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="773-555-1234"
    )

    created_customer = repository.create_customer(customer)

    stored_customer = (
        db.query(CustomerSchema)
        .filter_by(id=created_customer.id)
        .first()
    )

    assert stored_customer is not None
    assert stored_customer.phone_number == "7735551234"


def test_get_customers(repository, db):
    """Repository should return all customers."""

    customer_one = CustomerSchema(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
        active=True,
        loyalty_points=100
    )

    customer_two = CustomerSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="7735551234",
        active=True,
        loyalty_points=50
    )

    db.add_all([customer_one, customer_two])
    db.commit()

    customers = repository.get_customers()

    assert len(customers) == 2
    assert customers[0].first_name == "John"
    assert customers[1].first_name == "Jane"


def test_get_customers_returns_empty_list(repository):
    """Repository should return an empty list when no customers exist."""

    customers = repository.get_customers()

    assert customers == []


def test_get_customer_by_email(repository, db):
    """Repository should return a customer matching the email."""

    customer = CustomerSchema(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
        active=True,
        loyalty_points=100
    )

    db.add(customer)
    db.commit()

    found_customer = repository.get_customer_by_email(
        "john@example.com"
    )

    assert found_customer is not None
    assert found_customer.id == customer.id
    assert found_customer.email == "john@example.com"


def test_get_customer_by_email_returns_none_when_not_found(
    repository
):
    """Repository should return None when the email does not exist."""

    found_customer = repository.get_customer_by_email(
        "missing@example.com"
    )

    assert found_customer is None


def test_get_customer_by_phone(repository, db):
    """Repository should return a customer matching the phone number."""

    customer = CustomerSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="7735551234",
        active=True,
        loyalty_points=50
    )

    db.add(customer)
    db.commit()

    found_customer = repository.get_customer_by_phone(
        "7735551234"
    )

    assert found_customer is not None
    assert found_customer.id == customer.id
    assert found_customer.phone_number == "7735551234"


def test_get_customer_by_phone_returns_none_when_not_found(
    repository
):
    """Repository should return None when the phone number does not exist."""

    found_customer = repository.get_customer_by_phone(
        "5559999999"
    )

    assert found_customer is None