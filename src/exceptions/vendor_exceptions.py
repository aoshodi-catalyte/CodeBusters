"""
Custom exception classes used across the vendor domain.

Provides domain-specific errors for vendor lookup failures, duplicate
vendor creation, and vendor constraint violations. These exceptions allow
repositories and services to raise clear, typed errors that can be caught
and translated into appropriate API responses.
"""


class VendorNotFoundException(Exception):
    def __init__(self, vendor_id: int):
        self.vendor_id = vendor_id
        super().__init__(f"Vendor with ID {vendor_id} was not found.")


class DuplicateVendorException(Exception):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(
            f"Vendor with {field} '{value}' already exists."
        )


class VendorDeletionException(Exception):
    def __init__(self, vendor_id: int):
        self.vendor_id = vendor_id
        super().__init__(
            f"Vendor {vendor_id} cannot be deleted because it has associated records."
        )
