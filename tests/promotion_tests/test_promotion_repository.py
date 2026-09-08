import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from datetime import datetime

from database import Base
from promotion.promotion_model import Promotion
from promotion.promotion_schema import PromotionSchema
from repositories.promotion_repository import PromotionRepository

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

@pytest.fixture
def db():
    """Creates a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

def test_create_promotion(db):
    """
    Test that create_promotion creates and returns a
    PromotionSchema object.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    assert isinstance(result, PromotionSchema)

def test_create_promotion_generates_id(db):
    """
    Test that a newly created promotion receives a database-generated ID.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    assert result.id is not None

def test_create_promotion_stores_promo_code(db):
    """
    Test that the promotion code is stored correctly.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="SAVE20",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    assert result.promo_code == "SAVE20"

def test_create_promotion_stores_discount_percentage(db):
    """
    Test that the discount percentage is stored correctly.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="DISCOUNT25",
        discount_percentage=25.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    assert result.discount_percentage == 25.0

def test_create_promotion_stores_end_datetime(db):
    """
    Test that the promotion end datetime is stored correctly.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="END2026",
        discount_percentage=15.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    expected = datetime(
        2026,
        6,
        30,
        23,
        59,
    )

    assert result.end_datetime == expected

def test_deactivate_promotion(db):
    """
    Test that deactivate_promotion sets active to False for an
    existing promotion.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    created = repo.create_promotion(promotion)

    result = repo.deactivate_promotion(created.id)

    assert result is not None
    assert result.active is False


def test_deactivate_promotion_persists_to_database(db):
    """
    Test that deactivation is actually persisted in the database.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="FALLSALE",
        discount_percentage=15.0,
        start_datetime="09/01/2026 09:00 AM",
        end_datetime="09/30/2026 11:59 PM",
    )

    created = repo.create_promotion(promotion)

    repo.deactivate_promotion(created.id)

    stored_promotion = (
        db.query(PromotionSchema)
        .filter_by(id=created.id)
        .first()
    )

    assert stored_promotion.active is False


def test_deactivate_promotion_returns_none_when_not_found(db):
    """
    Test that deactivate_promotion returns None for a nonexistent ID.
    """
    repo = PromotionRepository(db)

    result = repo.deactivate_promotion(999)

    assert result is None


def test_deactivate_promotion_preserves_other_fields(db):
    """
    Test that deactivating a promotion does not alter its other fields.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="WINTER2026",
        discount_percentage=30.0,
        start_datetime="12/01/2026 09:00 AM",
        end_datetime="12/31/2026 11:59 PM",
    )

    created = repo.create_promotion(promotion)

    result = repo.deactivate_promotion(created.id)

    assert result.promo_code == "WINTER2026"
    assert result.discount_percentage == 30.0
    assert result.start_datetime == created.start_datetime
    assert result.end_datetime == created.end_datetime
    assert result.active is False


def test_update_promotion(db):
    """
    Test that update_promotion updates and returns an existing
    promotion's fields.
    """
    repo = PromotionRepository(db)

    original = Promotion(
        active=True,
        promo_code="ORIGINAL",
        discount_percentage=10.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    created = repo.create_promotion(original)

    updated_data = Promotion(
        active=False,
        promo_code="UPDATED",
        discount_percentage=50.0,
        start_datetime="07/01/2026 09:00 AM",
        end_datetime="07/31/2026 11:59 PM",
    )

    updated = repo.update_promotion(created.id, updated_data)

    assert updated.id == created.id
    assert updated.active is False
    assert updated.promo_code == "UPDATED"
    assert updated.discount_percentage == 50.0


def test_update_promotion_persists_to_database(db):
    """
    Test that an update is actually persisted in the database.
    """
    repo = PromotionRepository(db)

    original = Promotion(
        active=True,
        promo_code="PERSIST1",
        discount_percentage=10.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    created = repo.create_promotion(original)

    updated_data = Promotion(
        active=True,
        promo_code="PERSIST2",
        discount_percentage=25.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    repo.update_promotion(created.id, updated_data)

    stored_promotion = (
        db.query(PromotionSchema)
        .filter_by(id=created.id)
        .first()
    )

    assert stored_promotion.promo_code == "PERSIST2"
    assert stored_promotion.discount_percentage == 25.0


def test_update_promotion_returns_none_when_not_found(db):
    """
    Test that update_promotion returns None for a nonexistent ID.
    """
    repo = PromotionRepository(db)

    updated_data = Promotion(
        active=True,
        promo_code="NOTFOUND",
        discount_percentage=10.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.update_promotion(999, updated_data)

    assert result is None
