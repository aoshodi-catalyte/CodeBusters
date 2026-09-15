import models
import pytest

from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from routers.purchase_router import router as purchase_router

from baked_good.baked_good_schema import BakedGoodSchema
from drink_recipe.drink_recipe_schema import DrinkRecipeSchema
from drink_recipe.drink_type_schema import DrinkTypeSchema
from vendor.vendor_schema import Vendor


# ---------------------------------------------------------------------------
# Test database
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Test application
# ---------------------------------------------------------------------------

app = FastAPI()
app.include_router(purchase_router)


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db():
    """
    Creates a fresh in-memory database for each test.

    The same test engine is used by both the test database session
    and the FastAPI client.
    """
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Creates a TestClient using the same in-memory database as the test.

    Authentication overrides are not required because the purchase router
    does not currently declare an authentication dependency.
    """

    def override_get_db():
        session = TestingSessionLocal()

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def create_vendor(db):
    """
    Creates a vendor directly in the test database.
    """
    vendor = Vendor(
        active=True,
        name="Test Vendor",
        contact_name="Test Contact",
        contact_role="Manager",
        email="vendor@example.com",
        phone="5555555555",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


def create_baked_good(db, price=Decimal("4.00")):
    """
    Creates a baked good directly in the test database.
    """
    vendor = create_vendor(db)

    baked_good = BakedGoodSchema(
        name="Test Brownie",
        description="Test brownie",
        purchasing_cost=Decimal("2.00"),
        retail_price=price,
        active=True,
        vendor_id=vendor.id,
    )

    db.add(baked_good)
    db.commit()
    db.refresh(baked_good)

    return baked_good


def create_drink_type(db):
    """
    Creates a drink type directly in the test database.
    """
    drink_type = DrinkTypeSchema(
        name="Coffee",
        description="Coffee-based drinks",
    )

    db.add(drink_type)
    db.commit()
    db.refresh(drink_type)

    return drink_type


def create_drink(db, price=Decimal("4.00")):
    """
    Creates a drink recipe directly in the test database.
    """
    drink_type = create_drink_type(db)

    drink = DrinkRecipeSchema(
        name="Test Coffee",
        description="Test coffee",
        production_cost=Decimal("2.00"),
        sale_price=price,
        active=True,
        type_id=drink_type.id,
    )

    db.add(drink)
    db.commit()
    db.refresh(drink)

    return drink


# ---------------------------------------------------------------------------
# POST /purchases
# ---------------------------------------------------------------------------

def test_create_purchase_no_promo(client, db):
    """
    AC: A purchase can be created without a promotion.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )

    response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
    )

    assert response.status_code == 201, response.json()

    data = response.json()

    assert data["subtotal"] == "4.00"
    assert data["discount_amount"] == "0.00"
    assert data["tax_amount"] == "0.28"
    assert data["total"] == "4.28"
    assert data["items"][0]["price_at_sale"] == "4.00"


# ---------------------------------------------------------------------------
# GET /purchases/{purchase_id}
# ---------------------------------------------------------------------------

def test_get_purchase_by_id(client, db):
    """
    AC: A valid purchase ID returns the corresponding purchase.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )

    create_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
    )

    assert create_response.status_code == 201, create_response.json()

    purchase_id = create_response.json()["id"]

    response = client.get(
        f"/purchases/{purchase_id}"
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["id"] == purchase_id
    assert data["subtotal"] == "4.00"
    assert data["discount_amount"] == "0.00"
    assert data["tax_amount"] == "0.28"
    assert data["total"] == "4.28"
    assert data["items"][0]["price_at_sale"] == "4.00"


def test_get_purchase_not_found(client):
    """
    AC: An invalid purchase ID returns 404.
    """

    response = client.get("/purchases/999999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /purchases
# ---------------------------------------------------------------------------

def test_list_purchases(client, db):
    """
    AC: All purchases are returned when requesting the purchase list.
    """

    baked_good = create_baked_good(
        db,
        Decimal("4.00"),
    )

    first_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 1,
                }
            ]
        },
    )

    assert first_response.status_code == 201, first_response.json()

    second_response = client.post(
        "/purchases",
        json={
            "items": [
                {
                    "item_type": "baked_good",
                    "item_id": baked_good.id,
                    "quantity": 2,
                }
            ]
        },
    )

    assert second_response.status_code == 201, second_response.json()

    response = client.get("/purchases")

    assert response.status_code == 200, response.json()

    data = response.json()

    assert len(data) >= 2

    totals = {
        purchase["total"]
        for purchase in data
    }

    assert "4.28" in totals
    assert "8.56" in totals
