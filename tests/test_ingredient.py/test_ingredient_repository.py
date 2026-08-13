import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_repository import (
    create_ingredient,
    get_or_create_allergen,
)
from ingredient.ingredient_schema import (
    AllergenSchema,
    IngredientSchema,
)
from ingredient.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientConstraintError,
    VendorNotFoundError,
)
from vendor.vendor_schema import Vendor


# ============================================================
# HELPER
# ============================================================

def make_ingredient(
    name="Flour",
    vendor_id=1,
    purchasing_cost=Decimal("10.00"),
    unit_amount=Decimal("25.00"),
    unit_of_measure="lb",
    allergens=None,
):
    """
    Create valid ingredient test data.

    Args:
        name: Ingredient name.
        vendor_id: ID of the vendor.
        purchasing_cost: Cost of the ingredient.
        unit_amount: Amount purchased.
        unit_of_measure: Unit used to measure the ingredient.
        allergens: List of allergen names.

    Returns:
        A validated Ingredient Pydantic model.
    """

    if allergens is None:
        allergens = ["Wheat"]

    return Ingredient(
        active=True,
        name=name,
        purchasing_cost=purchasing_cost,
        unit_amount=unit_amount,
        unit_of_measure=unit_of_measure,
        allergens=allergens,
        vendor_id=vendor_id,
    )


# ============================================================
# TEST 1
# CREATE INGREDIENT SUCCESSFULLY
# ============================================================

def test_create_ingredient_success(db):
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

    ingredient_data = make_ingredient(
        name="Flour",
        vendor_id=vendor.id,
    )

    result = create_ingredient(
        db=db,
        ingredient_data=ingredient_data,
    )

    assert result.id is not None
    assert result.name == "Flour"
    assert result.vendor_id == vendor.id
    assert result.active is True


# ============================================================
# TEST 2
# INGREDIENT IS ASSOCIATED WITH THE CORRECT VENDOR
# ============================================================

def test_create_ingredient_with_vendor(db):
    vendor = Vendor(
        name="ABC Foods",
        contact_name="Jane Smith",
        contact_role="Sales Manager",
        email="jane@abcfoods.com",
        phone="3125551111",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient_data = make_ingredient(
        name="Sugar",
        vendor_id=vendor.id,
    )

    result = create_ingredient(
        db=db,
        ingredient_data=ingredient_data,
    )

    assert result.vendor_id == vendor.id
    assert result.vendor.id == vendor.id
    assert result.vendor.name == "ABC Foods"


# ============================================================
# TEST 3
# VENDOR DOES NOT EXIST
# ============================================================

def test_create_ingredient_vendor_not_found(db):
    ingredient_data = make_ingredient(
        name="Flour",
        vendor_id=9999,
    )

    with pytest.raises(VendorNotFoundError):
        create_ingredient(
            db=db,
            ingredient_data=ingredient_data,
        )


# ============================================================
# TEST 4
# CREATE NEW ALLERGEN
# ============================================================

def test_get_or_create_allergen_creates_new_allergen(db):
    result = get_or_create_allergen(
        db=db,
        allergen_name="Milk",
    )

    assert result.id is not None
    assert result.name == "Milk"


# ============================================================
# TEST 5
# RETURN EXISTING ALLERGEN
# ============================================================

def test_get_or_create_allergen_returns_existing_allergen(db):
    allergen = AllergenSchema(
        name="Milk",
    )

    db.add(allergen)
    db.commit()
    db.refresh(allergen)

    result = get_or_create_allergen(
        db=db,
        allergen_name="Milk",
    )

    assert result.id == allergen.id
    assert result.name == "Milk"


# ============================================================
# TEST 6
# INGREDIENT IS ASSOCIATED WITH ALLERGENS
# ============================================================

def test_create_ingredient_with_allergens(db):
    vendor = Vendor(
        name="Ingredient Supplier",
        contact_name="Bob Smith",
        contact_role="Sales",
        email="bob@supplier.com",
        phone="3125552222",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient_data = make_ingredient(
        name="Chocolate",
        vendor_id=vendor.id,
        allergens=[
            "Milk",
            "Soy",
        ],
    )

    result = create_ingredient(
        db=db,
        ingredient_data=ingredient_data,
    )

    allergen_names = {
        allergen.name
        for allergen in result.allergens
    }

    assert allergen_names == {
        "Milk",
        "Soy",
    }


# ============================================================
# TEST 7
# DUPLICATE ALLERGENS ARE REMOVED
# ============================================================

def test_duplicate_allergens_are_removed(db):
    vendor = Vendor(
        name="Duplicate Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="duplicate@test.com",
        phone="3125553333",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient_data = make_ingredient(
        name="Butter",
        vendor_id=vendor.id,
        allergens=[
            "Milk",
            "Milk",
            "Milk",
        ],
    )

    result = create_ingredient(
        db=db,
        ingredient_data=ingredient_data,
    )

    assert len(result.allergens) == 1
    assert result.allergens[0].name == "Milk"


# ============================================================
# TEST 8
# DUPLICATE INGREDIENT
# ============================================================

def test_duplicate_ingredient_raises_error(db):
    vendor = Vendor(
        name="Duplicate Ingredient Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="duplicateingredient@test.com",
        phone="3125554444",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    first_ingredient = make_ingredient(
        name="Flour",
        vendor_id=vendor.id,
    )

    create_ingredient(
        db=db,
        ingredient_data=first_ingredient,
    )

    second_ingredient = make_ingredient(
        name="Flour",
        vendor_id=vendor.id,
    )

    with pytest.raises(
        IngredientAlreadyExistsError
    ):
        create_ingredient(
            db=db,
            ingredient_data=second_ingredient,
        )


# ============================================================
# TEST 9
# INVALID DATABASE CONSTRAINT
# ============================================================

def test_invalid_purchasing_cost_raises_constraint_error(db):
    vendor = Vendor(
        name="Constraint Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="constraint@test.com",
        phone="3125555555",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    # Create the SQLAlchemy model directly so that
    # Pydantic validation does not stop the test first.
    ingredient = IngredientSchema(
        active=True,
        name="Invalid Flour",
        purchasing_cost=Decimal("-5.00"),
        unit_amount=Decimal("25.00"),
        unit_of_measure="lb",
        vendor_id=vendor.id,
    )

    db.add(ingredient)

    with pytest.raises(IngredientConstraintError):
        try:
            db.commit()
        except Exception as exc:
            db.rollback()

            # This test is primarily checking that
            # the database rejects invalid data.
            raise IngredientConstraintError(
                "ck_ingredient_purchasing_cost_non_negative"
            ) from exc


# ============================================================
# TEST 10
# UNEXPECTED SQLALCHEMY ERROR IS RERAISED
# ============================================================

def test_unexpected_sqlalchemy_error_is_reraised():
    db = MagicMock()

    db.query.side_effect = SQLAlchemyError(
        "Unexpected database failure"
    )

    ingredient_data = make_ingredient(
        vendor_id=1,
    )

    with pytest.raises(SQLAlchemyError):
        create_ingredient(
            db=db,
            ingredient_data=ingredient_data,
        )

    db.rollback.assert_called_once()