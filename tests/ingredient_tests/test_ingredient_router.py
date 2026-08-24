"""Tests for the ingredient API router."""

from decimal import Decimal
from unittest.mock import MagicMock
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

import ingredient.ingredient_router as ingredient_router
from constants.ingredient_types import CafeAllergen, UnitOfMeasure
from database import get_db
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from ingredient.ingredient_router import router
from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_repository import create_ingredient
from vendor.vendor_schema import Vendor
from main import app

app = FastAPI()
app.include_router(router)

@pytest.fixture(name="client")

def client(db):
    """Create a test client using the test database session."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

def create_test_vendor(db):
    """Create a vendor for ingredient integration tests."""

    vendor = Vendor(
        name="Test Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="john@testvendor.com",
        phone="3125551234",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor

def create_test_ingredient(
    db,
    vendor_id,
    name="Flour",
    ):
    """Create an ingredient using the real repository."""

    ingredient = Ingredient(
        active=True,
        name=name,
        purchasing_cost=Decimal("10.00"),
        unit_amount=Decimal("25.00"),
        unit_of_measure=UnitOfMeasure.POUNDS,
        allergens=["Wheat"],
        vendor_id=vendor_id,
    )

    return create_ingredient(
        db=db,
        ingredient_data=ingredient,
    )

def test_read_all_ingredients_returns_empty_list():
    """Verify an empty list is returned when no ingredients exist."""

    response = client.get("/ingredients/all")

    assert response.status_code == 200

    data = response.json()

    assert data["ingredients"] == []

def override_get_db():
    """Provide a mock database session for router tests."""
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

VALID_UNIT_OF_MEASURE = next(iter(UnitOfMeasure)).value
VALID_ALLERGEN = next(iter(CafeAllergen)).value


def valid_ingredient_payload():
    """Return a valid ingredient request body."""
    return {
        "active": True,
        "name": "Flour",
        "purchasing_cost": "10.50",
        "unit_amount": "25.00",
        "unit_of_measure": VALID_UNIT_OF_MEASURE,
        "allergens": [VALID_ALLERGEN],
        "vendor_id": 1,
    }

def valid_ingredient_response():
    """Return the data that the mocked repository would return."""
    payload = valid_ingredient_payload()

    return {
        "id": 1,
        "name": payload["name"],
        "active": payload["active"],
        "purchasing_cost": Decimal(payload["purchasing_cost"]),
        "unit_amount": Decimal(payload["unit_amount"]),
        "unit_of_measure": payload["unit_of_measure"],
        "allergens": [
            {"name": allergen.title()}
            for allergen in payload["allergens"]
        ],
        "vendor_id": payload["vendor_id"],
    }


def test_create_ingredient_success(monkeypatch):
    """Test that a valid ingredient is successfully created."""
    expected_ingredient = valid_ingredient_response()
    mock_create = MagicMock(return_value=expected_ingredient)

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Flour"
    assert data["active"] is True
    assert data["vendor_id"] == 1

    mock_create.assert_called_once()


def test_create_ingredient_vendor_not_found(monkeypatch):
    """Test that a missing vendor returns HTTP 404."""
    mock_create = MagicMock(
        side_effect=VendorNotFoundError(999),
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 999

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "vendor_not_found"


def test_create_ingredient_already_exists(monkeypatch):
    """Test that a duplicate ingredient returns HTTP 409."""
    mock_create = MagicMock(
        side_effect=IngredientAlreadyExistsError("Flour"),
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "ingredient_already_exists"


def test_create_ingredient_constraint_error(monkeypatch):
    """Test that a database constraint violation returns HTTP 409."""
    mock_create = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_unit_amount_positive",
        ),
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "database_constraint_violation"


def test_create_ingredient_database_error(monkeypatch):
    """Test that an unexpected SQLAlchemy error returns HTTP 500."""
    mock_create = MagicMock(
        side_effect=SQLAlchemyError("Database connection failed"),
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredients/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"]["error"] == "database_error"
    assert (
        data["detail"]["message"]
        == "An unexpected database error occurred "
        "while creating the ingredient."
    )


def test_create_ingredient_invalid_vendor_id():
    """Test that vendor_id must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_negative_purchasing_cost():
    """Test that purchasing_cost cannot be negative."""
    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_zero_unit_amount():
    """Test that unit_amount must be greater than zero."""
    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_missing_name():
    """Test that name is required."""
    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_create_ingredient_empty_name():
    """Test that ingredient name cannot be empty."""
    payload = valid_ingredient_payload()
    payload["name"] = ""

    response = client.post(
        "/ingredients/",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_success(monkeypatch):
    """Test that a valid PUT updates and returns the ingredient."""
    expected_ingredient = valid_ingredient_response()
    expected_ingredient["name"] = "Whole Wheat Flour"
    expected_ingredient["purchasing_cost"] = Decimal("12.50")
    expected_ingredient["unit_amount"] = Decimal("30.00")

    mock_update = MagicMock(return_value=expected_ingredient)

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    payload = valid_ingredient_payload()
    payload["name"] = "Whole Wheat Flour"
    payload["purchasing_cost"] = "12.50"
    payload["unit_amount"] = "30.00"

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Whole Wheat Flour"
    assert data["purchasing_cost"] == 12.50
    assert data["unit_amount"] == 30.00
    assert data["vendor_id"] == 1

    mock_update.assert_called_once()


def test_update_ingredient_not_found(monkeypatch):
    """Test that updating a nonexistent ingredient returns HTTP 404."""
    mock_update = MagicMock(return_value=None)

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/9999",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "ingredient_not_found"
    assert (
        data["detail"]["message"]
        == "Ingredient with ID 9999 was not found."
    )

    mock_update.assert_called_once()


def test_update_ingredient_negative_purchasing_cost():
    """Test that PUT rejects a negative purchasing cost."""
    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_zero_unit_amount():
    """Test that PUT rejects a zero unit amount."""
    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_invalid_unit_of_measure():
    """Test that PUT rejects an invalid unit of measure."""
    payload = valid_ingredient_payload()
    payload["unit_of_measure"] = "invalid_unit"

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_invalid_allergen():
    """Test that PUT rejects an invalid allergen."""
    payload = valid_ingredient_payload()
    payload["allergens"] = ["Kryptonite"]

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_missing_name():
    """Test that PUT rejects a payload without a name."""
    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_empty_name():
    """Test that PUT rejects an empty ingredient name."""
    payload = valid_ingredient_payload()
    payload["name"] = ""

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_invalid_vendor_id():
    """Test that PUT rejects an invalid vendor ID."""
    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 422


def test_update_ingredient_vendor_not_found(monkeypatch):
    """Test that a missing vendor returns HTTP 404."""
    mock_update = MagicMock(
        side_effect=VendorNotFoundError(999),
    )

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 999

    response = client.put(
        "/ingredients/1",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "vendor_not_found"


def test_update_ingredient_already_exists(monkeypatch):
    """Test that a duplicate ingredient name returns HTTP 409."""
    mock_update = MagicMock(
        side_effect=IngredientAlreadyExistsError("Flour"),
    )

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/1",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "ingredient_already_exists"


def test_update_ingredient_constraint_error(monkeypatch):
    """Test that a database constraint violation returns HTTP 409."""
    mock_update = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_unit_amount_positive",
        ),
    )

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/1",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "database_constraint_violation"


def test_update_ingredient_database_error(monkeypatch):
    """Test that an unexpected SQLAlchemy error returns HTTP 500."""
    mock_update = MagicMock(
        side_effect=SQLAlchemyError("Database connection failed"),
    )

    monkeypatch.setattr(
        ingredient_router,
        "update_ingredient",
        mock_update,
    )

    response = client.put(
        "/ingredients/1",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"]["error"] == "database_error"
    assert (
        data["detail"]["message"]
        == "An unexpected database error occurred "
        "while updating the ingredient."
    )
