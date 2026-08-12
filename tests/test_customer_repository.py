import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from customer.customer_model import Customer
from customer.customer_schema import CustomerSchema
from customer.customer_repository import CustomerRepository


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
    Creates a fresh test database for each test.
    """
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_customer(db):
    """
    Verifies that a customer can be created successfully.
    """
    customer = Customer(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="555-123-4567",
        active=True,
        loyalty_points=100
    )

    repo = CustomerRepository(db)

    result = repo.create_customer(customer)

    assert result.id is not None
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone_number == "555-123-4567"
    assert result.active is True
    assert result.loyalty_points == 100


def test_create_customer_persists_to_database(db):
    """
    Verifies that the created customer is actually persisted.
    """
    customer = Customer(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone_number="555-987-6543",
        active=True,
        loyalty_points=250
    )

    repo = CustomerRepository(db)

    created_customer = repo.create_customer(customer)

    saved_customer = (
        db.query(CustomerSchema)
        .filter(CustomerSchema.id == created_customer.id)
        .first()
    )

    assert saved_customer is not None
    assert saved_customer.first_name == "Jane"
    assert saved_customer.last_name == "Smith"
    assert saved_customer.email == "jane.smith@example.com"
    assert saved_customer.phone_number == "555-987-6543"
    assert saved_customer.active is True
    assert saved_customer.loyalty_points == 250


def test_create_customer_generates_id(db):
    """
    Verifies that the database generates an ID for a new customer.
    """
    customer = Customer(
        first_name="Michael",
        last_name="Jordan",
        email="michael@example.com",
        phone_number="555-111-2222",
        active=True,
        loyalty_points=500
    )

    repo = CustomerRepository(db)

    result = repo.create_customer(customer)

    assert result.id is not None


def test_get_customers_returns_all_customers(db):
    """
    Verifies that get_customers returns all customers.
    """
    customer1 = CustomerSchema(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone_number="555-111-1111",
        active=True,
        loyalty_points=100
    )

    customer2 = CustomerSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="555-222-2222",
        active=True,
        loyalty_points=200
    )

    db.add(customer1)
    db.add(customer2)
    db.commit()

    repo = CustomerRepository(db)

    result = repo.get_customers()

    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"


def test_get_customers_returns_empty_list(db):
    """
    Verifies that get_customers returns an empty list when
    no customers exist.
    """
    repo = CustomerRepository(db)

    result = repo.get_customers()

    assert result == []