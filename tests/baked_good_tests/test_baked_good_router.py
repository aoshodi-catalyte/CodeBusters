import models
import pytest

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from routers.baked_good_router import router as baked_good_router
from routers.vendor_router import router as vendor_router
from security.secure_manager_login import check_role, oauth2_scheme


TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

app = FastAPI()
app.include_router(vendor_router)
app.include_router(baked_good_router)


def override_manager_role():
    """
    Bypasses manager authentication during router tests.
    """
    return {"role": "manager"}


def override_oauth2_scheme():
    """
    Bypasses the bearer-token requirement during router tests.

    role_checker declares Depends(oauth2_scheme) as its own sub-dependency.
    Overriding role_checker's own call is enough to bypass oauth2_scheme too
    (FastAPI rebuilds the sub-dependency tree from the override callable's
    signature), but this override is kept as a safety net in case any route
    ever depends on oauth2_scheme directly rather than through check_role.
    """
    return "test-token"


@pytest.fixture(scope="function")
def client():
    """
    Creates a test client using a temporary in-memory database.

    The manager authentication dependency is overridden so these tests
    can focus on baked good endpoint behavior.
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
    app.dependency_overrides[oauth2_scheme] = override_oauth2_scheme

    # check_role(["manager"]) is evaluated when each router module is
    # imported, so the actual dependency function (the "role_checker"
    # closure) must be located and overridden directly.
    #
    # NOTE: this walks the ORIGINAL router objects' `.routes` (built at
    # route-decoration time), not `app.routes`. In current FastAPI
    # versions, `app.routes` wraps included routers in a lazy internal
    # object that does not expose a populated `.dependant` tree the way
    # a plain APIRoute does, so walking `app.routes` here would silently
    # find nothing and leave every protected route unauthenticated.
    for router in (vendor_router, baked_good_router):
        for route in router.routes:
            if not hasattr(route, "dependant"):
                continue

            for dependency in route.dependant.dependencies:
                dependency_call = dependency.call

                if dependency_call is None:
                    continue

                if dependency_call.__name__ in {
                    "check_role",
                    "role_checker",
                    "verify_role",
                }:
                    app.dependency_overrides[
                        dependency_call
                    ] = override_manager_role

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def create_vendor(client, name="Test Vendor", email="vendor@example.com"):
    """Helper to create a vendor and return its ID."""
    vendor = {
        "active": True,
        "name": name,
        "contact_name": "John Doe",
        "contact_role": "Manager",
        "email": email,
        "phone": "5551234567",
    }

    response = client.post("/vendors", json=vendor)

    assert response.status_code == 201

    return response.json()["id"]


def test_post_baked_good(client):
    """Tests that a valid baked good can be created through the API."""

    vendor_id = create_vendor(client)

    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": vendor_id,
    }

    baked_good_response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert baked_good_response.status_code == 201

    data = baked_good_response.json()

    assert data["id"] is not None
    assert data["active"] is True
    assert data["name"] == "Chocolate Chip Cookie"
    assert data["description"] == "A cookie with chocolate chips."
    assert data["purchasing_cost"] == "1.00"
    assert data["retail_price"] == "2.50"
    assert data["vendor_id"] == vendor_id


def test_post_baked_good_missing_description(client):
    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1,
    }

    response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert response.status_code == 422


def test_post_baked_good_invalid_retail_price(client):
    baked_good = {
        "active": True,
        "name": "Chocolate Chip Cookie",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 3.00,
        "retail_price": 2.00,
        "vendor_id": 1,
    }

    response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert response.status_code == 422


def test_post_baked_good_empty_name(client):
    baked_good = {
        "active": True,
        "name": "   ",
        "description": "A cookie with chocolate chips.",
        "purchasing_cost": 1.00,
        "retail_price": 2.50,
        "vendor_id": 1,
    }

    response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert response.status_code == 422


def test_get_baked_goods_empty(client):
    response = client.get("/baked_goods/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_baked_goods(client):
    vendor_id = create_vendor(
        client,
        name="Test Vendor",
        email="christian@robinsonvendor.com",
    )

    baked_good = {
        "active": True,
        "name": "Chocolate Cake",
        "description": "A chocolate cake",
        "purchasing_cost": 5.0,
        "retail_price": 10.0,
        "vendor_id": vendor_id,
    }

    baked_good_response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert baked_good_response.status_code == 201

    response = client.get("/baked_goods/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] is not None
    assert data[0]["name"] == "Chocolate Cake"
    assert data[0]["vendor_id"] == vendor_id
    assert data[0]["purchasing_cost"] == "5.00"
    assert data[0]["retail_price"] == "10.00"


def test_post_baked_good_invalid_vendor(client):
    baked_good = {
        "active": True,
        "name": "Chocolate Cake",
        "description": "A chocolate cake",
        "purchasing_cost": 5.0,
        "retail_price": 10.0,
        "vendor_id": 9999,
    }

    response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert response.status_code == 404


def test_post_duplicate_baked_good(client):
    vendor_id = create_vendor(
        client,
        name="Test Vendor",
        email="christian@robinsonvendor.com",
    )

    baked_good = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": vendor_id,
    }

    first_response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert second_response.status_code == 409


def test_post_same_baked_good_different_vendor(client):
    vendor_1_id = create_vendor(
        client,
        name="Test Vendor One",
        email="vendorone@example.com",
    )

    vendor_2_id = create_vendor(
        client,
        name="Test Vendor Two",
        email="vendortwo@example.com",
    )

    baked_good_1 = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": vendor_1_id,
    }

    baked_good_2 = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": vendor_2_id,
    }

    response_1 = client.post(
        "/baked_goods/",
        json=baked_good_1,
    )

    response_2 = client.post(
        "/baked_goods/",
        json=baked_good_2,
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 409


def test_get_baked_good_by_id(client):
    vendor_id = create_vendor(
        client,
        name="Test Vendor",
        email="christian@robinsonvendor.com",
    )

    baked_good = {
        "active": True,
        "name": "Blueberry Muffin",
        "description": "A fresh blueberry muffin",
        "purchasing_cost": 2.0,
        "retail_price": 4.0,
        "vendor_id": vendor_id,
    }

    baked_good_response = client.post(
        "/baked_goods/",
        json=baked_good,
    )

    assert baked_good_response.status_code == 201

    baked_good_id = baked_good_response.json()["id"]

    response = client.get(
        f"/baked_goods/{baked_good_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == baked_good_id
    assert data["name"] == "Blueberry Muffin"
    assert data["description"] == "A fresh blueberry muffin"
    assert data["vendor_id"] == vendor_id
    assert data["purchasing_cost"] == "2.00"
    assert data["retail_price"] == "4.00"


# --- PUT /baked_goods/{baked_good_id} ---


def test_put_baked_good_success(client):
    """AC1: valid PUT updates the baked good and returns the entity."""

    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Chocolate Cake",
            "description": "A chocolate cake",
            "purchasing_cost": 5.0,
            "retail_price": 10.0,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    update_payload = {
        "active": False,
        "name": "Double Chocolate Cake",
        "description": "An even richer chocolate cake",
        "purchasing_cost": 6.0,
        "retail_price": 12.0,
        "vendor_id": vendor_id,
    }

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == baked_good_id
    assert data["active"] is False
    assert data["name"] == "Double Chocolate Cake"
    assert data["description"] == "An even richer chocolate cake"
    assert data["purchasing_cost"] == "6.00"
    assert data["retail_price"] == "12.00"
    assert data["vendor_id"] == vendor_id


def test_put_baked_good_persists_change(client):
    """Verifies the update is reflected on a subsequent GET."""

    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Bagel",
            "description": "A plain bagel",
            "purchasing_cost": 1.0,
            "retail_price": 2.5,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    update_response = client.put(
        f"/baked_goods/{baked_good_id}",
        json={
            "active": True,
            "name": "Everything Bagel",
            "description": "A bagel with everything seasoning",
            "purchasing_cost": 1.25,
            "retail_price": 3.0,
            "vendor_id": vendor_id,
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["purchasing_cost"] == "1.25"
    assert update_response.json()["retail_price"] == "3.00"

    get_response = client.get(
        f"/baked_goods/{baked_good_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Everything Bagel"
    assert get_response.json()["purchasing_cost"] == "1.25"
    assert get_response.json()["retail_price"] == "3.00"


def test_put_baked_good_with_nonexistent_id(client):
    """AC2: invalid ID returns 404."""

    vendor_id = create_vendor(client)

    update_payload = {
        "active": True,
        "name": "Ghost Pastry",
        "description": "Does not exist",
        "purchasing_cost": 1.0,
        "retail_price": 2.0,
        "vendor_id": vendor_id,
    }

    response = client.put(
        "/baked_goods/9999",
        json=update_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Baked good with ID 9999 was not found."
    )


def test_put_baked_good_with_invalid_vendor(client):
    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Croissant",
            "description": "A buttery croissant",
            "purchasing_cost": 1.5,
            "retail_price": 3.5,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    update_payload = {
        "active": True,
        "name": "Croissant",
        "description": "A buttery croissant",
        "purchasing_cost": 1.5,
        "retail_price": 3.5,
        "vendor_id": 9999,
    }

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json=update_payload,
    )

    assert response.status_code == 404


def test_put_baked_good_allows_keeping_own_name_and_vendor(client):
    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Cinnamon Roll",
            "description": "A gooey cinnamon roll",
            "purchasing_cost": 2.0,
            "retail_price": 4.5,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json={
            "active": True,
            "name": "Cinnamon Roll",
            "description": "An even gooier cinnamon roll",
            "purchasing_cost": 2.25,
            "retail_price": 5.0,
            "vendor_id": vendor_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["description"] == (
        "An even gooier cinnamon roll"
    )
    assert response.json()["purchasing_cost"] == "2.25"
    assert response.json()["retail_price"] == "5.00"


def test_put_baked_good_duplicate_name(client):
    """AC3-adjacent conflict case: name collides with another baked good."""

    vendor_id = create_vendor(client)

    client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Blueberry Muffin",
            "description": "A fresh blueberry muffin",
            "purchasing_cost": 2.0,
            "retail_price": 4.0,
            "vendor_id": vendor_id,
        },
    )

    second_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Banana Bread",
            "description": "A moist banana bread",
            "purchasing_cost": 2.0,
            "retail_price": 4.5,
            "vendor_id": vendor_id,
        },
    )

    second_id = second_response.json()["id"]

    response = client.put(
        f"/baked_goods/{second_id}",
        json={
            "active": True,
            "name": "Blueberry Muffin",
            "description": "A moist banana bread",
            "purchasing_cost": 2.0,
            "retail_price": 4.5,
            "vendor_id": vendor_id,
        },
    )

    assert response.status_code == 409


def test_put_baked_good_invalid_payload(client):
    """AC3: Pydantic validation rejects a malformed update payload."""

    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Danish",
            "description": "A fruit danish",
            "purchasing_cost": 2.0,
            "retail_price": 4.0,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json={
            "active": True,
            "name": "Danish",
            "description": "",
            "purchasing_cost": 2.0,
            "retail_price": 4.0,
            "vendor_id": vendor_id,
        },
    )

    assert response.status_code == 422


def test_put_baked_good_invalid_payload_retail_price_too_low(client):
    """AC3: retail_price <= purchasing_cost is rejected."""

    vendor_id = create_vendor(client)

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Danish",
            "description": "A fruit danish",
            "purchasing_cost": 2.0,
            "retail_price": 4.0,
            "vendor_id": vendor_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json={
            "active": True,
            "name": "Danish",
            "description": "A fruit danish",
            "purchasing_cost": 4.0,
            "retail_price": 3.0,
            "vendor_id": vendor_id,
        },
    )

    assert response.status_code == 422


def test_put_baked_good_updates_vendor(client):
    """
    AC4: updating a baked good's vendor moves it to the new vendor.

    Full relationship-side verification is covered at the repository
    level because there is no GET /vendors/{id} endpoint exposed here
    to inspect the relationship directly through the API.
    """

    vendor_1_id = create_vendor(
        client,
        name="Vendor One",
        email="vendorone@example.com",
    )

    vendor_2_id = create_vendor(
        client,
        name="Vendor Two",
        email="vendortwo@example.com",
    )

    create_response = client.post(
        "/baked_goods/",
        json={
            "active": True,
            "name": "Baguette",
            "description": "A crusty baguette",
            "purchasing_cost": 1.0,
            "retail_price": 3.0,
            "vendor_id": vendor_1_id,
        },
    )

    baked_good_id = create_response.json()["id"]

    response = client.put(
        f"/baked_goods/{baked_good_id}",
        json={
            "active": True,
            "name": "Baguette",
            "description": "A crusty baguette",
            "purchasing_cost": 1.0,
            "retail_price": 3.0,
            "vendor_id": vendor_2_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["vendor_id"] == vendor_2_id

    get_response = client.get(
        f"/baked_goods/{baked_good_id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["vendor_id"] == vendor_2_id
