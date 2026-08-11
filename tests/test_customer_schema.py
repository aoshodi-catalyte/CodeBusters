import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError

from database import Base
from customer.customer_schema import CustomerSchema


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
    Creates a fresh database before each test
    and removes it after the test completes.
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
    Tests that a customer can be created and persisted
    in the database.
    """

    customer = CustomerSchema(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    assert customer.id is not None
    assert customer.first_name == "John"
    assert customer.last_name == "Smith"
    assert customer.email == "john@example.com"
    assert customer.phone_number == "312-555-1234"
    assert customer.loyalty_points == 0
    assert customer.active is True
    assert customer.created_at is not None


def test_email_must_be_unique(db):
    """
    Tests that a customer's email must be unique.
    """

    customer1 = CustomerSchema(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    customer2 = CustomerSchema(
        first_name="Jane",
        email="john@example.com",
        phone_number="773-555-1234"
    )

    db.add(customer1)
    db.commit()

    db.add(customer2)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_phone_number_must_be_unique(db):
    """
    Tests that a customer's phone number must be unique.
    """

    customer1 = CustomerSchema(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    customer2 = CustomerSchema(
        first_name="Jane",
        email="jane@example.com",
        phone_number="312-555-1234"
    )

    db.add(customer1)
    db.commit()

    db.add(customer2)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_last_name_is_optional(db):
    """
    Tests that a customer's last name is optional.
    """

    customer = CustomerSchema(
        first_name="John",
        email="john@example.com",
        phone_number="312-555-1234"
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    assert customer.last_name is None