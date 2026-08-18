import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from promotion.promotion_model import Promotion
from pydantic import ValidationError

CHICAGO_TZ = ZoneInfo("America/Chicago")

def test_valid_promotion():
    """
    Test that a valid promotion can be created successfully.

    Verifies that all required promotion fields are accepted and that
    the provided values are stored correctly. Also verifies that the
    datetime values are converted into timezone-aware datetime objects
    using the America/Chicago timezone.

    Returns:
        None: The test passes if the promotion is created with the
            expected values.
    """
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
    """
    Test that promo codes can contain numbers and symbols.

    Verifies that symbols and numbers are permitted in a promo code
    as long as the letters in the promo code are uppercase.

    Returns:
        None: The test passes if the promo code is accepted.
    """
    promotion = Promotion(
        active=True,
        promo_code="SUMMER-2026!",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.promo_code == "SUMMER-2026!"

def test_promo_code_rejects_lowercase_letters():
    """
    Test that promo codes containing lowercase letters are rejected.

    Verifies that the promo code validator raises a ValidationError
    when lowercase letters are provided.

    Returns:
        None: The test passes if the invalid promo code is rejected.
    """ 
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
    """
    Test that promo codes cannot begin with a space.

    Verifies that the promo code validator raises a ValidationError
    when the promo code contains a leading space.

    Returns:
        None: The test passes if the invalid promo code is rejected.
    """
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
    """
    Test that promo codes cannot end with a space.

    Verifies that the promo code validator raises a ValidationError
    when the promo code contains a trailing space.

    Returns:
        None: The test passes if the invalid promo code is rejected.
    """
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
    """
    Test that a positive discount percentage is accepted.

    Verifies that a discount percentage greater than zero can be used
    when creating a promotion.

    Returns:
        None: The test passes if the positive discount is accepted.
    """
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=25.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.discount_percentage == 25.0

def test_discount_percentage_rejects_zero():
    """
    Test that a discount percentage of zero is rejected.

    Verifies that the discount percentage must be greater than zero
    and that a zero value raises a Pydantic ValidationError.

    Returns:
        None: The test passes if the zero discount percentage is rejected.
    """
    with pytest.raises(ValidationError):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_discount_percentage_rejects_negative_value():
    """
    Test that a negative discount percentage is rejected.

    Verifies that the discount percentage cannot be less than zero.

    Returns:
        None: The test passes if the negative discount is rejected.
    """
    with pytest.raises(ValidationError):
        Promotion(
            active=True,
            promo_code="SUMMER2026",
            discount_percentage=-10.0,
            start_datetime="06/01/2026 09:00 AM",
            end_datetime="06/30/2026 11:59 PM",
        )

def test_discount_percentage_accepts_100():
    """
    Test that a discount percentage of exactly 100 is accepted.

    Verifies that 100 percent is the maximum valid discount and can
    be used when creating a promotion.

    Returns:
        None: The test passes if a 100 percent discount is accepted.
    """
    promotion = Promotion(
        active=True,
        promo_code="FULLDISCOUNT",
        discount_percentage=100.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/30/2026 11:59 PM",
    )

    assert promotion.discount_percentage == 100.0


def test_discount_percentage_rejects_over_100():
    """
    Test that a discount percentage greater than 100 is rejected.

    Verifies that the promotion discount cannot exceed 100 percent
    and that a value greater than 100 raises a Pydantic ValidationError.

    Returns:
        None: The test passes if the discount percentage above 100
            is rejected.
    """
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
    """
    Test that datetime strings are converted to datetime objects.

    Verifies that the start and end datetime strings supplied in the
    expected user-friendly format are converted into Python datetime
    objects.

    Returns:
        None: The test passes if both datetime fields are datetime objects.
    """
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
    """
    Test that datetime strings use the expected MM/DD/YYYY format.

    Verifies that the month, day, and year are correctly parsed from
    a datetime string using the expected input format.

    Returns:
        None: The test passes if the datetime components are parsed correctly.
    """
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
    """
    Test that datetime strings containing AM are parsed correctly.

    Verifies that a morning time is converted to the correct 24-hour
    datetime representation.

    Returns:
        None: The test passes if the AM time is parsed correctly.
    """
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 AM",
        end_datetime="06/01/2026 10:00 AM",
    )

    assert promotion.start_datetime.hour == 9


def test_datetime_accepts_pm():
    """
    Test that datetime strings containing PM are parsed correctly.

    Verifies that an afternoon or evening time is converted to the
    correct 24-hour datetime representation.

    Returns:
        None: The test passes if the PM time is parsed correctly.
    """
    promotion = Promotion(
        active=True,
        promo_code="SUMMER2026",
        discount_percentage=20.0,
        start_datetime="06/01/2026 09:00 PM",
        end_datetime="06/01/2026 10:00 PM",
    )

    assert promotion.start_datetime.hour == 21

def test_datetime_rejects_wrong_format():
    """
    Test that incorrectly formatted datetime strings are rejected.

    Verifies that the datetime validator raises a ValidationError when
    a datetime does not follow the required MM/DD/YYYY HH:MM AM/PM format.

    Returns:
        None: The test passes if the incorrectly formatted datetime
            is rejected.
    """
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
    """
    Test that a timezone is added to datetime values without timezone
    information.

    Verifies that both the start and end datetime values become
    timezone-aware when timezone information is not provided.

    Returns:
        None: The test passes if both datetime values contain timezone
            information.
    """
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
    """
    Test that naive datetime values receive the America/Chicago timezone.

    Verifies that the promotion model assigns the expected Chicago
    timezone to datetime values that do not already contain timezone
    information.

    Returns:
        None: The test passes if both datetime values use the
            America/Chicago timezone.
    """
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
    """
    Test that an existing timezone is preserved.

    Verifies that timezone information already provided on a datetime
    is not replaced with the America/Chicago timezone.

    Returns:
        None: The test passes if the existing timezone is preserved.
    """
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
    """
    Test that the promotion end datetime cannot occur before the start
    datetime.

    Verifies that the date validation raises a ValidationError when
    the promotion's end datetime occurs earlier than its start datetime.

    Returns:
        None: The test passes if the invalid datetime range is rejected.
    """
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
    """
    Test that the promotion end datetime cannot equal the start datetime.

    Verifies that a promotion must have a positive duration and therefore
    cannot have identical start and end datetime values.

    Returns:
        None: The test passes if equal datetime values are rejected.
    """
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