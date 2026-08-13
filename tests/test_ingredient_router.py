from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from constants.INGREDIENT_TYPES import UnitOfMeasure, CafeAllergen

from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)

from ingredient.ingredient_router import router
import ingredient.ingredient_router as ingredient_router


# ============================================================
# TEST APPLICATION
# ============================================================

app = FastAPI()
app.include_router(router)


# ============================================================
# DATABASE OVERRIDE
# ============================================================

def override_get_db():
    """
    Provide a fake database session for router tests.

    The repository function is mocked in these tests, so we
    do not need a real database.
    """
    db = MagicMock()
    yield db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================
# TEST DATA
# ============================================================

# Get valid enum values without assuming their exact names.
VALID_UNIT_OF_MEASURE = next(iter(UnitOfMeasure)).value
VALID_ALLERGEN = next(iter(CafeAllergen)).value


def valid_ingredient_payload():
    """
    Return a valid ingredient request body.
    """
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
    """
    Return the data that the mocked repository would return.
    """
    payload = valid_ingredient_payload()

    return {
        "id": 1,
        "name": payload["name"],
        "active": payload["active"],
        "purchasing_cost": Decimal(payload["purchasing_cost"]),
        "unit_amount": Decimal(payload["unit_amount"]),
        "unit_of_measure": payload["unit_of_measure"],
        "allergens": [payload["allergens"][0]],
        "vendor_id": payload["vendor_id"],
    }


# ============================================================
# 1. SUCCESSFUL CREATION
# ============================================================

def test_create_ingredient_success(monkeypatch):
    """
    Test that a valid ingredient is successfully created.
    """

    expected_ingredient = valid_ingredient_response()

    mock_create = MagicMock(return_value=expected_ingredient)

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredient/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Flour"
    assert data["active"] is True
    assert data["vendor_id"] == 1

    mock_create.assert_called_once()


# ============================================================
# 2. VENDOR DOES NOT EXIST
# ============================================================

def test_create_ingredient_vendor_not_found(monkeypatch):
    """
    Test that a missing vendor returns HTTP 404.
    """

    mock_create = MagicMock(
        side_effect=VendorNotFoundError(999)
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 999

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"]["error"] == "vendor_not_found"


# ============================================================
# 3. DUPLICATE INGREDIENT
# ============================================================

def test_create_ingredient_already_exists(monkeypatch):
    """
    Test that attempting to create a duplicate ingredient
    returns HTTP 409.
    """

    mock_create = MagicMock(
        side_effect=IngredientAlreadyExistsError("Flour")
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredient/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "ingredient_already_exists"


# ============================================================
# 4. DATABASE CONSTRAINT ERROR
# ============================================================

def test_create_ingredient_constraint_error(monkeypatch):
    """
    Test that a database constraint violation returns HTTP 409.
    """

    mock_create = MagicMock(
        side_effect=IngredientConstraintError(
            "ck_ingredient_unit_amount_positive"
        )
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredient/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 409

    data = response.json()

    assert data["detail"]["error"] == "database_constraint_violation"


# ============================================================
# 5. UNEXPECTED DATABASE ERROR
# ============================================================

def test_create_ingredient_database_error(monkeypatch):
    """
    Test that an unexpected SQLAlchemy error returns HTTP 500.
    """

    mock_create = MagicMock(
        side_effect=SQLAlchemyError("Database connection failed")
    )

    monkeypatch.setattr(
        ingredient_router,
        "create_ingredient",
        mock_create,
    )

    response = client.post(
        "/ingredient/",
        json=valid_ingredient_payload(),
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"]["error"] == "database_error"

    assert (
        data["detail"]["message"]
        == "An unexpected database error occurred while creating the ingredient."
    )


# ============================================================
# 6. INVALID VENDOR ID
# ============================================================

def test_create_ingredient_invalid_vendor_id(monkeypatch):
    """
    Test that vendor_id must be greater than zero.
    """

    payload = valid_ingredient_payload()
    payload["vendor_id"] = 0

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 7. NEGATIVE PURCHASING COST
# ============================================================

def test_create_ingredient_negative_purchasing_cost(monkeypatch):
    """
    Test that purchasing_cost cannot be negative.
    """

    payload = valid_ingredient_payload()
    payload["purchasing_cost"] = "-5.00"

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 8. ZERO UNIT AMOUNT
# ============================================================

def test_create_ingredient_zero_unit_amount(monkeypatch):
    """
    Test that unit_amount must be greater than zero.
    """

    payload = valid_ingredient_payload()
    payload["unit_amount"] = "0"

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 9. MISSING REQUIRED FIELD
# ============================================================

def test_create_ingredient_missing_name(monkeypatch):
    """
    Test that name is required.
    """

    payload = valid_ingredient_payload()
    del payload["name"]

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 422


# ============================================================
# 10. EMPTY INGREDIENT NAME
# ============================================================

def test_create_ingredient_empty_name(monkeypatch):
    """
    Test that ingredient name cannot be empty.
    """

    payload = valid_ingredient_payload()
    payload["name"] = ""

    response = client.post(
        "/ingredient/",
        json=payload,
    )

    assert response.status_code == 422
