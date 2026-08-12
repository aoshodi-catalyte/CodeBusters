from sqlalchemy.orm import sessionmaker
from baked_good.baked_good_repository import BakedGoodRepository
from baked_good.baked_good_model import BakedGood
import pytest

from database import Base, engine
from tests.test_customer_router import TestingSessionLocal

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture
def db():
    """Creates a fresh in-memory DB for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_baked_good_repository():
    """
    Tests that a baked good can be created and stored in the repository.

    Creates a BakedGoodRepository and a valid BakedGood object, then adds
    the baked good to the repository. Verifies that the baked good is
    stored in the repository and that the repository contains one item.

    Args:
        None

    Returns:
        None
    """
    
    repository = BakedGoodRepository(db)

    baked_good = BakedGood (
        id=1,
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
        vendor_id=1
    )

    repository.create_baked_good(baked_good)

    assert baked_good in repository.baked_goods
    assert len(repository.baked_goods) == 1

    def test_create_baked_good_returns_baked_good():
        """
        Tests that creating a baked good returns the same BakedGood object.

        Creates a BakedGoodRepository and a valid BakedGood object, then passes
        the baked good to the create_baked_good method. Verifies that the
        returned object is equal to the baked good that was provided.

        Args:
            None

        Returns:
            None
        """

        repository = BakedGoodRepository()

        baked_good = BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=5.00,
            retail_price=10.00,
            vendor_id=1
        )

        result = repository.create_baked_good(baked_good)

        assert result == baked_good
