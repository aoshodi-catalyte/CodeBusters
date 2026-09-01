import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from exceptions.customer_exceptions import (
    CustomerEmailAlreadyExistsError,
    CustomerNotFoundError,
    CustomerPhoneAlreadyExistsError,
)
from customer.customer_model import CustomerCreate, CustomerUpdate
from repositories.customer_repository import CustomerRepository
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


def test_create_customer_with_duplicate_email_raises_error(
    repository
):
    """Repository should raise when the email already exists."""

    first_customer = CustomerCreate(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
    )

    repository.create_customer(first_customer)

    second_customer = CustomerCreate(
        first_name="Jane",
        last_name="Doe",
        email="john@example.com",
        phone_number="7735551234",
    )

    with pytest.raises(CustomerEmailAlreadyExistsError):
        repository.create_customer(second_customer)


def test_create_customer_with_duplicate_phone_raises_error(
    repository
):
    """Repository should raise when the phone number already exists."""

    first_customer = CustomerCreate(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
    )

    repository.create_customer(first_customer)

    second_customer = CustomerCreate(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="3125551234",
    )

    with pytest.raises(CustomerPhoneAlreadyExistsError):
        repository.create_customer(second_customer)


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


def test_get_customer_by_id(repository, db):
    """Repository should return a customer matching the ID."""

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

    found_customer = repository.get_customer_by_id(
        customer.id
    )

    assert found_customer is not None
    assert found_customer.id == customer.id
    assert found_customer.first_name == "John"
    assert found_customer.email == "john@example.com"


def test_get_customer_by_id_raises_when_not_found(repository):
    """Repository should raise CustomerNotFoundError when the ID does not exist."""

    with pytest.raises(CustomerNotFoundError):
        repository.get_customer_by_id(999)


def test_update_customer(repository):
    """Repository should update and persist an existing customer's fields."""

    original = CustomerCreate(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="3125551234",
        active=True,
        loyalty_points=100
    )

    created_customer = repository.create_customer(original)

    updated_data = CustomerUpdate(
        active=False,
        first_name="Johnny",
        last_name="Smithson",
        email="johnny@example.com",
        phone_number="7735559999",
        loyalty_points=250
    )

    updated_customer = repository.update_customer(
        created_customer.id,
        updated_data
    )

    assert updated_customer.id == created_customer.id
    assert updated_customer.active is False
    assert updated_customer.first_name == "Johnny"
    assert updated_customer.last_name == "Smithson"
    assert updated_customer.email == "johnny@example.com"
    assert updated_customer.phone_number == "7735559999"
    assert updated_customer.loyalty_points == 250


def test_update_customer_persists_to_database(repository, db):
    """Updated customer fields should actually be persisted in the database."""

    original = CustomerCreate(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone_number="3125551234"
    )

    created_customer = repository.create_customer(original)

    updated_data = CustomerUpdate(
        active=True,
        first_name="Janet",
        last_name="Doe",
        email="janet@example.com",
        phone_number="3125551234",
        loyalty_points=500
    )

    repository.update_customer(created_customer.id, updated_data)

    stored_customer = (
        db.query(CustomerSchema)
        .filter_by(id=created_customer.id)
        .first()
    )

    assert stored_customer is not None
    assert stored_customer.first_name == "Janet"
    assert stored_customer.email == "janet@example.com"
    assert stored_customer.loyalty_points == 500


def test_update_customer_raises_when_id_not_found(repository):
    """Repository should raise CustomerNotFoundError for a nonexistent ID."""

    updated_data = CustomerUpdate(
        active=True,
        first_name="John",
        email="john@example.com",
        phone_number="3125551234",
        loyalty_points=0
    )

    with pytest.raises(CustomerNotFoundError):
        repository.update_customer(999, updated_data)


def test_update_customer_allows_unchanged_email(repository):
    """Repository should allow a customer to keep their own existing email."""

    original = CustomerCreate(
        first_name="John",
        email="john@example.com",
        phone_number="3125551234"
    )

    created_customer = repository.create_customer(original)

    updated_data = CustomerUpdate(
        active=True,
        first_name="Johnny",
        email="john@example.com",
        phone_number="3125551234",
        loyalty_points=0
    )

    updated_customer = repository.update_customer(
        created_customer.id,
        updated_data
    )

    assert updated_customer.email == "john@example.com"
    assert updated_customer.first_name == "Johnny"


def test_update_customer_raises_when_email_belongs_to_another_customer(
    repository
):
    """Repository should raise when the new email belongs to a different customer."""

    first_customer = repository.create_customer(
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="3125551234"
        )
    )

    second_customer = repository.create_customer(
        CustomerCreate(
            first_name="Jane",
            email="jane@example.com",
            phone_number="7735551234"
        )
    )

    updated_data = CustomerUpdate(
        active=True,
        first_name="Jane",
        email="john@example.com",
        phone_number="7735551234",
        loyalty_points=0
    )

    with pytest.raises(CustomerEmailAlreadyExistsError):
        repository.update_customer(second_customer.id, updated_data)


def test_update_customer_raises_when_phone_belongs_to_another_customer(
    repository
):
    """Repository should raise when the new phone belongs to a different customer."""

    first_customer = repository.create_customer(
        CustomerCreate(
            first_name="John",
            email="john@example.com",
            phone_number="3125551234"
        )
    )

    second_customer = repository.create_customer(
        CustomerCreate(
            first_name="Jane",
            email="jane@example.com",
            phone_number="7735551234"
        )
    )

    updated_data = CustomerUpdate(
        active=True,
        first_name="Jane",
        email="jane@example.com",
        phone_number="3125551234",
        loyalty_points=0
    )

    with pytest.raises(CustomerPhoneAlreadyExistsError):
        repository.update_customer(second_customer.id, updated_data)
