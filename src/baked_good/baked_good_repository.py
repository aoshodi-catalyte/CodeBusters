from sqlalchemy.orm import Session
from baked_good.baked_good_model import BakedGood
from baked_good.baked_good_schema import BakedGoodSchema

class BakedGoodRepository:
    """
    Stores and manages baked good objects using a SQLAlchemy session.

    The repository provides methods for creating and persisting
    BakedGood objects in the database.

    Args:
        session: The SQLAlchemy database session used to interact
        with the database.

    Returns:
         A BakedGoodRepository object configured with the provided
        database session.
    """

    def __init__(self, session: Session):
        """
        Initializes the baked good repository.

        Args:
            session: The SQLAlchemy database session used to interact
                with the database.

        Returns:
            None.
        """

        self.session = session

    def create_baked_good(self, baked_good: BakedGood) -> BakedGoodSchema:
        """
        Adds a baked good to the database.

        Converts the BakedGood Pydantic object into a BakedGoodSchema
        SQLAlchemy object, adds it to the database, commits the
        transaction, and refreshes the object with its generated values.

        Args:
            baked_good: The BakedGood object to add to the database.

        Returns:
            The newly created BakedGoodSchema object.
        """
        
        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        self.session.add(new_baked_good)
        self.session.commit()
        self.session.refresh(new_baked_good)
        return new_baked_good
