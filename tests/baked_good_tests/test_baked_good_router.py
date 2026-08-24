import models
import pytest

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient


from database import Base, get_db
from baked_good.baked_good_router import router as baked_good_router
from vendor.vendor_router import router as vendor_router

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

app = FastAPI()
app.include_router(vendor_router)
app.include_router(baked_good_router)


@pytest.fixture(scope="function")
def client():
    """
    Creates a test client using a temporary in-memory database.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Optional cleanup (not required for in-memory SQLite)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def test_post_baked_good(client):
    """Tests that a valid baked good can be created through the API."""

    vendor = {
        "active": True,
        "name": "Test Vendor",
        "contact_name": "John Doe",
        "contact_role": "Manager",
        "email": "john@testvendor.com",
        "phone": "5551234567",
    }

    vendor_response = client.post("/vendors", json=vendor)
    assert vendor_response.status_code == 201

    vendor_data = vendor_response.json()
    vendor_id = vendor_data["id"]

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": vendor_id,
    }
    baked_good_response = client.post("/baked_goods/", json=baked_good)
    assert baked_good_response.status_code == 201

    data = baked_good_response.json()

    assert data["id"] is not None
    assert data["active"] is True
    assert data["name"] == "Chocolate Chip Cookie"
    assert data["description"] == "A cookie with chocolate chips."
    assert data["purchasing_cost"] == 1.00
    assert data["retail_price"] == 2.50
    assert data["vendor_id"] == vendor_id


def test_post_baked_good_missing_description(client):
    """
    Tests that a baked good cannot be created without a description.
    """

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1,
    }

    response = client.post("/baked_goods/", json=baked_good)

    assert response.status_code == 422


def test_post_baked_good_invalid_retail_price(client):
    """
    Tests that a baked good cannot be created when the retail price
    is less than the purchasing cost.
    """

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 3.00,
        "retail_price": 2.00,
        "vendor_id": 1,
    }

    response = client.post("/baked_goods/", json=baked_good)

    assert response.status_code == 422


def test_post_baked_good_empty_name(client):
    """
    Tests that a baked good cannot be created with an empty name.
    """

    baked_good = {
        "active": True,
        "name": "   ",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1,
    }

    response = client.post("/baked_goods/", json=baked_good)

    assert response.status_code == 422


def test_get_baked_goods_empty(client):
    """
    Tests that the GET baked goods endpoint returns an empty list
    when no baked goods are stored in the database.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    response = client.get("/baked_goods/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_baked_goods(client):
    """
    Tests that the GET baked goods endpoint returns stored baked goods.

    Creates a test vendor and baked good, then sends a GET request to
    the baked goods endpoint and verifies that the response has a 200
    status code and contains the expected baked good.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    vendor = {
        "active": True,
        "name": "Test Vendor",
        "contact_name": "Christian Robinson",
        "contact_role": "Manager",
        "email": "Christian@Robinsonvendor.com",
        "phone": "5551234567",
    }

    vendor_response = client.post("/vendors", json=vendor)

    assert vendor_response.status_code == 201

    baked_good = {
        "active": True,
        "name": "Chocolate Cake",
        "description": "A chocolate cake",
        "purchasing_cost": 5.0,
        "retail_price": 10.0,
        "vendor_id": 1,
    }

    baked_good_response = client.post("/baked_goods/", json=baked_good)

    assert baked_good_response.status_code == 201

    response = client.get("/baked_goods/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] is not None
    assert data[0]["name"] == "Chocolate Cake"
    assert data[0]["vendor_id"] == 1


def test_post_baked_good_invalid_vendor(client):
    """
    Tests that a baked good cannot be created when the vendor
    does not exist.
    """

    baked_good = {
        "active": True,
        "name": "Chocolate Cake",
        "description": "A chocolate cake",
        "purchasing_cost": 5.0,
        "retail_price": 10.0,
        "vendor_id": 9999,
    }

    response = client.post("/baked_goods/", json=baked_good)

    assert response.status_code == 404

def test_post_duplicate_baked_good(client):
    """
    Tests that a vendor cannot create the same baked good more than once.

    Creates a test vendor and baked good, then attempts to create the
    same baked good again for the same vendor and verifies that the
    response has a 409 status code.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    vendor = {
        "active": True,
        "name": "Test Vendor",
        "contact_name": "Christian Robinson",
        "contact_role": "Manager",
        "email": "Christian@Robinsonvendor.com",
        "phone": "5551234567",
    }

    vendor_response = client.post("/vendors", json=vendor)

    assert vendor_response.status_code == 201

    baked_good = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": 1,
    }

    first_response = client.post("/baked_goods/", json=baked_good)

    assert first_response.status_code == 201

    second_response = client.post("/baked_goods/", json=baked_good)

    assert second_response.status_code == 409

def test_post_baked_good_lowercase_name(client):
    """
    Tests that a baked good name cannot be entered in lowercase.

    Creates a test vendor and attempts to create a baked good with a
    lowercase name, then verifies that the response has a 422 status code.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    vendor = {
        "active": True,
        "name": "Test Vendor",
        "contact_name": "Christian Robinson",
        "contact_role": "Manager",
        "email": "Christian@Robinsonvendor.com",
        "phone": "5551234567",
    }

    vendor_response = client.post("/vendors", json=vendor)

    assert vendor_response.status_code == 201

    baked_good = {
        "active": True,
        "name": "blueberry muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": 1,
    }

    response = client.post("/baked_goods/", json=baked_good)

    assert response.status_code == 422

def test_post_same_baked_good_different_vendor(client):
    """
    Tests that different vendors can have the same baked good.

    Creates two test vendors and creates the same baked good for each
    vendor, then verifies that both requests are successful.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    vendor_1 = {
        "active": True,
        "name": "Test Vendor One",
        "contact_name": "Christian Robinson",
        "contact_role": "Manager",
        "email": "vendorone@example.com",
        "phone": "5551234567",
    }

    vendor_2 = {
        "active": True,
        "name": "Test Vendor Two",
        "contact_name": "John Smith",
        "contact_role": "Manager",
        "email": "vendortwo@example.com",
        "phone": "5551234568",
    }

    vendor_1_response = client.post("/vendors", json=vendor_1)
    vendor_2_response = client.post("/vendors", json=vendor_2)

    assert vendor_1_response.status_code == 201
    assert vendor_2_response.status_code == 201

    baked_good_1 = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": 1,
    }

    baked_good_2 = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": 2,
    }

    response_1 = client.post("/baked_goods/", json=baked_good_1)
    response_2 = client.post("/baked_goods/", json=baked_good_2)

    assert response_1.status_code == 201
    assert response_2.status_code == 201
