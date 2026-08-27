import models

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db


from vendor.vendor_router import router


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
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

    assert data["name"] == "Bob's Burgers"
    assert data["contact_name"] == "Bob Belcher"
    assert data["contact_role"] == "CEO"
    assert data["email"] == "bestburgers@burger.com"
    assert data["phone"] == "123-456-7896"

def test_get_all_vendors(client):
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


def test_post_duplicate_vendor_returns_409(client):
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896",
    }

    first_response = client.post("/vendors", json=vendor_payload)

    assert first_response.status_code == 201

    second_response = client.post("/vendors", json=vendor_payload)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Vendor with this name or email already exists."
    )
def test_get_all_vendors_empty(client):
    response = client.get("/vendors")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_vendors_returns_multiple_vendors(client):
    vendor_1 = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bob@burger.com",
        "phone": "1234567896",
    }

    vendor_2 = {
        "active": False,
        "name": "Acme Supplies",
        "contact_name": "Wile E. Coyote",
        "contact_role": "Manager",
        "email": "wile@acme.com",
        "phone": "9876543210",
    }

    vendor_3 = {
        "active": True,
        "name": "Wayne Enterprises",
        "contact_name": "Bruce Wayne",
        "contact_role": "Owner",
        "email": "bruce@wayne.com",
        "phone": "5555555555",
    }

    client.post("/vendors", json=vendor_1)
    client.post("/vendors", json=vendor_2)
    client.post("/vendors", json=vendor_3)

    response = client.get("/vendors")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["name"] == "Bob's Burgers"
    assert data[1]["name"] == "Acme Supplies"
    assert data[2]["name"] == "Wayne Enterprises"


def test_get_all_vendors_response_contains_expected_fields(client):
    vendor_payload = {
        "active": True,
        "name": "Stark Industries",
        "contact_name": "Tony Stark",
        "contact_role": "CEO",
        "email": "tony@stark.com",
        "phone": "5551234567",
    }

    client.post("/vendors", json=vendor_payload)

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
