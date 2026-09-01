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

def test_get_vendor_by_id_returns_vendor(db_session):
    """Test retrieving a vendor by its ID."""
    vendor = Vendor(
        active=True,
        name="Vendor One",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@vendorone.com",
        phone="5551111111",
    )

    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)

    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(vendor.id)

    assert result is not None
    assert result.id == vendor.id
    assert result.name == "Vendor One"
    assert result.email == "john@vendorone.com"


def test_get_vendor_by_id_returns_correct_vendor_when_multiple_exist(db_session):
    """Test retrieving the correct vendor when multiple vendors exist."""
    vendor1 = Vendor(
        active=True,
        name="Vendor One",
        contact_name="John Doe",
        contact_role="Manager",
        email="john@vendorone.com",
        phone="5551111111",
    )

    vendor2 = Vendor(
        active=True,
        name="Vendor Two",
        contact_name="Jane Doe",
        contact_role="Owner",
        email="jane@vendortwo.com",
        phone="5552222222",
    )

    db_session.add_all([vendor1, vendor2])
    db_session.commit()
    db_session.refresh(vendor1)
    db_session.refresh(vendor2)

    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(vendor2.id)

    assert result is not None
    assert result.id == vendor2.id
    assert result.name == "Vendor Two"
    assert result.email == "jane@vendortwo.com"

    assert result.id != vendor1.id


def test_get_vendor_by_id_raises_not_found_exception(db_session):
    """Test that retrieving a nonexistent vendor raises VendorNotFoundException."""
    repo = VendorRepository(db_session)

    with pytest.raises(VendorNotFoundException) as exc_info:
        repo.get_vendor_by_id(999)

    assert exc_info.value.vendor_id == 999
    assert str(exc_info.value) == "Vendor with ID 999 was not found."


def test_get_vendor_by_id_raises_exception_for_negative_id(db_session):
    """Test that a nonexistent negative vendor ID raises VendorNotFoundException."""
    repo = VendorRepository(db_session)

    with pytest.raises(VendorNotFoundException) as exc_info:
        repo.get_vendor_by_id(-1)

    assert exc_info.value.vendor_id == -1
    assert str(exc_info.value) == "Vendor with ID -1 was not found."


def test_get_vendor_by_id_raises_exception_for_zero_id(db_session):
    """Test that a nonexistent zero vendor ID raises VendorNotFoundException."""
    repo = VendorRepository(db_session)

    with pytest.raises(VendorNotFoundException) as exc_info:
        repo.get_vendor_by_id(0)

    assert exc_info.value.vendor_id == 0
    assert str(exc_info.value) == "Vendor with ID 0 was not found."


