"""
Repository layer for vendor-related database operations, including creation,
retrieval, and persistence logic for vendor records.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from exceptions.vendor_exceptions import (
    DuplicateVendorException,
    VendorNotFoundException,
)
from vendor.vendor_model import VendorBase, VendorUpdate
from vendor.vendor_schema import Vendor, VendorSchema


class VendorRepository:
    """
    Provides database operations for vendor records, including creation,
    retrieval, and deletion of vendor data.
    """

    def __init__(self, db: Session):
        """Initialize the VendorRepository with a database session.

        Args:
            db (Session): An active SQLAlchemy session used to perform
                database operations.
        """
        self.db = db

    def create_new_vendor(self, vendor_data: VendorBase) -> VendorSchema:
        """Create and persist a new vendor record.

        Args:
            vendor_data (VendorBase): Validated vendor data.

        Returns:
            VendorSchema: The newly created vendor.

        Raises:
            DuplicateVendorException: If a vendor with the same unique
                field already exists.
        """
        db_vendor = Vendor(
            active=vendor_data.active,
            name=vendor_data.name,
            contact_name=vendor_data.contact_name,
            contact_role=vendor_data.contact_role,
            email=vendor_data.email,
            phone=vendor_data.phone,
        )

        self.db.add(db_vendor)

        try:
            self.db.commit()
            self.db.refresh(db_vendor)

        except IntegrityError as exc:
            self.db.rollback()

            raise DuplicateVendorException(
                field="email",
                value=vendor_data.email,
            ) from exc

        return db_vendor

    def get_all_vendors(self) -> list[VendorSchema]:
        """Retrieve all vendor records from the database.

        Returns:
            list[VendorSchema]: A list of all vendors.
        """
        return self.db.query(Vendor).all()

    def get_vendor_by_id(self, vendor_id: int) -> VendorSchema:
        """Retrieve a vendor by its unique ID.

        Args:
            vendor_id (int): The unique identifier of the vendor.

        Returns:
            VendorSchema: The requested vendor.

        Raises:
            VendorNotFoundException: If the vendor does not exist.
        """
        vendor = (
            self.db.query(Vendor)
            .filter(Vendor.id == vendor_id)
            .first()
        )

        if vendor is None:
            raise VendorNotFoundException(vendor_id)

        return vendor

    def update_vendor(
        self,
        vendor_id: int,
        vendor_data: VendorUpdate,
    ) -> Vendor:
        vendor = (
            self.db.query(Vendor)
            .filter(Vendor.id == vendor_id)
            .first()
        )

        if vendor is None:
            raise VendorNotFoundException(vendor_id)

        update_data = vendor_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(vendor, field, value)

        try:
            self.db.commit()
            self.db.refresh(vendor)

        except IntegrityError as exc:
            self.db.rollback()

            raise DuplicateVendorException(
                field="email",
                value=vendor_data.email,
            ) from exc

        return vendor
