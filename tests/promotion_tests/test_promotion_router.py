import pytest

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from routers.promotion_router import router as promotion_router

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

app = FastAPI()
app.include_router(promotion_router)

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

def test_post_promotion(client):
    """
    Test that a valid promotion can be created successfully.
    """
    promotion = {
        "active": True,
        "promo_code": "SUMMER2026",
        "discount_percentage": 20.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    response = client.post("/promotions/", json=promotion)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["active"] is True
    assert data["promo_code"] == "SUMMER2026"
    assert data["discount_percentage"] == 20.0
    assert data["start_datetime"] is not None
    assert data["end_datetime"] is not None

def test_post_promotion_returns_created_id(client):
    """
    Test that a newly created promotion receives a database ID.
    """
    promotion = {
        "active": True,
        "promo_code": "ID2026",
        "discount_percentage": 15.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    response = client.post("/promotions/", json=promotion)

    assert response.status_code == 201
    assert response.json()["id"] == 1

def test_post_inactive_promotion(client):
    """
    Test that an inactive promotion can be created successfully.
    """
    promotion = {
        "active": False,
        "promo_code": "INACTIVE2026",
        "discount_percentage": 25.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    response = client.post("/promotions/", json=promotion)

    assert response.status_code == 201
    assert response.json()["active"] is False

def test_post_promotion_rejects_lowercase_promo_code(client):
    """
    Test that a promo code containing lowercase letters is rejected.
    """
    promotion = {
        "active": True,
        "promo_code": "summer2026",
        "discount_percentage": 20.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    response = client.post("/promotions/", json=promotion)

    assert response.status_code == 422


def test_post_promotion_requires_promo_code(client):
    """
    Test that promo_code is required.
    """
    promotion = {
        "active": True,
        "discount_percentage": 20.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    response = client.post("/promotions/", json=promotion)

    assert response.status_code == 422

def test_post_promotion_duplicate_promo_code(client):
    promotion = {
        "active": True,
        "promo_code": "SUMMER2026",
        "discount_percentage": 20.0,
        "start_datetime": "08/19/2026 09:00 AM",
        "end_datetime": "08/31/2026 11:59 PM"
    }

    first_response = client.post("/promotions/", json=promotion)

    assert first_response.status_code == 201

    second_response = client.post("/promotions/", json=promotion)

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Promotion with promo code 'SUMMER2026' already exists."
    }

def test_get_all_promotions(client):
    """
    Test that all promotions are returned successfully.
    """
    promotion_1 = {
        "active": True,
        "promo_code": "SAVE10",
        "discount_percentage": 10.0,
        "start_datetime": "08/01/2026 10:00 AM",
        "end_datetime": "08/31/2026 11:59 PM"
    }

    promotion_2 = {
        "active": True,
        "promo_code": "SAVE20",
        "discount_percentage": 20.0,
        "start_datetime": "08/05/2026 09:00 AM",
        "end_datetime": "08/25/2026 10:00 PM"
    }

    client.post("/promotions/", json=promotion_1)
    client.post("/promotions/", json=promotion_2)

    response = client.get("/promotions/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["promo_code"] == "SAVE10"
    assert data[0]["discount_percentage"] == 10.0
    assert data[1]["promo_code"] == "SAVE20"
    assert data[1]["discount_percentage"] == 20.0


def test_get_all_promotions_empty(client):
    """Test that an empty list is returned when no promotions exist."""
    response = client.get("/promotions/")

    assert response.status_code == 200
    assert response.json() == []

def test_get_promotion_by_id(client):
    """
    Tests that the GET promotion by ID endpoint returns the
    promotion matching the provided ID.

    Creates a test promotion, then sends a GET request using the
    promotion ID and verifies that the response has a 200 status
    code and contains the expected promotion.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    promotion = {
        "active": True,
        "promo_code": "SUMMER20",
        "discount_percentage": 20.0,
        "start_datetime": "08/01/2026 09:00 AM",
        "end_datetime": "08/31/2026 11:59 PM",
    }

    promotion_response = client.post(
        "/promotions/",
        json=promotion
    )

    assert promotion_response.status_code == 201

    promotion_id = promotion_response.json()["id"]

    response = client.get(f"/promotions/{promotion_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == promotion_id
    assert data["active"] is True
    assert data["promo_code"] == "SUMMER20"
    assert data["discount_percentage"] == 20.0

def test_get_promotion_by_id_invalid_id(client):
    """
    Tests that the GET promotion by ID endpoint returns a 404
    status code when the promotion does not exist.

    Sends a GET request using an ID that does not exist and verifies
    that the response has a 404 status code.

    Args:
        client: FastAPI test client provided by the client fixture.

    Returns:
        None
    """

    response = client.get("/promotions/9999")

    assert response.status_code == 404

    assert response.json()["detail"] == "Invalid Promotion ID"

def test_deactivate_promotion(client):
    """
    Test that a promotion can be deactivated (soft deleted) through
    the API and returns HTTP 204.
    """
    promotion = {
        "active": True,
        "promo_code": "DEACTIVATE1",
        "discount_percentage": 20.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM"
    }

    create_response = client.post("/promotions/", json=promotion)
    promotion_id = create_response.json()["id"]

    response = client.delete(f"/promotions/{promotion_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_deactivate_promotion_sets_active_false(client):
    """
    Test that deactivating a promotion sets active to False and the
    change is reflected on a subsequent GET request.
    """
    promotion = {
        "active": True,
        "promo_code": "DEACTIVATE2",
        "discount_percentage": 10.0,
        "start_datetime": "07/01/2026 09:00 AM",
        "end_datetime": "07/31/2026 11:59 PM"
    }

    create_response = client.post("/promotions/", json=promotion)
    promotion_id = create_response.json()["id"]

    client.delete(f"/promotions/{promotion_id}")

    get_response = client.get(f"/promotions/{promotion_id}")

    assert get_response.status_code == 200
    assert get_response.json()["active"] is False


def test_deactivate_promotion_with_invalid_id(client):
    """
    Test that deactivating a promotion with an ID that does not exist
    returns HTTP 404.
    """
    response = client.delete("/promotions/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Promotion ID"


def test_deactivate_promotion_preserves_record(client):
    """
    Test that deactivating a promotion preserves the historical
    record rather than deleting it.
    """
    promotion = {
        "active": True,
        "promo_code": "PRESERVE2026",
        "discount_percentage": 40.0,
        "start_datetime": "08/01/2026 09:00 AM",
        "end_datetime": "08/31/2026 11:59 PM"
    }

    create_response = client.post("/promotions/", json=promotion)
    promotion_id = create_response.json()["id"]

    client.delete(f"/promotions/{promotion_id}")

    get_response = client.get(f"/promotions/{promotion_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == promotion_id
    assert data["promo_code"] == "PRESERVE2026"
    assert data["discount_percentage"] == 40.0
    assert data["active"] is False


def test_update_promotion(client):
    """
    Test that a promotion can be updated through the API and the
    updated entity is returned.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "BEFORE2026",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    update_payload = {
        "active": False,
        "promo_code": "AFTER2026",
        "discount_percentage": 45.0,
        "start_datetime": "07/01/2026 09:00 AM",
        "end_datetime": "07/31/2026 11:59 PM",
    }

    response = client.put(
        f"/promotions/{promotion_id}", json=update_payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == promotion_id
    assert data["active"] is False
    assert data["promo_code"] == "AFTER2026"
    assert data["discount_percentage"] == 45.0


def test_update_promotion_persists_change(client):
    """
    Test that an update is reflected on a subsequent GET request.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "PATCH1",
            "discount_percentage": 5.0,
            "start_datetime": "08/01/2026 09:00 AM",
            "end_datetime": "08/31/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    client.put(
        f"/promotions/{promotion_id}",
        json={
            "active": True,
            "promo_code": "PATCH2",
            "discount_percentage": 15.0,
            "start_datetime": "08/01/2026 09:00 AM",
            "end_datetime": "08/31/2026 11:59 PM",
        },
    )

    get_response = client.get(f"/promotions/{promotion_id}")

    assert get_response.status_code == 200
    assert get_response.json()["promo_code"] == "PATCH2"
    assert get_response.json()["discount_percentage"] == 15.0


def test_update_promotion_with_invalid_id(client):
    """
    Test that updating a promotion with an ID that does not exist
    returns HTTP 404.
    """
    update_payload = {
        "active": True,
        "promo_code": "NOTFOUND2026",
        "discount_percentage": 10.0,
        "start_datetime": "06/01/2026 09:00 AM",
        "end_datetime": "06/30/2026 11:59 PM",
    }

    response = client.put("/promotions/9999", json=update_payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Promotion ID"


def test_update_promotion_rejects_lowercase_promo_code(client):
    """
    Test that the API rejects an update payload with a lowercase
    promo code.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "VALIDCODE",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    response = client.put(
        f"/promotions/{promotion_id}",
        json={
            "active": True,
            "promo_code": "lowercase",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    assert response.status_code == 422


def test_update_promotion_rejects_discount_over_100(client):
    """
    Test that the API rejects an update payload with a discount
    percentage above 100.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "OVERLIMIT",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    response = client.put(
        f"/promotions/{promotion_id}",
        json={
            "active": True,
            "promo_code": "OVERLIMIT",
            "discount_percentage": 150.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    assert response.status_code == 422


def test_update_promotion_rejects_end_before_start(client):
    """
    Test that the API rejects an update payload where the end
    datetime is before the start datetime.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "BADDATES",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    response = client.put(
        f"/promotions/{promotion_id}",
        json={
            "active": True,
            "promo_code": "BADDATES",
            "discount_percentage": 10.0,
            "start_datetime": "06/30/2026 11:59 PM",
            "end_datetime": "06/01/2026 09:00 AM",
        },
    )

    assert response.status_code == 422


def test_update_promotion_missing_required_field(client):
    """
    Test that the API rejects an update payload missing a required
    field.
    """
    create_response = client.post(
        "/promotions/",
        json={
            "active": True,
            "promo_code": "MISSINGFIELD",
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    promotion_id = create_response.json()["id"]

    response = client.put(
        f"/promotions/{promotion_id}",
        json={
            "active": True,
            "discount_percentage": 10.0,
            "start_datetime": "06/01/2026 09:00 AM",
            "end_datetime": "06/30/2026 11:59 PM",
        },
    )

    assert response.status_code == 422
