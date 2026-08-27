import models  # pylint: disable=unused-import

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
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
