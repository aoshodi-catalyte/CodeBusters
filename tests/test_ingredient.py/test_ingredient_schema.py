"""Tests for the SQLAlchemy ingredient model."""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from constants.INGREDIENT_TYPES import UnitOfMeasure
from database import Base
from ingredient.ingredient_schema import AllergenSchema, IngredientSchema
from vendor.vendor_schema import Vendor


# ============================================================
# TEST DATABASE
# ============================================================

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST DATA HELPERS
# ============================================================

def create_vendor(db, vendor_id=1):
    """Create a vendor that can be used by an ingredient."""
    vendor = Vendor(
        id=vendor_id,
        active=True,
        name=f"Test Vendor {vendor_id}",
        contact_name="John Smith",
        contact_role="Sales",
        email=f"vendor{vendor_id}@example.com",
        phone="3125551234",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return vendor


def create_ingredient(
    db,
    vendor_id=1,
    name="Flour",
    purchasing_cost=Decimal("10.00"),
    unit_amount=Decimal("25.00"),
):
    """Create a valid ingredient for testing."""
    ingredient = IngredientSchema(
        active=True,
        name=name,
        purchasing_cost=purchasing_cost,
        unit_amount=unit_amount,
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=vendor_id,
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    return ingredient


# ============================================================
# INGREDIENT CREATION
# ============================================================

def test_create_ingredient(db):
    """Test that a valid ingredient can be stored in the database."""
    create_vendor(db)

    ingredient = create_ingredient(db)

    assert ingredient.id is not None
    assert ingredient.name == "Flour"
    assert ingredient.active is True
    assert ingredient.purchasing_cost == Decimal("10.00")
    assert ingredient.unit_amount == Decimal("25.00")
    assert ingredient.vendor_id == 1


# ============================================================
# ACTIVE DEFAULT
# ============================================================

def test_ingredient_active_defaults_to_true(db):
    """Test that active defaults to True when no value is provided."""
    create_vendor(db)

    ingredient = IngredientSchema(
        name="Sugar",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)

    assert ingredient.active is True


# ============================================================
# NAME CONSTRAINTS
# ============================================================

def test_ingredient_name_cannot_be_null(db):
    """Test that the ingredient name cannot be NULL."""
    create_vendor(db)

    ingredient = IngredientSchema(
        name=None,
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(ingredient)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_ingredient_name_cannot_be_blank(db):
    """Test that blank ingredient names violate the database constraint."""
    create_vendor(db)

    ingredient = IngredientSchema(
        name="   ",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(ingredient)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


# ============================================================
# NUMERIC CONSTRAINTS
# ============================================================

def test_purchasing_cost_cannot_be_negative(db):
    """Test that purchasing_cost cannot be less than zero."""
    create_vendor(db)

    ingredient = IngredientSchema(
        name="Butter",
        purchasing_cost=Decimal("-1.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(ingredient)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_unit_amount_must_be_positive(db):
    """Test that unit_amount must be greater than zero."""
    create_vendor(db)

    ingredient = IngredientSchema(
        name="Milk",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("0.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(ingredient)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


# ============================================================
# UNIQUE CONSTRAINT
# ============================================================

def test_ingredient_name_must_be_unique(db):
    """Test that two ingredients cannot have the same name."""
    create_vendor(db)

    create_ingredient(
        db,
        name="Flour",
    )

    duplicate = IngredientSchema(
        active=True,
        name="Flour",
        purchasing_cost=Decimal("12.00"),
        unit_amount=Decimal("20.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db.add(duplicate)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


# ============================================================
# VENDOR CONSTRAINT
# ============================================================

def test_ingredient_vendor_id_is_required(db):
    """Test that vendor_id cannot be NULL."""
    ingredient = IngredientSchema(
        active=True,
        name="Chocolate",
        purchasing_cost=Decimal("15.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=None,
    )

    db.add(ingredient)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


# ============================================================
# INGREDIENT/ALLERGEN RELATIONSHIP
# ============================================================

def test_ingredient_can_have_multiple_allergens(db):
    """Test that an ingredient can have multiple allergens."""
    create_vendor(db)

    ingredient = create_ingredient(
        db,
        name="Peanut Flour",
    )

    peanut = AllergenSchema(name="Peanuts")
    gluten = AllergenSchema(name="Gluten")

    ingredient.allergens.append(peanut)
    ingredient.allergens.append(gluten)

    db.commit()
    db.refresh(ingredient)

    assert len(ingredient.allergens) == 2

    allergen_names = {
        allergen.name
        for allergen in ingredient.allergens
    }

    assert allergen_names == {
        "Peanuts",
        "Gluten",
    }


# ============================================================
# VENDOR/INGREDIENT RELATIONSHIP
# ============================================================

def test_vendor_has_ingredients_relationship(db):
    """Test that a vendor can access its associated ingredients."""
    vendor = create_vendor(db)

    ingredient = create_ingredient(
        db,
        vendor_id=vendor.id,
        name="Flour",
    )

    db.refresh(vendor)

    assert len(vendor.ingredients) == 1
    assert vendor.ingredients[0].id == ingredient.id
    assert vendor.ingredients[0].name == "Flour"
    assert vendor.ingredients[0].vendor_id == vendor.id