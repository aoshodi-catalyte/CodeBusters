from sqlalchemy.orm import Session
from typing import List
from baked_good.baked_good_model import BakedGood
from baked_good.baked_good_schema import BakedGoodSchema
from vendor.vendor_schema import Vendor

class BakedGoodRepository:
    """
    Stores and manages baked good objects using a SQLAlchemy session.

    The repository provides methods for retrieving all baked goods and
    creating and persisting BakedGood objects in the database.

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

    def get_baked_goods(self) -> List[BakedGoodSchema]:
        """
        Retrieves all baked goods from the database.

        Returns:
            A list of BakedGoodSchema objects representing all baked goods
            stored in the database.
        """
        
        return self.session.query(BakedGoodSchema).all()

    def create_baked_good(self, baked_good: BakedGood) -> BakedGoodSchema:
        """
        Creates and stores a new baked good in the database.

        Args:
            baked_good: The validated baked good to create.

        Raises:
            ValueError: If the vendor associated with the baked good
                does not exist.

        Returns:
            BakedGoodSchema: The newly created baked good.
        """
        
        vendor = self.session.query(Vendor).filter(
            Vendor.id == baked_good.vendor_id
        ).first()

        if vendor is None:
            raise ValueError("Vendor not found")
        
        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        self.session.add(new_baked_good)
        self.session.commit()
        self.session.refresh(new_baked_good)

        return new_baked_good
