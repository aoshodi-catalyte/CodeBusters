import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from vendor.vendor_router import router


@pytest.fixture
def client():
    test_app = FastAPI()
    test_app.include_router(router)

    with TestClient(test_app) as test_client:
        yield test_client


def test_post_new_vendor(client):
    vendor_payload = {
        "active": True,
        "name": "Bob's Burgers",
        "contact_name": "Bob Belcher",
        "contact_role": "CEO",
        "email": "bestburgers@burger.com",
        "phone": "1234567896"
    }

    response = client.post("/vendor", json=vendor_payload)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Bob's Burgers"
    assert data["contact_name"] == "Bob Belcher"
    assert data["contact_role"] == "CEO"
    assert data["email"] == "bestburgers@burger.com"
    assert data["phone"] == "123-456-7896"