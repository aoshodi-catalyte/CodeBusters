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


def test_update_customer(client):
    """
    Verifies that a customer can be updated through the API and the
    updated entity is returned.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 100
        }
    )

    customer_id = create_response.json()["id"]

    update_payload = {
        "active": False,
        "first_name": "Johnny",
        "last_name": "Doeson",
        "email": "johnny@example.com",
        "phone_number": "5559998888",
        "loyalty_points": 300
    }

    response = client.put(
        f"/customers/{customer_id}",
        json=update_payload
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == customer_id
    assert result["active"] is False
    assert result["first_name"] == "Johnny"
    assert result["last_name"] == "Doeson"
    assert result["email"] == "johnny@example.com"
    assert result["phone_number"] == "555-999-8888"
    assert result["loyalty_points"] == 300


def test_update_customer_persists_change(client):
    """
    Verifies that an update is actually persisted and reflected on a
    subsequent GET request.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone_number": "5551112222",
            "active": True,
            "loyalty_points": 50
        }
    )

    customer_id = create_response.json()["id"]

    client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "first_name": "Janet",
            "last_name": "Smith",
            "email": "janet@example.com",
            "phone_number": "5551112222",
            "loyalty_points": 75
        }
    )

    get_response = client.get(f"/customers/{customer_id}")

    assert get_response.status_code == 200
    assert get_response.json()["first_name"] == "Janet"
    assert get_response.json()["loyalty_points"] == 75


def test_update_customer_with_nonexistent_id(client):
    """
    Verifies that updating a customer with an ID that does not exist
    returns HTTP 404.
    """

    update_payload = {
        "active": True,
        "first_name": "John",
        "email": "john@example.com",
        "phone_number": "5551234567",
        "loyalty_points": 0
    }

    response = client.put(
        "/customers/999",
        json=update_payload
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Customer with ID 999 was not found."
    }


def test_update_customer_with_duplicate_email(client):
    """
    Verifies that updating a customer to use another customer's email
    returns HTTP 409.
    """

    client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551111111",
            "active": True,
            "loyalty_points": 0
        }
    )

    second_response = client.post(
        "/customers",
        json={
            "first_name": "Jane",
            "email": "jane@example.com",
            "phone_number": "5552222222",
            "active": True,
            "loyalty_points": 0
        }
    )

    second_customer_id = second_response.json()["id"]

    response = client.put(
        f"/customers/{second_customer_id}",
        json={
            "active": True,
            "first_name": "Jane",
            "email": "john@example.com",
            "phone_number": "5552222222",
            "loyalty_points": 0
        }
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "A customer with the email 'john@example.com' "
                   "already exists."
    }


def test_update_customer_with_duplicate_phone_number(client):
    """
    Verifies that updating a customer to use another customer's phone
    number returns HTTP 409.
    """

    client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551111111",
            "active": True,
            "loyalty_points": 0
        }
    )

    second_response = client.post(
        "/customers",
        json={
            "first_name": "Jane",
            "email": "jane@example.com",
            "phone_number": "5552222222",
            "active": True,
            "loyalty_points": 0
        }
    )

    second_customer_id = second_response.json()["id"]

    response = client.put(
        f"/customers/{second_customer_id}",
        json={
            "active": True,
            "first_name": "Jane",
            "email": "jane@example.com",
            "phone_number": "5551111111",
            "loyalty_points": 0
        }
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail": "A customer with the phone number '5551111111' "
                   "already exists."
    }


def test_update_customer_allows_keeping_own_email_and_phone(client):
    """
    Verifies that a customer can be updated without changing their
    email or phone number.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 0
        }
    )

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "first_name": "Jonathan",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "loyalty_points": 10
        }
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Jonathan"
    assert response.json()["loyalty_points"] == 10


def test_update_customer_with_invalid_phone_number(client):
    """
    Verifies that the API rejects an update payload with a malformed
    phone number.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 0
        }
    )

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "555-123-456",
            "loyalty_points": 0
        }
    )

    assert response.status_code == 422


def test_update_customer_with_invalid_email(client):
    """
    Verifies that the API rejects an update payload with a malformed
    email address.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 0
        }
    )

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "first_name": "John",
            "email": "not-an-email",
            "phone_number": "5551234567",
            "loyalty_points": 0
        }
    )

    assert response.status_code == 422


def test_update_customer_with_negative_loyalty_points(client):
    """
    Verifies that the API rejects an update payload with negative
    loyalty points.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 0
        }
    )

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "loyalty_points": -5
        }
    )

    assert response.status_code == 422


def test_update_customer_missing_required_field(client):
    """
    Verifies that the API rejects an update payload missing a
    required field.
    """

    create_response = client.post(
        "/customers",
        json={
            "first_name": "John",
            "email": "john@example.com",
            "phone_number": "5551234567",
            "active": True,
            "loyalty_points": 0
        }
    )

    customer_id = create_response.json()["id"]

    response = client.put(
        f"/customers/{customer_id}",
        json={
            "active": True,
            "email": "john@example.com",
            "phone_number": "5551234567",
            "loyalty_points": 0
        }
    )

    assert response.status_code == 422