def test_update_vendor_success(db):
    """Test that an existing vendor can be updated."""
    vendor = Vendor(
        active=True,
        name="Original Vendor",
        contact_name="John Smith",
        contact_role="Manager",
        email="original@example.com",
        phone="5551234567",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    vendor_data = VendorBase(
        active=False,
        name="Updated Vendor",
        contact_name="Jane Smith",
        contact_role="Owner",
        email="updated@example.com",
        phone="5559876543",
    )

    repo = VendorRepository(db)

    updated_vendor = repo.update_vendor(vendor.id, vendor_data)

    assert updated_vendor.id == vendor.id
    assert updated_vendor.active is False
    assert updated_vendor.name == "Updated Vendor"
    assert updated_vendor.contact_name == "Jane Smith"
    assert updated_vendor.contact_role == "Owner"
    assert updated_vendor.email == "updated@example.com"
    assert updated_vendor.phone == "5559876543"


def test_update_vendor_not_found(db):
    """Test that updating a nonexistent vendor raises an exception."""
    vendor_data = VendorBase(
        active=True,
        name="Updated Vendor",
        contact_name="John Smith",
        contact_role="Manager",
        email="updated@example.com",
        phone="5551234567",
    )

    repo = VendorRepository(db)

    with pytest.raises(VendorNotFoundException):
        repo.update_vendor(999999, vendor_data)


def test_update_vendor_all_fields(db):
    """Test that all vendor fields are updated correctly."""
    vendor = Vendor(
        active=True,
        name="Old Name",
        contact_name="Old Contact",
        contact_role="Old Role",
        email="old@example.com",
        phone="5551111111",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    vendor_data = VendorBase(
        active=False,
        name="New Name",
        contact_name="New Contact",
        contact_role="New Role",
        email="new@example.com",
        phone="5552222222",
    )

    repo = VendorRepository(db)

    repo.update_vendor(vendor.id, vendor_data)

    db.refresh(vendor)

    assert vendor.active is False
    assert vendor.name == "New Name"
    assert vendor.contact_name == "New Contact"
    assert vendor.contact_role == "New Role"
    assert vendor.email == "new@example.com"
    assert vendor.phone == "5552222222"


def test_update_vendor_duplicate_email(db):
    """Test that updating a vendor with an existing email raises an exception."""
    first_vendor = Vendor(
        active=True,
        name="First Vendor",
        contact_name="John Smith",
        contact_role="Manager",
        email="first@example.com",
        phone="5551111111",
    )

    second_vendor = Vendor(
        active=True,
        name="Second Vendor",
        contact_name="Jane Smith",
        contact_role="Owner",
        email="second@example.com",
        phone="5552222222",
    )

    db.add_all([first_vendor, second_vendor])
    db.commit()
    db.refresh(first_vendor)
    db.refresh(second_vendor)

    vendor_data = VendorBase(
        active=True,
        name="Second Vendor Updated",
        contact_name="Jane Smith",
        contact_role="Owner",
        email="first@example.com",
        phone="5552222222",
    )

    repo = VendorRepository(db)

    with pytest.raises(DuplicateVendorException):
        repo.update_vendor(second_vendor.id, vendor_data)


def test_update_vendor_persists_changes(db):
    """Test that the updated vendor is persisted in the database."""
    vendor = Vendor(
        active=True,
        name="Original Vendor",
        contact_name="John Smith",
        contact_role="Manager",
        email="original@example.com",
        phone="5551234567",
    )

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    vendor_id = vendor.id

    vendor_data = VendorBase(
        active=False,
        name="Persisted Vendor",
        contact_name="Jane Smith",
        contact_role="Owner",
        email="persisted@example.com",
        phone="5559876543",
    )

    repo = VendorRepository(db)

    repo.update_vendor(vendor_id, vendor_data)

    db.expire_all()

    saved_vendor = (
        db.query(Vendor)
        .filter(Vendor.id == vendor_id)
        .first()
    )

    assert saved_vendor is not None
    assert saved_vendor.name == "Persisted Vendor"
    assert saved_vendor.email == "persisted@example.com"
    assert saved_vendor.phone == "5559876543"
    assert saved_vendor.active is False


def test_update_vendor_duplicate_name_raises_correct_field(
    db_session,
):
    # Arrange
    existing_vendor = Vendor(
        active=True,
        name="Existing Vendor",
        contact_name="John Doe",
        contact_role="Manager",
        email="existing@example.com",
        phone="1111111111",
    )

    vendor_to_update = Vendor(
        active=True,
        name="Vendor To Update",
        contact_name="Jane Doe",
        contact_role="Manager",
        email="update@example.com",
        phone="2222222222",
    )

    db_session.add_all([existing_vendor, vendor_to_update])
    db_session.commit()

    repository = VendorRepository(db_session)

    vendor_data = VendorBase(
        active=True,
        name="Existing Vendor",  # Duplicate name
        contact_name="Jane Doe",
        contact_role="Manager",
        email="different@example.com",  # Not a duplicate email
        phone="2222222222",
    )

    # Act / Assert
    with pytest.raises(DuplicateVendorException) as exc_info:
        repository.update_vendor(
            vendor_to_update.id,
            vendor_data,
        )

    assert exc_info.value.field == "name"
    assert exc_info.value.value == "Existing Vendor"
