import pytest
from fastapi.testclient import TestClient
from database import Base, engine, SessionLocal, get_db
from main import app



@pytest.fixture
def client():
    """
    Creates a test client and prepares a clean database for each test.

    Drops and recreates all database tables before each test. Overrides
    the application's database dependency so that the test client uses
    a test database session. The database session and dependency override
    are cleaned up after the test is completed.

    Args:
        None

    Yields:
        TestClient: A FastAPI test client used to send requests to the API.
    """
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        """
        Provides a database session for the test client.

        Creates a SQLAlchemy database session and closes the session after
        the test request is completed.

        Args:
            None

        Yields:
            A SQLAlchemy database session for the test request.
        """

        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

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