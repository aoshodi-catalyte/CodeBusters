from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions.vendor_exceptions import (
    DuplicateVendorException,
    VendorNotFoundException,
)
from vendor.vendor_model import VendorBase
from vendor.vendor_schema import Vendor, VendorSchema


UNIQUE_FIELDS = ("email", "name")


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

    def _raise_duplicate_error(
        self,
        exc: IntegrityError,
        data: dict,
    ) -> None:
        """Inspect an integrity error and identify the duplicate field.

        Falls back to a generic duplicate error when the offending
        unique field cannot be determined from the database error.
        """
        error_text = str(exc.orig).lower()

        for field in UNIQUE_FIELDS:
            if field in data and field in error_text:
                raise DuplicateVendorException(
                    field=field,
                    value=data[field],
                ) from exc

        raise DuplicateVendorException(
            field="unknown",
            value=None,
        ) from exc

    def create_new_vendor(self, vendor_data: VendorBase) -> VendorSchema:
        """Create and persist a new vendor record.

        Args:
            vendor_data: Validated vendor data.

        Returns:
            The newly created vendor.

        Raises:
            DuplicateVendorException:
                If a unique vendor field is already in use.
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
            self._raise_duplicate_error(
                exc,
                vendor_data.model_dump(),
            )

        return db_vendor

    def get_all_vendors(self) -> list[VendorSchema]:
        """Retrieve all vendor records from the database.

        Returns:
            A list of all vendors.
        """
        return self.db.query(Vendor).all()

    def get_vendor_by_id(self, vendor_id: int) -> VendorSchema:
        """Retrieve a vendor by its unique ID.

        Args:
            vendor_id: The unique identifier of the vendor.

        Returns:
            The requested vendor.

        Raises:
            VendorNotFoundException:
                If the vendor does not exist.
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
        vendor_data: VendorBase,
    ) -> VendorSchema:
        """Update an existing vendor with the provided fields.

        Args:
            vendor_id: ID of the vendor to update.
            vendor_data: Full set of vendor fields to apply.

        Returns:
            The updated vendor.

        Raises:
            VendorNotFoundException:
                If the vendor does not exist.
            DuplicateVendorException:
                If the update violates a unique email or name constraint.
        """
        vendor = (
            self.db.query(Vendor)
            .filter(Vendor.id == vendor_id)
            .first()
        )

        if vendor is None:
            raise VendorNotFoundException(vendor_id)

        update_data = vendor_data.model_dump()

        for field, value in update_data.items():
            setattr(vendor, field, value)

        try:
            self.db.commit()
            self.db.refresh(vendor)
        except IntegrityError as exc:
            self.db.rollback()
            self._raise_duplicate_error(exc, update_data)

        return vendor
