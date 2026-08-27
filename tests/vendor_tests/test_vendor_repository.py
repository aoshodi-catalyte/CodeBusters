import models

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from exceptions.vendor_exceptions import (
    DuplicateVendorException,
    VendorDeletionException,
    VendorNotFoundException,
)
from ingredient.ingredient_schema import IngredientSchema
from repositories.vendor_repository import VendorRepository
from vendor.vendor_model import VendorBase
from vendor.vendor_schema import Vendor


@pytest.fixture
def db_session():
    """Create a temporary database session for testing."""
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_new_vendor(db_session):
    """Test creating a new vendor."""
    repo = VendorRepository(db_session)

    vendor_data = VendorBase(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bestburgers@burger.com",
        phone="1234567896",
    )

    created_vendor = repo.create_new_vendor(vendor_data)

    assert created_vendor.id is not None
    assert created_vendor.name == "Bob's Burgers"
    assert created_vendor.email == "bestburgers@burger.com"


def test_vendor_ingredients_relationship(db_session):
    """Test the relationship between vendors and ingredients."""
    repo = VendorRepository(db_session)

    vendor = repo.create_new_vendor(
        VendorBase(
            active=True,
            name="Bob's Burgers Supply Co",
            contact_name="Bob Belcher",
            contact_role="CEO",
            email="supplyco@burger.com",
            phone="1234567896",
        )
    )

    ingredient = IngredientSchema(
        active=True,
        name="Ground Beef",
        purchasing_cost=12.50,
        unit_amount=5,
        unit_of_measure="lb",
        vendor_id=vendor.id,
    )

    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(vendor)

    assert len(vendor.ingredients) == 1
    assert vendor.ingredients[0].name == "Ground Beef"
    assert ingredient.vendor.name == "Bob's Burgers Supply Co"


def test_get_all_vendors_returns_all_vendors(db_session):
    """Test retrieving multiple vendors."""
    vendor1 = Vendor(
        active=True,
        name="Vendor One",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@vendorone.com",
        phone="555-1111",
    )

    vendor2 = Vendor(
        active=True,
        name="Vendor Two",
        contact_name="Jane Doe",
        contact_role="Owner",
        email="jane@vendortwo.com",
        phone="555-2222",
    )

    db_session.add_all([vendor1, vendor2])
    db_session.commit()

    repo = VendorRepository(db_session)

    result = repo.get_all_vendors()

    assert len(result) == 2
    assert result[0].name == "Vendor One"
    assert result[1].name == "Vendor Two"


def test_get_all_vendors_returns_single_vendor(db_session):
    """Test retrieving a single vendor."""
    vendor = Vendor(
        active=True,
        name="Vendor One",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@vendorone.com",
        phone="555-1111",
    )

    db_session.add(vendor)
    db_session.commit()

    repo = VendorRepository(db_session)

    result = repo.get_all_vendors()

    assert len(result) == 1
    assert result[0].id == vendor.id
    assert result[0].name == "Vendor One"


def test_get_all_vendors_returns_empty_list_when_no_vendors(db_session):
    """Test retrieving vendors when none exist."""
    repo = VendorRepository(db_session)

    result = repo.get_all_vendors()

    assert result == []


def test_vendor_not_found_exception():
    """Test the VendorNotFoundException."""
    exception = VendorNotFoundException(123)

    assert exception.vendor_id == 123
    assert str(exception) == "Vendor with ID 123 was not found."


def test_duplicate_vendor_exception():
    """Test the DuplicateVendorException."""
    exception = DuplicateVendorException(
        field="email",
        value="test@vendor.com",
    )

    assert exception.field == "email"
    assert exception.value == "test@vendor.com"
    assert (
        str(exception)
        == "Vendor with email 'test@vendor.com' already exists."
    )


def test_vendor_deletion_exception():
    """Test the VendorDeletionException."""
    exception = VendorDeletionException(123)

    assert exception.vendor_id == 123
    assert (
        str(exception)
        == "Vendor 123 cannot be deleted because it has associated records."
    )
