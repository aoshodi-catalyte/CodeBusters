import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base
from vendor.vendor_router import get_db


@pytest.fixture
def client():
    # in-memory SQLite - no real Postgres needed
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_post_new_vendor(client):
    response = client.post("/vendor", json={
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bob's Burgers"
    assert data["phone"] == "123-456-7896" 


def test_post_duplicate_vendor_fails(client):
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896"
    }
    client.post("/vendor", json=vendor_payload)
    response = client.post("/vendor", json=vendor_payload)

    assert response.status_code != 201


def test_get_all_vendors(client):
    client.post("/vendor", json={
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896"
    })
    client.post("/vendor", json={
        "active": True,
        "name": "Linda's Bakery",
        "contact_name": "Linda Belcher",
        "contact_role": "Owner",
        "email": "linda@bakery.com",
        "phone": "9876543210"
    })

    response = client.get("/vendor")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_vendor_by_id(client):
    post_response = client.post("/vendor", json={
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896"
    })
    vendor_id = post_response.json()["id"]

    response = client.get(f"/vendor/{vendor_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Bob's Burgers"


def test_get_vendor_by_id_not_found(client):
    response = client.get("/vendor/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found"