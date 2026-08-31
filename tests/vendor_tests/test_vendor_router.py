from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import models
from routers.vendor_router import router


@pytest.fixture
def client():
    """Create a FastAPI test client with an in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db():
        db = testing_session_local()

        try:
            yield db
        finally:
            db.close()

    test_app = FastAPI()
    test_app.include_router(router)
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def test_post_new_vendor(client):
    """Test creating a new vendor."""
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896",
    }

    response = client.post("/vendors", json=vendor_payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["active"] is True
    assert data["name"] == "Bob's Burgers"
    assert data["contact_name"] == "Bob Belcher"
    assert data["contact_role"] == "CEO"
    assert data["email"] == "bestburgers@burger.com"
    assert data["phone"] == "123-456-7896"


def test_post_duplicate_vendor_returns_409(client):
    """Test that creating a duplicate vendor returns HTTP 409."""
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896",
    }

    first_response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Vendor with email 'bestburgers@burger.com' already exists."
    )


def test_get_all_vendors_empty(client):
    """Test retrieving vendors when no vendors exist."""
    response = client.get("/vendors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_vendors(client):
    """Test retrieving all vendors."""
    vendor_payload_1 = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bob@burger.com",
        "phone": "1234567896",
    }

    vendor_payload_2 = {
        "active": True,
        "name": "Acme Supplies",
        "contact_name": "Wile E. Coyote",
        "contact_role": "Manager",
        "email": "acme@example.com",
        "phone": "9876543210",
    }

    client.post("/vendors", json=vendor_payload_1)
    client.post("/vendors", json=vendor_payload_2)

    response = client.get("/vendors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Bob's Burgers"
    assert data[1]["name"] == "Acme Supplies"


def test_get_all_vendors_returns_multiple_vendors(client):
    """Test retrieving multiple vendors."""
    vendors = [
        {
            "active": True,
            "name": "Bob's Burgers",
            "contact_name": "Bob Belcher",
            "contact_role": "CEO",
            "email": "bob@burger.com",
            "phone": "1234567896",
        },
        {
            "active": False,
            "name": "Acme Supplies",
            "contact_name": "Wile E. Coyote",
            "contact_role": "Manager",
            "email": "wile@acme.com",
            "phone": "9876543210",
        },
        {
            "active": True,
            "name": "Wayne Enterprises",
            "contact_name": "Bruce Wayne",
            "contact_role": "Owner",
            "email": "bruce@wayne.com",
            "phone": "5555555555",
        },
    ]

    for vendor in vendors:
        response = client.post("/vendors", json=vendor)
        assert response.status_code == 201

    response = client.get("/vendors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["name"] == "Bob's Burgers"
    assert data[1]["name"] == "Acme Supplies"
    assert data[2]["name"] == "Wayne Enterprises"


def test_get_all_vendors_response_contains_expected_fields(client):
    """Test that vendor responses contain expected fields."""
    vendor_payload = {
        "active": True,
        "name": "Stark Industries",
        "contact_name": "Tony Stark",
        "contact_role": "CEO",
        "email": "tony@stark.com",
        "phone": "5551234567",
    }

    response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert response.status_code == 201

    response = client.get("/vendors")

    assert response.status_code == 200

    vendor = response.json()[0]

    assert "id" in vendor
    assert "active" in vendor
    assert "name" in vendor
    assert "contact_name" in vendor
    assert "contact_role" in vendor
    assert "email" in vendor
    assert "phone" in vendor


def test_post_vendor_missing_required_field_returns_422(client):
    """Test that missing required fields return HTTP 422."""
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "phone": "1234567896",
    }

    response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert response.status_code == 422


def test_post_vendor_invalid_email_returns_422(client):
    """Test that an invalid email returns HTTP 422."""
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "not-an-email",
        "phone": "1234567896",
    }

    response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert response.status_code == 422

def test_get_vendor_by_id(client):
    """Test retrieving a vendor by ID."""
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bob@burger.com",
        "phone": "1234567896",
    }

    create_response = client.post(
        "/vendors",
        json=vendor_payload,
    )

    assert create_response.status_code == 201

    created_vendor = create_response.json()
    vendor_id = created_vendor["id"]

    response = client.get(f"/vendors/{vendor_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vendor_id
    assert data["active"] is True
    assert data["name"] == "Bob's Burgers"
    assert data["contact_name"] == "Bob Belcher"
    assert data["contact_role"] == "CEO"
    assert data["email"] == "bob@burger.com"
    assert data["phone"] == "123-456-7896"


def test_get_vendor_by_id_returns_correct_vendor(client):
    """Test retrieving the correct vendor when multiple vendors exist."""
    vendor_payload_1 = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bob@burger.com",
        "phone": "1234567896",
    }

    vendor_payload_2 = {
        "active": True,
        "name": "Acme Supplies",
        "contact_name": "Wile E. Coyote",
        "contact_role": "Manager",
        "email": "wile@acme.com",
        "phone": "9876543210",
    }

    first_response = client.post(
        "/vendors",
        json=vendor_payload_1,
    )

    second_response = client.post(
        "/vendors",
        json=vendor_payload_2,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    vendor_id = second_response.json()["id"]

    response = client.get(f"/vendors/{vendor_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vendor_id
    assert data["name"] == "Acme Supplies"
    assert data["email"] == "wile@acme.com"


def test_get_vendor_by_id_not_found_returns_404(client):
    """Test that a nonexistent vendor ID returns HTTP 404."""
    response = client.get("/vendors/999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Vendor with ID 999 was not found."
    )


def test_get_vendor_by_id_zero_returns_404(client):
    """Test that vendor ID zero returns HTTP 404."""
    response = client.get("/vendors/0")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Vendor with ID 0 was not found."
    )


def test_get_vendor_by_id_negative_id_returns_404(client):
    """Test that a negative vendor ID returns HTTP 404."""
    response = client.get("/vendors/-1")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Vendor with ID -1 was not found."
    )


def test_update_vendor_success(client):
    """Test that an existing vendor can be updated."""
    create_response = client.post(
        "/vendors",
        json={
            "active": True,
            "name": "Original Vendor",
            "contact_name": "John Smith",
            "contact_role": "Manager",
            "email": "original@example.com",
            "phone": "555-123-4567",
        },
    )

    vendor_id = create_response.json()["id"]

    response = client.put(
        f"/vendors/{vendor_id}",
        json={
            "active": False,
            "name": "Updated Vendor",
            "contact_name": "Jane Smith",
            "contact_role": "Owner",
            "email": "updated@example.com",
            "phone": "555-987-6543",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == vendor_id
    assert data["active"] is False
    assert data["name"] == "Updated Vendor"
    assert data["contact_name"] == "Jane Smith"
    assert data["contact_role"] == "Owner"
    assert data["email"] == "updated@example.com"
    assert data["phone"] == "555-987-6543"

def test_update_vendor_not_found(client):
    """Test that updating a nonexistent vendor returns 404."""
    response = client.put(
        "/vendors/999999",
        json={
            "active": True,
            "name": "Updated Vendor",
            "contact_name": "John Smith",
            "contact_role": "Manager",
            "email": "updated@example.com",
            "phone": "555-123-4567",
        },
    )

    assert response.status_code == 404


def test_update_vendor_invalid_email(client):
    """Test that invalid email data returns a validation error."""
    create_response = client.post(
        "/vendors",
        json={
            "active": True,
            "name": "Email Test Vendor",
            "contact_name": "John Smith",
            "contact_role": "Manager",
            "email": "emailtest@example.com",
            "phone": "555-123-4567",
        },
    )

    vendor_id = create_response.json()["id"]

    response = client.put(
        f"/vendors/{vendor_id}",
        json={
            "active": True,
            "name": "Email Test Vendor",
            "contact_name": "John Smith",
            "contact_role": "Manager",
            "email": "not-a-valid-email",
            "phone": "555-123-4567",
        },
    )

    assert response.status_code == 422


def test_update_vendor_invalid_phone(client):
    """Test that invalid phone data returns a validation error."""

    response = client.put(
        "/vendors/1",
        json={
            "active": True,
            "name": "Phone Test Vendor",
            "contact_name": "John Smith",
            "contact_role": "Manager",
            "email": "phonetest@example.com",
            "phone": "123",
        },
    )

    assert response.status_code == 422
