from baked_good.baked_good_model import BakedGood
from typing import List

class BakedGoodRepository:

    def __init__(self) -> None:

        self.baked_goods: List[BakedGood] = []

    def create_baked_good(self, baked_good: BakedGood) -> BakedGood:
        
        self.baked_goods.append(baked_good)
        return baked_good