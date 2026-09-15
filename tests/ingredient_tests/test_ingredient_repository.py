"""Tests for the ingredient repository."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from constants.entity_types import EntityType
from exceptions.ingredient_exceptions import (
    IngredientAlreadyExistsError,
    IngredientAlreadyInactiveError,
    IngredientConstraintError,
    IngredientNotFoundError,
    VendorNotFoundError,
)
from ingredient.ingredient_model import Ingredient
from ingredient.ingredient_schema import AllergenSchema, IngredientSchema
from repositories.ingredient_repository import (
    IngredientRepository,
    get_or_create_allergen,
)
from vendor.vendor_schema import Vendor


def make_ingredient(
    name="Flour",
    vendor_id=1,
    purchasing_cost=Decimal("10.00"),
    unit_amount=Decimal("25.00"),
    unit_of_measure="lb",
    allergens=None,
):
    """Create an Ingredient object for testing."""
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


def test_create_ingredient_success(db):
    """Test that an ingredient can be created successfully."""
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

    repo = IngredientRepository(db)

    result = repo.create_ingredient(
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    assert result.id is not None
    assert result.name == "Flour"
    assert result.vendor_id == vendor.id
    assert result.active is True


def test_create_ingredient_with_vendor(db):
    """Test that an ingredient is associated with the correct vendor."""
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

    repo = IngredientRepository(db)

    result = repo.create_ingredient(
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    assert result.vendor_id == vendor.id
    assert result.vendor.id == vendor.id
    assert result.vendor.name == "ABC Foods"


def test_create_ingredient_vendor_not_found(db):
    """Test that a missing vendor raises VendorNotFoundError."""
    with pytest.raises(VendorNotFoundError):
        repo = IngredientRepository(db)

        repo.create_ingredient(
            make_ingredient(
                name="Flour",
                vendor_id=9999,
            ),
        )


def test_get_or_create_allergen_creates_new_allergen(db):
    """Test that a missing allergen is created."""
    result = get_or_create_allergen(db, "Milk")

    assert result.id is not None
    assert result.name == "Milk"


def test_get_or_create_allergen_returns_existing_allergen(db):
    """Test that an existing allergen is returned."""
    allergen = AllergenSchema(name="Milk")

    db.add(allergen)
    db.commit()
    db.refresh(allergen)

    result = get_or_create_allergen(db, "Milk")

    assert result.id == allergen.id
    assert result.name == "Milk"


def test_create_ingredient_with_allergens(db):
    """Test that an ingredient is associated with its allergens."""
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

    repo = IngredientRepository(db)

    result = repo.create_ingredient(
        make_ingredient(
            name="Chocolate",
            vendor_id=vendor.id,
            allergens=["Milk", "Soy"],
        ),
    )

    assert {allergen.name for allergen in result.allergens} == {
        "Milk",
        "Soy",
    }


def test_duplicate_allergens_are_removed(db):
    """Test that duplicate allergens are removed."""
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

    repo = IngredientRepository(db)

    result = repo.create_ingredient(
        make_ingredient(
            name="Butter",
            vendor_id=vendor.id,
            allergens=["Milk", "Milk", "Milk"],
        ),
    )

    assert len(result.allergens) == 1
    assert result.allergens[0].name == "Milk"


def test_duplicate_ingredient_raises_error(db):
    """Test that duplicate ingredient names raise an exception."""
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

    repo = IngredientRepository(db)

    repo.create_ingredient(
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    with pytest.raises(IngredientAlreadyExistsError):
        repo.create_ingredient(
            make_ingredient(
                name="Flour",
                vendor_id=vendor.id,
            ),
        )


def test_invalid_purchasing_cost_raises_constraint_error(db):
    """Test that a negative purchasing cost violates the database constraint."""
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

    ingredient_data.purchasing_cost = Decimal("-5.00")

    with pytest.raises(IngredientConstraintError):
        repo = IngredientRepository(db)
        repo.create_ingredient(ingredient_data)


def test_unexpected_sqlalchemy_error_is_reraised():
    """Test that unexpected SQLAlchemy errors are re-raised."""
    db = MagicMock()
    db.query.side_effect = SQLAlchemyError(
        "Unexpected database failure"
    )

    repo = IngredientRepository(db)

    with pytest.raises(SQLAlchemyError):
        repo.create_ingredient(make_ingredient())

    db.rollback.assert_called_once()


def test_update_ingredient_success(db):
    """Test that an existing ingredient can be updated successfully."""
    vendor = Vendor(
        name="Original Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="original@test.com",
        phone="3125551000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    ingredient = repo.create_ingredient(
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
            purchasing_cost=Decimal("10.00"),
            unit_amount=Decimal("25.00"),
        ),
    )

    updated_data = make_ingredient(
        name="Whole Wheat Flour",
        vendor_id=vendor.id,
        purchasing_cost=Decimal("12.50"),
        unit_amount=Decimal("30.00"),
        unit_of_measure="kg",
        allergens=["Wheat"],
    )

    result = repo.update_ingredient(
        ingredient_id=ingredient.id,
        ingredient_data=updated_data,
    )

    assert result is not None
    assert result.id == ingredient.id
    assert result.name == "Whole Wheat Flour"
    assert result.purchasing_cost == Decimal("12.50")
    assert result.unit_amount == Decimal("30.00")
    assert result.vendor_id == vendor.id
    assert result.active is True


def test_update_ingredient_is_persisted(db):
    """Test that ingredient updates are persisted."""
    vendor = Vendor(
        name="Persistence Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="persist@test.com",
        phone="3125552000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    ingredient = repo.create_ingredient(
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    updated_data = make_ingredient(
        name="Brown Sugar",
        vendor_id=vendor.id,
        purchasing_cost=Decimal("15.00"),
        unit_amount=Decimal("20.00"),
    )

    repo.update_ingredient(
        ingredient_id=ingredient.id,
        ingredient_data=updated_data,
    )

    db.expire_all()

    persisted = repo.get_ingredient_by_id(
        ingredient_id=ingredient.id,
    )

    assert persisted is not None
    assert persisted.name == "Brown Sugar"
    assert persisted.purchasing_cost == Decimal("15.00")
    assert persisted.unit_amount == Decimal("20.00")


def test_update_ingredient_not_found(db):
    """Test that updating a nonexistent ingredient raises an error."""
    vendor = Vendor(
        name="Missing Ingredient Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="missing@test.com",
        phone="3125553000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient_data = make_ingredient(
        name="Flour",
        vendor_id=vendor.id,
    )

    repo = IngredientRepository(db)

    with pytest.raises(IngredientNotFoundError) as exc_info:
        repo.update_ingredient(
            ingredient_id=9999,
            ingredient_data=ingredient_data,
        )

    assert str(exc_info.value) == (
        "Ingredient with ID 9999 does not exist."
    )


def test_update_ingredient_replaces_allergens(db):
    """Test that updating an ingredient replaces its allergens."""
    vendor = Vendor(
        name="Allergen Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="allergen@test.com",
        phone="3125554000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    ingredient = repo.create_ingredient(
        make_ingredient(
            name="Chocolate",
            vendor_id=vendor.id,
            allergens=["Milk", "Soy"],
        ),
    )

    assert {allergen.name for allergen in ingredient.allergens} == {
        "Milk",
        "Soy",
    }

    updated_data = make_ingredient(
        name="Dark Chocolate",
        vendor_id=vendor.id,
        allergens=["Soy", "Wheat"],
    )

    result = repo.update_ingredient(
        ingredient_id=ingredient.id,
        ingredient_data=updated_data,
    )

    assert result is not None
    assert {allergen.name for allergen in result.allergens} == {
        "Soy",
        "Wheat",
    }


def test_update_ingredient_duplicate_name_raises_error(db):
    """Test that updating to an existing name raises an error."""
    vendor = Vendor(
        name="Duplicate Update Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="duplicateupdate@test.com",
        phone="3125555000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    repo.create_ingredient(
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    second_ingredient = repo.create_ingredient(
        make_ingredient(
            name="Sugar",
            vendor_id=vendor.id,
        ),
    )

    with pytest.raises(IngredientAlreadyExistsError):
        repo.update_ingredient(
            ingredient_id=second_ingredient.id,
            ingredient_data=make_ingredient(
                name="Flour",
                vendor_id=vendor.id,
            ),
        )


def test_update_ingredient_vendor_not_found(db):
    """Test that updating to a nonexistent vendor raises an error."""
    vendor = Vendor(
        name="Vendor Update Test",
        contact_name="John Doe",
        contact_role="Sales",
        email="vendorupdate@test.com",
        phone="3125556000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    ingredient = repo.create_ingredient(
        make_ingredient(
            name="Flour",
            vendor_id=vendor.id,
        ),
    )

    with pytest.raises(VendorNotFoundError):
        repo.update_ingredient(
            ingredient_id=ingredient.id,
            ingredient_data=make_ingredient(
                name="Updated Flour",
                vendor_id=9999,
            ),
        )


def test_soft_delete_ingredient_success(db):
    """Test that an active ingredient can be soft deleted."""
    vendor = Vendor(
        name="Soft Delete Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="softdelete@test.com",
        phone="3125557000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    repo = IngredientRepository(db)

    ingredient = repo.create_ingredient(
        make_ingredient(
            name="Vanilla Extract",
            vendor_id=vendor.id,
        ),
    )

    audit_db = MagicMock()

    with patch(
        "repositories.ingredient_repository.AuditRepository"
    ) as audit_repository_class:
        audit_repo = audit_repository_class.return_value

        result = repo.__class__(
            db=db,
            audit_db=audit_db,
        ).soft_delete_ingredient(
            ingredient_id=ingredient.id,
            employee_id=123,
        )

        assert result is not None
        assert result.id == ingredient.id
        assert result.active is False

        audit_repo.record_deactivation.assert_called_once_with(
            item_id=ingredient.id,
            item_name=ingredient.name,
            user="123",
            item_type=EntityType.INGREDIENT,
        )


def test_soft_delete_ingredient_not_found(db):
    """Test that soft deleting a nonexistent ingredient returns None."""
    repo = IngredientRepository(db)

    result = repo.soft_delete_ingredient(
        ingredient_id=99999,
        employee_id=123,
    )

    assert result is None


def test_soft_delete_already_inactive_ingredient(db):
    """Test that an already inactive ingredient cannot be deactivated again."""
    vendor = Vendor(
        name="Already Inactive Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="alreadyinactive@test.com",
        phone="3125558000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    ingredient = IngredientSchema(
        active=False,
        name="Inactive Ingredient",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("1.00"),
        unit_of_measure="kg",
        vendor_id=vendor.id,
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    repo = IngredientRepository(db)

    with pytest.raises(IngredientAlreadyInactiveError):
        repo.soft_delete_ingredient(
            ingredient_id=ingredient.id,
            employee_id=123,
        )


def test_get_deactivated_ingredients(db):
    """Test that only inactive ingredients are returned."""
    vendor = Vendor(
        name="Deactivated List Vendor",
        contact_name="John Doe",
        contact_role="Sales",
        email="deactivatedlist@test.com",
        phone="3125559000",
        active=True,
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    active_ingredient = IngredientSchema(
        active=True,
        name="Active Ingredient",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("1.00"),
        unit_of_measure="kg",
        vendor_id=vendor.id,
    )

    inactive_ingredient = IngredientSchema(
        active=False,
        name="Inactive Ingredient",
        purchasing_cost=Decimal("6.00"),
        unit_amount=Decimal("1.00"),
        unit_of_measure="kg",
        vendor_id=vendor.id,
    )

    db.add_all(
        [
            active_ingredient,
            inactive_ingredient,
        ]
    )
    db.commit()

    repo = IngredientRepository(db)

    result = repo.get_deactivated_ingredients()

    assert len(result) == 1
    assert result[0].id == inactive_ingredient.id
    assert result[0].active is False


def test_soft_delete_ingredient_sqlalchemy_error():
    """Test that SQLAlchemy errors are rolled back and re-raised."""
    db = MagicMock()
    db.query.side_effect = SQLAlchemyError(
        "Unexpected database failure"
    )

    repo = IngredientRepository(db)

    with pytest.raises(SQLAlchemyError):
        repo.soft_delete_ingredient(
            ingredient_id=1,
            employee_id=123,
        )

    db.rollback.assert_called_once()
