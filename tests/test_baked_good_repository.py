from baked_good.baked_good_repository import BakedGoodRepository
from baked_good.baked_good_model import BakedGood

def test_create_baked_good_repository():
    repository = BakedGoodRepository()

    baked_good = BakedGood (
        id=1,
        active=True,
        name="Chocolate Cake",
        description="A chocolate cake",
        purchasing_cost=5.00,
        retail_price=10.00,
    )

    repository.create_baked_good(baked_good)

    assert baked_good in repository.baked_goods
    assert len(repository.baked_goods) == 1

    def test_create_baked_good_returns_baked_good():
        repository = BakedGoodRepository()

        baked_good = BakedGood(
            id=1,
            active=True,
            name="Chocolate Cake",
            description="A chocolate cake",
            purchasing_cost=5.00,
            retail_price=10.00
        )

        result = repository.create_baked_good(baked_good)

        assert result == baked_good
