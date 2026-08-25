import models
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from database import Base, get_db
from ingredient.ingredient_router import router as ingredient_router
from vendor.vendor_router import router as vendor_router

# Use an in-memory SQLite database for fast integration tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app = FastAPI()
app.include_router(ingredient_router)
app.include_router(vendor_router)
@pytest.fixture
def client():
    """
    Creates a test client using a temporary in-memory database.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

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

# --- POST /ingredients/ Tests (1 to 5) ---

def test_create_ingredient_success(client):
    """Test 1: Successfully creating an ingredient returns 201 Created."""
    
    vendor_res = client.post("/vendors/", json={
            "active": True,
            "name": "Bob's Burgers",
            "contact_name": "Bob Belcher",
            "contact_role": "CEO",
            "email": "bestburgers@burger.com",
            "phone": "1234567896",
        })

    vendor_id = vendor_res.json()["id"]
    
    payload = {
        "active": True,
        "name": "Flour",
        "purchasing_cost": 2.50,
        "unit_amount": 1000.0,
        "unit_of_measure": "g",
        "vendor_id": vendor_id,
        "allergens": ["gluten"]
    }
    response = client.post("/ingredients/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Flour"
    assert "id" in data


def test_create_ingredient_vendor_not_found(client):
    """Test 2: Creating an ingredient with a non-existent vendor returns 404."""
    payload = {
        "active": True,
        "name": "Sugar",
        "purchasing_cost": 1.50,
        "unit_amount": 500.0,
        "unit_of_measure": "g",
        "vendor_id": 999,  # Doesn't exist
        "allergens": []
    }
    response = client.post("/ingredients/", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "vendor_not_found"


def test_create_ingredient_already_exists(client):
    """Test 3: Creating a duplicate ingredient name returns 409 Conflict."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]

    payload = {
        "active": True,
        "name": "Salt",
        "purchasing_cost": 1.00,
        "unit_amount": 100.0,
        "unit_of_measure": "g",
        "vendor_id": vendor_id,
        "allergens": []
    }
    # Create first time
    client.post("/ingredients/", json=payload)
    # Create second time with same name
    response = client.post("/ingredients/", json=payload)
    
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "ingredient_already_exists"


def test_create_ingredient_invalid_data_type(client):
    """Test 4: FastAPI validation catches bad types (e.g. string for cost) returning 422."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    
    payload = {
        "active": True,
        "name": "Butter",
        "purchasing_cost": "not-a-number",  # Invalid type
        "unit_amount": 200.0,
        "unit_of_measure": "g",
        "vendor_id": vendor_id,
        "allergens": []
    }
    response = client.post("/ingredients/", json=payload)
    assert response.status_code == 422


def test_create_ingredient_missing_required_field(client):
    """Test 5: Omitting a required field returns 422 Unprocessable Entity."""
    response = client.post("/ingredients/", json={"name": "Incomplete"})
    assert response.status_code == 422


# --- GET /ingredients/ Tests (6 to 7) ---

def test_read_all_ingredients_success(client):
    """Test 6: Retrieving all ingredients returns 200 OK with inventory list."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    
    client.post("/ingredients/", json={
        "active": True, "name": "Rice", "purchasing_cost": 3.00,
        "unit_amount": 1000.0, "unit_of_measure": "g", "vendor_id": vendor_id, "allergens": []
    })
    
    response = client.get("/ingredients/")
    
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_read_all_ingredients_empty(client):
    """Test 7: Retrieving inventory when empty returns 200 OK with an empty list."""
    response = client.get("/ingredients/")
    assert response.status_code == 200
    assert response.json() == []


# --- GET /ingredients/{id} Tests (8 to 9) ---

