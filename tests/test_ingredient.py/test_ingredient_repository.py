import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_repository import (
    create_ingredient,
    get_all_ingredients,
    get_or_create_allergen, 
    get_ingredient_by_id,
    update_ingredient
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

    result = create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    assert result.id is not None
    assert result.name == "Flour"
    assert result.vendor_id == vendor.id
    assert result.active is True


# ============================================================
# TEST 2
# INGREDIENT IS ASSOCIATED WITH CORRECT VENDOR
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

    result = create_ingredient(
        db,
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    assert result.vendor_id == vendor.id
    assert result.vendor.id == vendor.id
    assert result.vendor.name == "ABC Foods"


# ============================================================
# TEST 3
# VENDOR DOES NOT EXIST
# ============================================================

def test_create_ingredient_vendor_not_found(db):
    with pytest.raises(VendorNotFoundError):
        create_ingredient(
            db,
            make_ingredient(
                name="Flour",
                vendor_id=9999,
            ),
        )


# ============================================================
# TEST 4
# CREATE NEW ALLERGEN
# ============================================================

def test_get_or_create_allergen_creates_new_allergen(db):
    result = get_or_create_allergen(db, "Milk")

    assert result.id is not None
    assert result.name == "Milk"


# ============================================================
# TEST 5
# RETURN EXISTING ALLERGEN
# ============================================================

def test_get_or_create_allergen_returns_existing_allergen(db):
    allergen = AllergenSchema(name="Milk")

    db.add(allergen)
    db.commit()
    db.refresh(allergen)

    result = get_or_create_allergen(db, "Milk")

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

    result = create_ingredient(
        db,
        make_ingredient(
            name="Chocolate",
            vendor_id=vendor.id,
            allergens=["Milk", "Soy"],
        ),
    )

    assert {a.name for a in result.allergens} == {"Milk", "Soy"}


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

    result = create_ingredient(
        db,
        make_ingredient(
            name="Butter",
            vendor_id=vendor.id,
            allergens=["Milk", "Milk", "Milk"],
        ),
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

    create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    with pytest.raises(IngredientAlreadyExistsError):
        create_ingredient(
            db,
            make_ingredient(
                name="Flour",
                vendor_id=vendor.id,
            ),
        )


# ============================================================
# TEST 9
# INVALID DATABASE CONSTRAINT
# ============================================================

def test_invalid_purchasing_cost_raises_constraint_error(db):
    """Raise IngredientConstraintError when the database rejects a negative purchasing cost."""

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

    ingredient_data = make_ingredient(
        name="Invalid Flour",
        vendor_id=vendor.id,
    )

    # Bypass Pydantic validation so the database constraint
    # is responsible for rejecting the invalid value.
    ingredient_data.purchasing_cost = Decimal("-5.00")

    with pytest.raises(IngredientConstraintError):
        create_ingredient(
            db,
            ingredient_data,
        )

# ============================================================
# TEST 10
# UNEXPECTED SQLALCHEMY ERROR
# ============================================================

def test_unexpected_sqlalchemy_error_is_reraised():
    db = MagicMock()

    db.query.side_effect = SQLAlchemyError(
        "Unexpected database failure"
    )

    with pytest.raises(SQLAlchemyError):
        create_ingredient(
            db,
            make_ingredient(),
        )

    db.rollback.assert_called_once()
    # ============================================================
# TEST 11
# RETURN EMPTY LIST
# ============================================================

def test_get_all_ingredients_returns_empty_list(db):
    result = get_all_ingredients(db)

    assert result == []


# ============================================================
# TEST 12
# RETURN ONE INGREDIENT
# ============================================================

def test_get_all_ingredients_returns_one_ingredient(db):
    vendor = Vendor(
        name="Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="test@vendor.com",
        phone="3125556666",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    result = get_all_ingredients(db)

    assert len(result) == 1
    assert result[0].name == "Flour"


# ============================================================
# TEST 13
# RETURN MULTIPLE INGREDIENTS
# ============================================================

def test_get_all_ingredients_returns_multiple_ingredients(db):
    vendor = Vendor(
        name="Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="test2@vendor.com",
        phone="3125557777",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    create_ingredient(
        db,
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    result = get_all_ingredients(db)

    assert len(result) == 2
    assert {i.name for i in result} == {"Flour", "Sugar"}
# ============================================================
# TEST 14
# GET INGREDIENT BY ID
# ============================================================

def test_get_ingredient_by_id_returns_ingredient(db):
    """
    Test that an ingredient can be retrieved by its ID.
    """
    vendor = Vendor(
        name="Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="byid@test.com",
        phone="3125559999",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient = create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    result = get_ingredient_by_id(
        db,
        ingredient.id,
    )

    assert result is not None
    assert result.id == ingredient.id
    assert result.name == "Flour"


# ============================================================
# TEST 15
# INGREDIENT ID DOES NOT EXIST
# ============================================================

def test_get_ingredient_by_id_returns_none(db):
    """
    Test that None is returned when the ingredient ID does not exist.
    """
    result = get_ingredient_by_id(
        db,
        9999,
    )

    assert result is None


# ============================================================
# TEST 16
# GET CORRECT INGREDIENT WHEN MULTIPLE EXIST
# ============================================================

def test_get_ingredient_by_id_returns_correct_ingredient(db):
    """
    Test that the correct ingredient is returned when multiple
    ingredients exist.
    """
    vendor = Vendor(
        name="Test Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="multiple@test.com",
        phone="3125550000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    flour = create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    sugar = create_ingredient(
        db,
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    result = get_ingredient_by_id(
        db,
        sugar.id,
    )

    assert result is not None
    assert result.id == sugar.id
    assert result.name == "Sugar"
    assert result.id != flour.id
    # ============================================================
# TEST 17
# UPDATE INGREDIENT SUCCESSFULLY
# ============================================================

def test_update_ingredient_success(db):
    """
    Test that an existing ingredient is updated successfully.
    """
    vendor = Vendor(
        name="Update Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="update@test.com",
        phone="3125551234",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient = create_ingredient(
        db,
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    updated = update_ingredient(
        db,
        ingredient.id,
        make_ingredient(
            name="Bread Flour",
            vendor_id=vendor.id,
            purchasing_cost=Decimal("15.00"),
        ),
    )

    assert updated.id == ingredient.id
    assert updated.name == "Bread Flour"
    assert updated.purchasing_cost == Decimal("15.00")


# ============================================================
# TEST 18
# UPDATE INGREDIENT NOT FOUND
# ============================================================

def test_update_ingredient_returns_none_when_not_found(db):
    """
    Test that None is returned when the ingredient does not exist.
    """
    result = update_ingredient(
        db,
        9999,
        make_ingredient(),
    )

    assert result is None


# ============================================================
# TEST 19
# UPDATE INGREDIENT ALLERGENS
# ============================================================

def test_update_ingredient_updates_allergens(db):
    """
    Test that an ingredient's allergens are replaced during update.
    """
    vendor = Vendor(
        name="Allergen Vendor",
        contact_name="Test Person",
        contact_role="Sales",
        email="allergen@test.com",
        phone="3125555678",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient = create_ingredient(
        db,
        make_ingredient(
            name="Chocolate",
            vendor_id=vendor.id,
            allergens=["Milk"],
        ),
    )

    updated = update_ingredient(
        db,
        ingredient.id,
        make_ingredient(
            name="Chocolate",
            vendor_id=vendor.id,
            allergens=["Soy"],
        ),
    )

    assert {a.name for a in updated.allergens} == {"Soy"}