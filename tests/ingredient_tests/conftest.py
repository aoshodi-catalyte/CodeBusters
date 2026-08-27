import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base

# Import ALL models so SQLAlchemy knows about every table
from ingredient.ingredient_schema import (
AllergenSchema,
IngredientSchema,
)
from vendor.vendor_schema import Vendor
from ingredient.ingredient_model import IngredientOut, AllergenOut
from vendor.vendor_schema import Vendor
from vendor.vendor_model import VendorBase

# SQLite test database
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    """
    Create a fresh database session for each test.
    """

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)