import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from routers.customer_router import router


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
    assert result["phone_number"] == "555-123-4567"
    assert result["active"] is True
    assert result["loyalty_points"] == 100
    assert result["id"] is not None


def test_get_customers(client):
    """
    Verifies that the API returns all customers.

    Phone numbers should be returned in xxx-xxx-xxxx format.
    """

    customer_one = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551111111",
        "active": True,
        "loyalty_points": 100
    }

    customer_two = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone_number": "5552222222",
        "active": True,
        "loyalty_points": 200
    }

    client.post(
        "/customers",
        json=customer_one
    )

    client.post(
        "/customers",
        json=customer_two
    )

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
    Verifies that the API returns an empty list with HTTP 200 when
    no customers exist.
    """

    response = client.get("/customers")

    assert response.status_code == 200
    assert response.json() == []


def test_get_customer_by_id(client):
    """
    Verifies that the API returns a single customer when a valid
    customer ID is provided.
    """

    customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 100
    }

    create_response = client.post(
        "/customers",
        json=customer
    )

    assert create_response.status_code == 201

    created_customer = create_response.json()
    customer_id = created_customer["id"]

    response = client.get(
        f"/customers/{customer_id}"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == customer_id
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["email"] == "john@example.com"
    assert result["phone_number"] == "555-123-4567"
    assert result["active"] is True
    assert result["loyalty_points"] == 100


def test_get_customer_by_nonexistent_id(client):
    """
    Verifies that requesting a customer with an ID that does not exist
    returns HTTP 404.
    """

    response = client.get(
        "/customers/999"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Customer with ID 999 was not found."
    }


def test_create_customer_with_duplicate_email(client):
    """
    Verifies that creating a customer with an existing email returns
    HTTP 409 with the correct error message.
    """

    first_customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 100
    }

    second_customer = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "john@example.com",
        "phone_number": "5559876543",
        "active": True,
        "loyalty_points": 50
    }

    first_response = client.post(
        "/customers",
        json=first_customer
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/customers",
        json=second_customer
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "A customer with the email 'john@example.com' "
                   "already exists."
    }


def test_create_customer_with_duplicate_phone_number(client):
    """
    Verifies that creating a customer with an existing phone number
    returns HTTP 409 with the correct error message.
    """

    first_customer = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 100
    }

    second_customer = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone_number": "5551234567",
        "active": True,
        "loyalty_points": 50
    }

    first_response = client.post(
        "/customers",
        json=first_customer
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/customers",
        json=second_customer
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "A customer with the phone number '5551234567' "
                   "already exists."
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
    