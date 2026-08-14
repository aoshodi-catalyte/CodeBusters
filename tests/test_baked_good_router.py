import pytest

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base
from baked_good.baked_good_router import router as baked_good_router
from baked_good.baked_good_router import get_db as baked_good_get_db
from vendor.vendor_router import router as vendor_router
from vendor.vendor_router import get_db as vendor_get_db

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
app.include_router(vendor_router)
app.include_router(baked_good_router)

@pytest.fixture
def client():
    """
    Creates a test client using a temporary in-memory database.
    """

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        """
        Provides a test database session for the client.
        """
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[baked_good_get_db] = override_get_db
    app.dependency_overrides[vendor_get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
def test_post_baked_good(client):
    """
    Tests that a valid baked good can be created through the API.

    Creates a test vendor first because the baked good requires a valid
    vendor_id. Then sends a POST request containing valid baked good data
    and verifies that the API returns a 201 status code and the expected
    baked good information.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    vendor = {
        "active": True,
        "name": "Test Vendor",
        "contact_name": "John Doe",
        "contact_role": "Manager",
        "email": "john@testvendor.com",
        "phone": "5551234567",
        "vendor_id": 1
    }

    vendor_response = client.post("/vendor", json=vendor)
    assert vendor_response.status_code == 201

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1
    }
    baked_good_response = client.post("/baked_goods/", json=baked_good)
    assert baked_good_response.status_code == 201

    data = baked_good_response.json()

    assert data["active"] is True
    assert data["name"] == "Chocolate Chip Cookie"
    assert data["description"] == "A cookie with chocolate chips."
    assert data["purchasing_cost"] == 1.00
    assert data["retail_price"] == 2.50
    assert data["vendor_id"] == 1

def test_post_baked_good_missing_description(client):
    """
    Tests that a baked good cannot be created without a description.
    """

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1
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
        "vendor_id": 1
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
        "vendor_id": 1
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
        "vendor_id": 1
    }

    vendor_response = client.post("/vendor", json=vendor)
    assert vendor_response.status_code == 201

    baked_good = {
        "active": True,
        "name": "Chocolate Cake",
        "description": "A chocolate cake",
        "purchasing_cost": 5.0,
        "retail_price": 10.0,
        "vendor_id": 1
    }

    baked_good_response = client.post(
        "/baked_goods/",
        json=baked_good
    )

    assert baked_good_response.status_code == 201

    response = client.get("/baked_goods/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Chocolate Cake"
    assert response.json()[0]["vendor_id"] == 1