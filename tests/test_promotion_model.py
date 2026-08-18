import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from promotion.promotion_model import Promotion

CHICAGO_TZ = ZoneInfo("America/Chicago")

def test_valid_promotion():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.active is True
    assert promotion.promo_code == "SUMMER2026"
    assert promotion.discount_percentage == 20.0
    assert promotion.start_datetime == datetime(
        2026, 6, 1, 9, 0, tzinfo=CHICAGO_TZ
    )
    assert promotion.end_datetime == datetime(
        2026, 6, 30, 23, 59, tzinfo=CHICAGO_TZ
    )

