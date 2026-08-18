from sqlalchemy import inspect
from promotion.promotion_schema import PromotionSchema

def test_promotion_columns_exist():
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
    column = PromotionSchema.__table__.c.id

    assert column.primary_key is True

def test_promo_code_is_unique():
    column = PromotionSchema.__table__.c.promo_code

    assert column.unique is True
