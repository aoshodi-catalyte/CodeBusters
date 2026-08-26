"""
Custom exception classes used across the application.

Provides domain‑specific errors for vendor lookup failures, duplicate
ingredient creation, and ingredient constraint violations. These exceptions
allow repositories and services to raise clear, typed errors that can be
caught and translated into appropriate API responses.
"""

class VendorNotFoundError(Exception):
    """Raised when the specified vendor does not exist."""

    def __init__(self, vendor_id: int) -> None:
        """Initialize a VendorNotFoundError.

        Args:
            vendor_id: ID of the vendor that could not be found.
        """
        self.vendor_id = vendor_id

        super().__init__(
            f"Vendor with ID {vendor_id} does not exist."
        )


class IngredientAlreadyExistsError(Exception):
    """Raised when an ingredient with the same name already exists."""

    def __init__(self, name: str) -> None:
        """Initialize an IngredientAlreadyExistsError.

        Args:
            name: Name of the ingredient that already exists.
        """
        self.name = name

        super().__init__(
            f"An ingredient with the name '{name}' already exists."
        )


class IngredientConstraintError(Exception):
    """Raised when an ingredient violates a database constraint."""

    def __init__(self, constraint: str | None = None) -> None:
        """Initialize an IngredientConstraintError.

        Args:
            constraint: Name of the database constraint that was
                violated, if available.
        """
        self.constraint = constraint

        super().__init__(
            "The ingredient violates a database constraint."
        )
