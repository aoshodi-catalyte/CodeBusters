from sqlalchemy import inspect
from promotion.promotion_schema import PromotionSchema

def test_promotion_columns_exist():
    """
    Test that the PromotionSchema contains all required database columns.

    Inspects the PromotionSchema table and verifies that the expected
    columns are present, including the promotion identifier, active status,
    promo code, discount percentage, and start and end datetimes.

    Returns:
        None: The test passes if the schema contains exactly the expected
            columns.
    """
    columns = inspect(PromotionSchema).columns

    expected_columns = {
        "id",
        "active",
        "promo_code",
        "discount_percentage",
        "start_datetime",
        "end_datetime",
    }

    assert set(columns.keys()) == expected_columns


def test_id_is_primary_key():
    """
    Test that the promotion ID column is configured as the primary key.

    Verifies that the id column in the PromotionSchema table is marked
    as a primary key.

    Returns:
        None: The test passes if the id column is a primary key.
    """
    column = PromotionSchema.__table__.c.id

    assert column.primary_key is True

def test_promo_code_is_unique():
    """
    Test that the promotion code column is configured as unique.

    Verifies that the promo_code column has a unique constraint so that
    duplicate promotion codes cannot be stored in the database.

    Returns:
        None: The test passes if the promo_code column is unique.
    """
    column = PromotionSchema.__table__.c.promo_code

    assert column.unique is True
