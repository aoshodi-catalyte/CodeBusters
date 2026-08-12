import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base
from src.main import app
from src.database import get_db
from src.customer.customer_schema import CustomerSchema


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


@pytest.fixture
def override_get_db(db):
    """
    Provides the test database session to FastAPI
    instead of the application's real database.
    """

    def _override_get_db():
        yield db

    return _override_get_db


@pytest.fixture
def client(db, override_get_db):
    """
    Creates a FastAPI test client that uses
    the isolated test database.
    """

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_create_customer(client):
    """
    Tests that POST /customers creates a new customer
    and returns HTTP 201.
    """

    response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "phone_number": "312-555-1234"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["first_name"] == "John"
    assert data["last_name"] == "Smith"
    assert data["email"] == "john@example.com"
    assert data["phone_number"] == "312-555-1234"
    assert data["active"] is True
    assert data["loyalty_points"] == 0


def test_create_customer_duplicate_email(client):
    """
    Tests that creating a customer with an existing
    email returns HTTP 409.
    """

    customer = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "phone_number": "312-555-1234"
    }

    first_response = client.post(
        "/customers",
        json=customer
    )

    assert first_response.status_code == 201

    duplicate_email = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "773-555-1234"
    }

    second_response = client.post(
        "/customers",
        json=duplicate_email
    )

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "A customer with this email or phone number already exists."
    )


def test_create_customer_duplicate_phone(client):
    """
    Tests that creating a customer with an existing
    phone number returns HTTP 409.
    """

    customer = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "phone_number": "312-555-1234"
    }

    first_response = client.post(
        "/customers",
        json=customer
    )

    assert first_response.status_code == 201

    duplicate_phone = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "phone_number": "312-555-1234"
    }

    second_response = client.post(
        "/customers",
        json=duplicate_phone
    )

    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "A customer with this email or phone number already exists."
    )


def test_get_customers(client, db):
    """
    Tests that GET /customers returns all customers
    and HTTP 200.
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

    response = client.get("/customers")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["first_name"] == "John"
    assert data[1]["first_name"] == "Jane"


def test_get_customers_when_empty(client):
    """
    Tests that GET /customers returns HTTP 404
    when no customers exist.
    """

    response = client.get("/customers")

    assert response.status_code == 404

    assert response.json()["detail"] == "No customers found."

def test_create_customer_unexpected_error(client, monkeypatch):
    """
    Tests that an unexpected repository error returns HTTP 500.
    """

    def mock_create_customer(db, customer):
        raise Exception("Database failure")

    monkeypatch.setattr(
        "src.customer.customer_router.customer_repository.create_customer",
        mock_create_customer
    )

    response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john@example.com",
            "phone_number": "312-555-1234"
        }
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "An unexpected error occurred while creating the customer."
    )

def test_get_customers_unexpected_error(client, monkeypatch):
    """
    Tests that an unexpected repository error returns HTTP 500.
    """

    def mock_get_customers(db):
        raise Exception("Database failure")

    monkeypatch.setattr(
        "src.customer.customer_router.customer_repository.get_customers",
        mock_get_customers
    )

    response = client.get("/customers")

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "An unexpected error occurred while retrieving customers."
    )

def test_root(client):
    """
    Tests that the API root endpoint is available.
    """

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Customer API is running"
    }