from baked_good.baked_good_model import BakedGood
from typing import List

class BakedGoodRepository:
    """
    Stores and manages baked good objects in memory.

    The repository maintains a list of BakedGood objects and provides
    methods for interacting with the stored baked goods.

    Args:
        None

    Returns:
        A BakedGoodRepository object containing an empty list of baked goods.
    """

    def __init__(self) -> None:
        """
        Initializes the baked good repository.

            Creates an empty list that will be used to store BakedGood objects.

            Args:
                None

            Returns:
                None
            """

        self.baked_goods: List[BakedGood] = []

    def create_baked_good(self, baked_good: BakedGood) -> BakedGood:
        """
        Adds a baked good to the repository.

        Args:
            baked_good: The BakedGood object to add to the repository.

        Returns:
            The BakedGood object that was added to the repository.
        """
        
        self.baked_goods.append(baked_good)
        return baked_good