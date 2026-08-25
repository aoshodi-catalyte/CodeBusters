"""
Repository operations for baked goods.

This module provides the BakedGoodRepository class, which handles
database operations for baked goods using a SQLAlchemy session.

The repository supports retrieving all baked goods and creating new
baked goods while verifying that the associated vendor exists.
"""
import re
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from baked_good.baked_good_exceptions import (
    DuplicateBakedGoodError,
    VendorNotFoundError,
)
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

    def get_all_baked_goods(self) -> List[BakedGoodSchema]:
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
            VendorNotFoundError: If the vendor does not exist.
            DuplicateBakedGoodError: If the vendor already has a baked good
                with the same name.

        Returns:
            BakedGoodSchema: The newly created baked good.
        """

        vendor = self.session.query(Vendor).filter(
            Vendor.id == baked_good.vendor_id
        ).first()

        if vendor is None:
            raise VendorNotFoundError("Vendor not found")

        normalized_input = re.sub(r"\s+", "", baked_good.name).lower()

        existing = (
            self.session.query(BakedGoodSchema)
            .filter(
                func.lower(
                    func.replace(BakedGoodSchema.name, " ", "")
                ) == normalized_input
            )
            .first()
        )

        if existing is not None:
            raise DuplicateBakedGoodError(
                f"A baked good with name '{baked_good.name}' already exists"
            )

        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        self.session.add(new_baked_good)
        self.session.commit()
        self.session.refresh(new_baked_good)

        return new_baked_good

    def get_baked_good_by_id(self, baked_good_id: int) -> BakedGoodSchema | None:
        """
        Retrieves a baked good by its ID.

        Args:
            baked_good_id: The unique ID of the baked good.

        Returns:
            BakedGoodSchema: The baked good matching the provided ID,
                or None if the baked good does not exist.
        """
        return self.session.query(BakedGoodSchema).filter(
            BakedGoodSchema.id == baked_good_id
        ).first()
