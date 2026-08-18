import pytest
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo
from promotion.promotion_model import Promotion
from pydantic import ValidationError

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

def test_promo_code_accepts_symbols():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER-2026!",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.promo_code == "SUMMER-2026!"

def test_promo_code_rejects_lowercase_letters():
    with pytest.raises(
        ValidationError,
        match="Promo code letters must be uppercase."
    ):
        Promotion(
            active=True,
            promo_code="summer2026",
            discount_percentage=20.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )    

def test_promo_code_rejects_leading_space():
    with pytest.raises(
        ValidationError,
        match="Promo code cannot start or end with a space"
    ):
        Promotion(
            active=True,
            promo_code=" SUMMER2026",
            discount_percentage=20.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_promo_code_rejects_trailing_space():
    with pytest.raises(
        ValidationError,
        match="Promo code cannot start or end with a space"
    ):
        Promotion(
            active=True,
            promo_code="SUMMER2026 ",
            discount_percentage=20.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_discount_percentage_accepts_positive_value():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=25.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.discount_percentage == 25.0

def test_discount_percentage_rejects_zero():
    with pytest.raises(ValidationError):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_discount_percentage_rejects_negative_value():
    with pytest.raises(ValidationError):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=-10.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_discount_percentage_accepts_100():
    promotion = Promotion(
        active=True,
        promo_code="FULLDISCOUNT",
        discount_percentage=100.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.discount_percentage == 100.0


def test_discount_percentage_rejects_over_100():
    with pytest.raises(
        ValidationError,
        match="Discount percentage cannot exceed 100%"
    ):
        Promotion(
            active=True,
            promo_code="INVALID100",
            discount_percentage=100.01,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_datetime_string_is_converted_to_datetime():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert isinstance(promotion.start_datetime, datetime)
    assert isinstance(promotion.end_datetime, datetime)

def test_datetime_uses_expected_month_day_year_format():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="12/25/2026 10:30 AM",
        end_datetime="12/31/2026 11:30 PM",
    )

    assert promotion.start_datetime.month == 12
    assert promotion.start_datetime.day == 25
    assert promotion.start_datetime.year == 2026


def test_datetime_accepts_am():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/01/2026 10:00 AM",
    )

    assert promotion.start_datetime.hour == 9


def test_datetime_accepts_pm():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 PM",
        end_datetime="06/01/2026 10:00 PM",
    )

    assert promotion.start_datetime.hour == 21

def test_datetime_rejects_wrong_format():
    with pytest.raises(
        ValidationError,
        match="Invalid date/time format"
    ):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=20.0,
            start_datetime="2026-06-01 09:00",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_timezone_is_added_to_naive_datetime():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.start_datetime.tzinfo is not None
    assert promotion.end_datetime.tzinfo is not None

def test_timezone_is_america_chicago():
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.start_datetime.tzinfo == CHICAGO_TZ
    assert promotion.end_datetime.tzinfo == CHICAGO_TZ

def test_existing_timezone_is_preserved():
    eastern_tz = ZoneInfo("America/New_York")

    start = datetime(
        2026,
        6,
        1,
        9,
        0,
        tzinfo=eastern_tz,
    )

    end = datetime(
        2026,
        6,
        30,
        11,
        59,
        tzinfo=eastern_tz,
    )

    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime=start,
        end_datetime=end,
    )

    assert promotion.start_datetime.tzinfo == eastern_tz
    assert promotion.end_datetime.tzinfo == eastern_tz

def test_end_datetime_cannot_be_before_start_datetime():
    with pytest.raises(
        ValidationError,
        match="End datetime must be after start datetime."
    ):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=20.0,
            start_datetime="06/30/2026 11:59 PM",
            end_datetime="06/01/2026 09:00 AM",
        )

def test_end_datetime_cannot_equal_start_datetime():
    with pytest.raises(
        ValidationError,
        match="End datetime must be after start datetime."
    ):
        Promotion(
            active=True,
            promo_code="SAME-TIME",
            discount_percentage=20.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/01/2026 09:00 AM",
        )