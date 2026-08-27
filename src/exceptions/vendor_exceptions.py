"""
Custom exception classes used across the vendor domain.

Provides domain-specific errors for vendor lookup failures, duplicate
vendor creation, and vendor deletion constraint violations. These exceptions
allow repositories and services to raise clear, typed errors that can be
caught and translated into appropriate API responses.
"""


class VendorNotFoundException(Exception):
    """Raised when a requested vendor cannot be found in the database."""

    def __init__(self, vendor_id: int):
        """Initialize the vendor not found exception.

        Args:
            vendor_id (int): The unique identifier of the vendor that
                could not be found.
        """
        self.vendor_id = vendor_id
        super().__init__(f"Vendor with ID {vendor_id} was not found.")


class DuplicateVendorException(Exception):
    """Raised when a vendor violates a uniqueness constraint."""

    def __init__(self, field: str, value: str):
        """Initialize the duplicate vendor exception.

        Args:
            field (str): The vendor field that caused the uniqueness
                conflict, such as name or email.
            value (str): The value that already exists for the specified
                field.
        """
        self.field = field
        self.value = value
        super().__init__(
            f"Vendor with {field} '{value}' already exists."
        )


class VendorDeletionException(Exception):
    """Raised when a vendor cannot be deleted because related records exist."""

    def __init__(self, vendor_id: int):
        """Initialize the vendor deletion exception.

        Args:
            vendor_id (int): The unique identifier of the vendor that
                cannot be deleted.
        """
        self.vendor_id = vendor_id
        super().__init__(
            f"Vendor {vendor_id} cannot be deleted because it has associated records."
        )
