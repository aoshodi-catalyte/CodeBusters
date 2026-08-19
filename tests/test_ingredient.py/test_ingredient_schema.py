"""Tests for the SQLAlchemy ingredient schema."""

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

TESTING_SESSION_LOCAL = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)

    database_session = TESTING_SESSION_LOCAL()

    try:
        yield database_session
    finally:
        database_session.close()
        Base.metadata.drop_all(bind=engine)


# ============================================================
# TEST DATA HELPERS
# ============================================================

def create_vendor(session, vendor_id=1):
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

    session.add(vendor)
    session.commit()
    session.refresh(vendor)

    return vendor


def create_ingredient(
    session,
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

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    return ingredient


# ============================================================
# 1. INGREDIENT CAN BE CREATED
# ============================================================

def test_create_ingredient(session):
    """Test that a valid ingredient can be stored in the database."""
    create_vendor(session)

    ingredient = create_ingredient(session)

    assert ingredient.id is not None
    assert ingredient.name == "Flour"
    assert ingredient.active is True
    assert ingredient.purchasing_cost == Decimal("10.00")
    assert ingredient.unit_amount == Decimal("25.00")
    assert ingredient.vendor_id == 1


# ============================================================
# 2. ACTIVE DEFAULTS TO TRUE
# ============================================================

def test_ingredient_active_defaults_to_true(session):
    """Test that active defaults to True when no value is provided."""
    create_vendor(session)

    ingredient = IngredientSchema(
        name="Sugar",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    session.add(ingredient)
    session.commit()
    session.refresh(ingredient)

    assert ingredient.active is True


# ============================================================
# 3. INGREDIENT NAME CANNOT BE NULL
# ============================================================

def test_ingredient_name_cannot_be_null(session):
    """Test that the ingredient name cannot be NULL."""
    create_vendor(session)

    ingredient = IngredientSchema(
        name=None,
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    session.add(ingredient)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 4. INGREDIENT NAME CANNOT BE BLANK
# ============================================================

def test_ingredient_name_cannot_be_blank(session):
    """Test that blank ingredient names violate the database constraint."""
    create_vendor(session)

    ingredient = IngredientSchema(
        name="   ",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    session.add(ingredient)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 5. PURCHASING COST CANNOT BE NEGATIVE
# ============================================================

def test_purchasing_cost_cannot_be_negative(session):
    """Test that purchasing_cost cannot be less than zero."""
    create_vendor(session)

    ingredient = IngredientSchema(
        name="Butter",
        purchasing_cost=Decimal("-1.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    session.add(ingredient)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 6. UNIT AMOUNT MUST BE GREATER THAN ZERO
# ============================================================

def test_unit_amount_must_be_positive(session):
    """Test that unit_amount must be greater than zero."""
    create_vendor(session)

    ingredient = IngredientSchema(
        name="Milk",
        purchasing_cost=Decimal("5.00"),
        unit_amount=Decimal("0.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=1,
    )

    session.add(ingredient)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 7. INGREDIENT NAME MUST BE UNIQUE
# ============================================================

def test_ingredient_name_must_be_unique(session):
    """Test that two ingredients cannot have the same name."""
    create_vendor(session)

    create_ingredient(
        session,
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

    session.add(duplicate)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 8. INGREDIENT MUST HAVE A VALID VENDOR
# ============================================================

def test_ingredient_vendor_id_is_required(session):
    """Test that vendor_id cannot be NULL."""
    ingredient = IngredientSchema(
        active=True,
        name="Chocolate",
        purchasing_cost=Decimal("15.00"),
        unit_amount=Decimal("10.00"),
        unit_of_measure=next(iter(UnitOfMeasure)),
        vendor_id=None,
    )

    session.add(ingredient)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ============================================================
# 9. INGREDIENT AND ALLERGEN MANY-TO-MANY RELATIONSHIP
# ============================================================

def test_ingredient_can_have_multiple_allergens(session):
    """Test that an ingredient can have multiple allergens."""
    create_vendor(session)

    ingredient = create_ingredient(
        session,
        name="Peanut Flour",
    )

    peanut = AllergenSchema(name="Peanuts")
    gluten = AllergenSchema(name="Gluten")

    ingredient.allergens.append(peanut)
    ingredient.allergens.append(gluten)

    session.commit()
    session.refresh(ingredient)

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
# 10. VENDOR AND INGREDIENT RELATIONSHIP
# ============================================================

def test_vendor_has_ingredients_relationship(session):
    """Test that a vendor can access its associated ingredients."""
    vendor = create_vendor(session)

    ingredient = create_ingredient(
        session,
        vendor_id=vendor.id,
        name="Flour",
    )

    session.refresh(vendor)

    assert len(vendor.ingredients) == 1
    assert vendor.ingredients[0].id == ingredient.id
    assert vendor.ingredients[0].name == "Flour"
    assert vendor.ingredients[0].vendor_id == vendor.id