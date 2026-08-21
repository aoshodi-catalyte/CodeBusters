import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from customer.customer_router import router


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

app = FastAPI()
app.include_router(router)


@pytest.fixture
def client():
    """
    Creates a test client using a temporary in-memory database.
    """

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_customer(client):
    """
    Verifies that a customer can be created through the API.

    The phone number is submitted without formatting and should be
    returned in xxx-xxx-xxxx format by the API.
    """

    customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 100
    }

    response = client.post(
        "/customers",
        json=customer
    )

    assert response.status_code == 201

    result = response.json()

    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["email"] == "john.doe@example.com"

    # API response should format the phone number.
    assert result["phone_number"] == "555-123-4567"

    assert result["active"] is True
    assert result["loyalty_points"] == 100
    assert result["id"] is not None


def test_get_customers(client):
    """
    Verifies that the API returns all customers.

    Phone numbers should be returned in xxx-xxx-xxxx format.
    """

    customer1 = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551111111",
        "active": True,
        "loyalty_points": 100
    }

    customer2 = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone_number": "5552222222",
        "active": True,
        "loyalty_points": 200
    }

    client.post("/customers", json=customer1)
    client.post("/customers", json=customer2)

    response = client.get("/customers")

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 2

    assert customers[0]["first_name"] == "John"
    assert customers[0]["phone_number"] == "555-111-1111"

    assert customers[1]["first_name"] == "Jane"
    assert customers[1]["phone_number"] == "555-222-2222"


def test_get_customers_when_empty(client):
    """
    Verifies that the API returns 404 when no customers exist.
    """

    response = client.get("/customers")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "No customers found."
    }


def test_create_duplicate_customer(client):
    """
    Verifies that creating a customer with an existing email
    or phone number returns HTTP 409.
    """

    customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 100
    }

    first_response = client.post(
        "/customers",
        json=customer
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/customers",
        json=customer
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": (
            "A customer with this email or phone number "
            "already exists."
        )
    }


def test_create_customer_with_invalid_phone_number(client):
    """
    Verifies that the API rejects phone numbers that do not contain
    exactly 10 digits.
    """

    customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "555-123-456",
        "active": True,
        "loyalty_points": 100
    }

    response = client.post(
        "/customers",
        json=customer
    )

    assert response.status_code == 422