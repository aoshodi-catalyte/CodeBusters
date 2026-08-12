import pytest
from fastapi.testclient import TestClient
from database import Base, engine, SessionLocal, get_db
from main import app


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
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


def test_home_page(client):
    response = client.get("/baked_goods/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Hello! You are in Baked Goods. Baked Goods table is currently empty."
    }

def test_post_baked_good(client):
    baked_good = {
        "id": 1,
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1
    }

    response = client.post("/baked_goods/create", json=baked_good)

    assert response.status_code == 201

    data = response.json()

    assert data["active"] is True
    assert data["name"] == "Chocolate Chip Cookie"
    assert data["description"] == "A cookie with chocolate chips."
    assert data["purchasing_cost"] == 1.00
    assert data["retail_price"] == 2.50
    assert data["vendor_id"] == 1

def test_post_baked_good_missing_description(client):
    baked_good = {
        "id": 1,
        "active": True,
        "name": "Chocolate Chip Cookie",
        "purchasing_cost": 1.00,
        "retail_price": 2.50
    }

    response = client.post("/baked_goods/create", json=baked_good)

    assert response.status_code == 422

def test_post_baked_good_invalid_retail_price(client):
    baked_good = {
        "id": 1,
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 3.00,
        "retail_price": 2.00
    }

    response = client.post("/baked_goods/create", json=baked_good)

    assert response.status_code == 422    

def test_post_baked_good_empty_name(client):
    baked_good = {
        "id": 1,
        "active": True,
        "name": "   ",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50
    }

    response = client.post("/baked_goods/create", json=baked_good)

    assert response.status_code == 422

