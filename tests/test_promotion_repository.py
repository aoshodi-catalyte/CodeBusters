import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from datetime import datetime

from datetime import datetime
from database import Base
from promotion.promotion_model import Promotion
from promotion.promotion_schema import PromotionSchema
from promotion.promotion_repository import PromotionRepository

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

def test_create_promotion_stores_start_datetime(db):
    """
    Test that the promotion start datetime is stored correctly.
    """
    repo = PromotionRepository(db)

    promotion = Promotion(
        active=True,
        promo_code="START2026",
        discount_percentage=15.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    result = repo.create_promotion(promotion)

    expected = datetime(
        2026,
        6,
        1,
        9,
        0,
    )

    assert result.start_datetime == expected

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