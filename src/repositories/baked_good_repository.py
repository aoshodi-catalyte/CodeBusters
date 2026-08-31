"""
Repository operations for baked goods.

This module provides the BakedGoodRepository class, which handles
database operations for baked goods using a SQLAlchemy session.

The repository supports retrieving all baked goods, retrieving a single
baked good by ID, creating new baked goods, and updating existing baked
goods, all while verifying that the associated vendor exists.
"""
import re
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from exceptions.baked_good_exceptions import (
    BakedGoodNotFoundError,
    DuplicateBakedGoodError,
    VendorNotFoundError,
)
from baked_good.baked_good_model import BakedGood, BakedGoodUpdate
from baked_good.baked_good_schema import BakedGoodSchema
from vendor.vendor_schema import Vendor


class BakedGoodRepository:
    """
    Stores and manages baked good objects using a SQLAlchemy session.

    The repository provides methods for retrieving, creating, and
    updating BakedGood records in the database.

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

    def _get_vendor_or_raise(self, vendor_id: int) -> Vendor:
        """
        Retrieves a vendor by ID, raising VendorNotFoundError if it
        does not exist.

        Args:
            vendor_id: The unique ID of the vendor.

        Raises:
            VendorNotFoundError: If no vendor exists with the given ID.

        Returns:
            Vendor: The matching vendor record.
        """
        vendor = self.session.query(Vendor).filter(
            Vendor.id == vendor_id
        ).first()

        if vendor is None:
            raise VendorNotFoundError(vendor_id)

        return vendor

    def _find_duplicate_by_name(
        self,
        name: str,
        exclude_id: int | None = None,
    ) -> BakedGoodSchema | None:
        """
        Looks up an existing baked good with the same name, ignoring
        case and whitespace differences.

        Args:
            name: The baked good name to check for duplicates.
            exclude_id: An optional baked good ID to exclude from the
                search (used when updating a baked good, so it does not
                collide with itself).

        Returns:
            BakedGoodSchema | None: The matching baked good if one
                exists, otherwise None.
        """
        normalized_input = re.sub(r"\s+", "", name).lower()

        query = self.session.query(BakedGoodSchema).filter(
            func.lower(
                func.replace(BakedGoodSchema.name, " ", "")
            ) == normalized_input
        )

        if exclude_id is not None:
            query = query.filter(BakedGoodSchema.id != exclude_id)

        return query.first()

    def create_baked_good(self, baked_good: BakedGood) -> BakedGoodSchema:
        """
        Creates and stores a new baked good in the database.

        Args:
            baked_good: The validated baked good to create.

        Raises:
            VendorNotFoundError: If the vendor does not exist.
            DuplicateBakedGoodError: If a baked good with the same name
                already exists.

        Returns:
            BakedGoodSchema: The newly created baked good.
        """

        self._get_vendor_or_raise(baked_good.vendor_id)

        if self._find_duplicate_by_name(baked_good.name) is not None:
            raise DuplicateBakedGoodError(baked_good.name)

        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        self.session.add(new_baked_good)
        self.session.commit()
        self.session.refresh(new_baked_good)

        return new_baked_good

    def update_baked_good(
        self,
        baked_good_id: int,
        update_data: BakedGoodUpdate,
    ) -> BakedGoodSchema:
        """
        Updates and persists an existing baked good's properties.

        If the vendor associated with the baked good changes, the new
        vendor is validated and the relationship is updated so that the
        change is reflected on both the baked good and the vendor side
        of the relationship.

        Args:
            baked_good_id: The ID of the baked good to update.
            update_data: The validated replacement baked good data.

        Raises:
            BakedGoodNotFoundError: If no baked good exists with the
                given ID.
            VendorNotFoundError: If the vendor does not exist.
            DuplicateBakedGoodError: If another baked good already has
                the given name.

        Returns:
            BakedGoodSchema: The updated baked good.
        """

        baked_good = self.get_baked_good_by_id(baked_good_id)

        if baked_good is None:
            raise BakedGoodNotFoundError(baked_good_id)

        vendor = self._get_vendor_or_raise(update_data.vendor_id)

        duplicate = self._find_duplicate_by_name(
            update_data.name,
            exclude_id=baked_good_id,
        )
        if duplicate is not None:
            raise DuplicateBakedGoodError(update_data.name)

        baked_good.active = update_data.active
        baked_good.name = update_data.name
        baked_good.description = update_data.description
        baked_good.purchasing_cost = update_data.purchasing_cost
        baked_good.retail_price = update_data.retail_price
        baked_good.vendor_id = update_data.vendor_id

        # Explicitly reassign the relationship so the vendor side of the
        # association (vendor.baked_good) is updated in the same unit of
        # work, not just the raw vendor_id foreign key column.
        baked_good.vendor = vendor

        self.session.commit()
        self.session.refresh(baked_good)
        self.session.refresh(vendor)

        return baked_good
