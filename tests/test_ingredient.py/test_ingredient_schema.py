"""Tests for the SQLAlchemy ingredient database schema."""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from constants.INGREDIENT_TYPES import UnitOfMeasure
from database import Base
from ingredient.ingredient_schema import (
    AllergenSchema,
    IngredientSchema,
)
from vendor.vendor_schema import Vendor


ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TESTING_SESSION_LOCAL = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=ENGINE,
)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=ENGINE)

    session = TESTING_SESSION_LOCAL()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=ENGINE)


def create_vendor(db_session, vendor_id=1):
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

    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)

    return vendor


def create_ingredient(
    db_session,
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

    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(ingredient)

    return ingredient


def test_create_ingredient(db_session):
    """Test that a valid ingredient can be stored."""
    create_vendor(db_session)

    ingredient = create_ingredient(db_session)

    assert ingredient.id is not None
    assert ingredient.name == "Flour"
    assert ingredient.active is True
    assert ingredient.purchasing_cost == Decimal("10.00")
    assert ingredient.unit_amount == Decimal("25.00")
    assert ingredient.vendor_id == 1


def test_ingredient_active_defaults_to_true(db_session):
    """Test that active defaults to True."""
    create_vendor(db_session)

    ingredient = IngredientSchema(
        name="Sugar",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(ingredient)

    assert ingredient.active is True


def test_ingredient_name_cannot_be_null(db_session):
    """Test that the ingredient name cannot be NULL."""
    create_vendor(db_session)

    ingredient = IngredientSchema(
        name=None,
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db_session.add(ingredient)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_ingredient_name_cannot_be_blank(db_session):
    """Test that blank ingredient names are rejected."""
    create_vendor(db_session)

    ingredient = IngredientSchema(
        name="   ",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db_session.add(ingredient)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_purchasing_cost_cannot_be_negative(db_session):
    """Test that purchasing_cost cannot be less than zero."""
    create_vendor(db_session)

    ingredient = IngredientSchema(
        name="Butter",
        purchasing_cost=Decimal("-1.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db_session.add(ingredient)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_unit_amount_must_be_positive(db_session):
    """Test that unit_amount must be greater than zero."""
    create_vendor(db_session)

    ingredient = IngredientSchema(
        name="Milk",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("0.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    db_session.add(ingredient)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_ingredient_name_must_be_unique(db_session):
    """Test that two ingredients cannot have the same name."""
    create_vendor(db_session)

    create_ingredient(
        db_session,
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

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_ingredient_vendor_id_is_required(db_session):
    """Test that vendor_id cannot be NULL."""
    ingredient = IngredientSchema(
        active=True,
        name="Chocolate",
        purchasing_cost=Decimal("15.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=None,
    )

    db_session.add(ingredient)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_ingredient_can_have_multiple_allergens(db_session):
    """Test that an ingredient can have multiple allergens."""
    create_vendor(db_session)

    ingredient = create_ingredient(
        db_session,
        name="Peanut Flour",
    )

    peanut = AllergenSchema(name="Peanuts")
    gluten = AllergenSchema(name="Gluten")

    ingredient.allergens.append(peanut)
    ingredient.allergens.append(gluten)

    db_session.commit()
    db_session.refresh(ingredient)

    assert len(ingredient.allergens) == 2

    allergen_names = {
        allergen.name
        for allergen in ingredient.allergens
    }

    assert allergen_names == {
        "Peanuts",
        "Gluten",
    }


def test_vendor_has_ingredients_relationship(db_session):
    """Test that a vendor can access associated ingredients."""
    vendor = create_vendor(db_session)

    ingredient = create_ingredient(
        db_session,
        vendor_id=vendor.id,
        name="Flour",
    )

    db_session.refresh(vendor)

    assert len(vendor.ingredients) == 1
    assert vendor.ingredients[0].id == ingredient.id
    assert vendor.ingredients[0].name == "Flour"
    assert vendor.ingredients[0].vendor_id == vendor.id