def test_read_ingredient_by_id_success(client):
    """Test 8: Retrieving a single valid ingredient ID returns 200 OK."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    create_res = client.post("/ingredients/", json={
        "active": True, "name": "Milk", "purchasing_cost": 2.00,
        "unit_amount": 1.0, "unit_of_measure": "L", "vendor_id": vendor_id, "allergens": ["Milk"]
    })
    ingredient_id = create_res.json()["id"]

    response = client.get(f"/ingredients/{ingredient_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == ingredient_id
    assert response.json()["name"] == "Milk"


def test_read_ingredient_by_id_not_found(client):
    """Test 9: Retrieving a non-existent ingredient ID returns 404 Not Found."""
    response = client.get("/ingredients/999")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "ingredient_not_found"


# --- PUT /ingredients/{id} Tests (10 to 15) ---

def test_update_ingredient_success(client):
    """Test 10: Successfully updating an existing ingredient returns 200 OK."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    create_res = client.post("/ingredients/", json={
        "active": True, "name": "Oil", "purchasing_cost": 5.00,
        "unit_amount": 1000.0, "unit_of_measure": "ml", "vendor_id": vendor_id, "allergens": []
    })
    ingredient_id = create_res.json()["id"]

    update_payload = {
        "active": False,
        "name": "Olive Oil",
        "purchasing_cost": 7.50,
        "unit_amount": 1000.0,
        "unit_of_measure": "ml",
        "vendor_id": vendor_id,
        "allergens": []
    }
    response = client.put(f"/ingredients/{ingredient_id}", json=update_payload)
    
    assert response.status_code == 200
    assert response.json()["name"] == "Olive Oil"
    assert response.json()["active"] is False


def test_update_ingredient_not_found(client):
    """Test 11: Updating a non-existent ingredient ID returns 404 Not Found."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    payload = {
        "active": True, "name": "Pepper", "purchasing_cost": 1.00,
        "unit_amount": 50.0, "unit_of_measure": "g", "vendor_id": vendor_id, "allergens": []
    }
    response = client.put("/ingredients/999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "ingredient_not_found"


def test_update_ingredient_vendor_not_found(client):
    """Test 12: Updating an ingredient with a non-existent vendor ID returns 404."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    create_res = client.post("/ingredients/", json={
        "active": True, "name": "Garlic", "purchasing_cost": 1.50,
        "unit_amount": 100.0, "unit_of_measure": "g", "vendor_id": vendor_id, "allergens": []
    })
    ingredient_id = create_res.json()["id"]

    update_payload = {
        "active": True, "name": "Garlic", "purchasing_cost": 1.50,
        "unit_amount": 100.0, "unit_of_measure": "g",
        "vendor_id": 9999,  # Invalid vendor
        "allergens": []
    }
    response = client.put(f"/ingredients/{ingredient_id}", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "vendor_not_found"


def test_update_ingredient_already_exists(client):
    """Test 13: Updating an ingredient name to one that already exists returns 409."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    client.post("/ingredients/", json={
        "active": True, "name": "Apples", "purchasing_cost": 3.00,
        "unit_amount": 1.0, "unit_of_measure": "kg", "vendor_id": vendor_id, "allergens": []
    })
    item2 = client.post("/ingredients/", json={
        "active": True, "name": "Bananas", "purchasing_cost": 2.00,
        "unit_amount": 1.0, "unit_of_measure": "kg", "vendor_id": vendor_id, "allergens": []
    }).json()

    # Try to rename "Bananas" to "Apples" (which already exists)
    update_payload = {
        "active": True,
        "name": "Apples",  # Duplicate name
        "purchasing_cost": 2.00,
        "unit_amount": 1.0,
        "unit_of_measure": "kg",
        "vendor_id": vendor_id,
        "allergens": []
    }
    response = client.put(f"/ingredients/{item2['id']}", json=update_payload)
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "ingredient_already_exists"


def test_update_ingredient_invalid_schema(client):
    """Test 14: Passing bad payload schema to update returns 422 Unprocessable Entity."""
    response = client.put(f"/ingredients/1", json={"invalid_field": True})
    assert response.status_code == 422


def test_get_all_ingredients_multiple(client):
    """Test 15: Retrieving inventory with multiple items returns correct count."""
    vendor_res = client.post("/vendors/", json={
                "active": True,
                "name": "Bob's Burgers",
                "contact_name": "Bob Belcher",
                "contact_role": "CEO",
                "email": "bestburgers@burger.com",
                "phone": "1234567896",
            })
    
    vendor_id = vendor_res.json()["id"]
    for name in ["Carrot", "Potato", "Tomato"]:
        client.post("/ingredients/", json={
            "active": True, "name": name, "purchasing_cost": 1.00,
            "unit_amount": 1.0, "unit_of_measure": "kg", "vendor_id": vendor_id, "allergens": []
        })

    response = client.get("/ingredients/")
    assert response.status_code == 200
    assert len(response.json()) == 3