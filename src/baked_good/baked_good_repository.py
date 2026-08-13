from sqlalchemy.orm import Session
from baked_good.baked_good_model import BakedGood
from baked_good.baked_good_schema import BakedGoodSchema

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

    def __init__(self, session: Session):
        """
        Initializes the baked good repository.

            Creates an empty list that will be used to store BakedGood objects.

            Args:
                None

            Returns:
                None
            """

        self.session = session

    def create_baked_good(self, baked_good: BakedGood) -> BakedGoodSchema:
        """
        Adds a baked good to the repository.

        Args:
            baked_good: The BakedGood object to add to the repository.

        Returns:
            The BakedGood object that was added to the repository.
        """
        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        self.session.add(new_baked_good)
        self.session.commit()
        self.session.refresh(new_baked_good)
        return new_baked_good
