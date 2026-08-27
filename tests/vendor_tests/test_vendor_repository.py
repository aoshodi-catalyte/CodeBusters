import models

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base


from database import Base
from vendor.vendor_model import VendorBase
from vendor.vendor_schema import Vendor
from repositories.vendor_repository import VendorRepository
from ingredient.ingredient_schema import IngredientSchema


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_new_vendor(db_session):
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
    repo = VendorRepository(db_session)

    result = repo.get_all_vendors()

    assert result == []
    
def test_get_vendor_by_id_returns_vendor(db_session):
    vendor = Vendor(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bob@burger.com",
        phone="1234567896",
    )

    db_session.add(vendor)
    db_session.commit()
    db_session.refresh(vendor)

    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(vendor.id)

    assert result is not None
    assert result.id == vendor.id
    assert result.name == "Bob's Burgers"
    assert result.email == "bob@burger.com"

def test_get_vendor_by_id_returns_none_when_vendor_does_not_exist(db_session):
    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(999)

    assert result is None

def test_get_vendor_by_id_returns_correct_vendor(db_session):
    vendor_1 = Vendor(
        active=True,
        name="Bob's Burgers",
        contact_name="Bob Belcher",
        contact_role="CEO",
        email="bob@burger.com",
        phone="1234567896",
    )

    vendor_2 = Vendor(
        active=True,
        name="Acme Supplies",
        contact_name="Wile E. Coyote",
        contact_role="Manager",
        email="wile@acme.com",
        phone="9876543210",
    )

    db_session.add_all([vendor_1, vendor_2])
    db_session.commit()
    db_session.refresh(vendor_1)
    db_session.refresh(vendor_2)

    repo = VendorRepository(db_session)

    result = repo.get_vendor_by_id(vendor_2.id)

    assert result is not None
    assert result.id == vendor_2.id
    assert result.name == "Acme Supplies"
    assert result.email == "wile@acme.com"
