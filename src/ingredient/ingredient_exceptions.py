"""
Custom exception classes used across the application.

Provides domain‑specific errors for vendor lookup failures, duplicate
ingredient creation, and ingredient constraint violations. These exceptions
allow repositories and services to raise clear, typed errors that can be
caught and translated into appropriate API responses.
"""

class VendorNotFoundError(Exception):
    """Raised when the specified vendor does not exist."""

<<<<<<< HEAD
    def __init__(self, vendor_id: int):
        """Initialize the vendor-not-found exception.
=======
    def __init__(self, vendor_id: int) -> None:
        """Initialize a VendorNotFoundError.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

        Args:
            vendor_id: ID of the vendor that could not be found.
        """
        self.vendor_id = vendor_id

        super().__init__(
            f"Vendor with ID {vendor_id} does not exist."
        )


class IngredientAlreadyExistsError(Exception):
    """Raised when an ingredient with the same name already exists."""

<<<<<<< HEAD
    def __init__(self, name: str):
        """Initialize the duplicate-ingredient exception.
=======
    def __init__(self, name: str) -> None:
        """Initialize an IngredientAlreadyExistsError.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

        Args:
            name: Name of the ingredient that already exists.
        """
        self.name = name

        super().__init__(
            f"An ingredient with the name '{name}' already exists."
        )


class IngredientConstraintError(Exception):
    """Raised when an ingredient violates a database constraint."""

<<<<<<< HEAD
    def __init__(self, constraint: str | None = None):
        """Initialize the database-constraint exception.
=======
    def __init__(self, constraint: str | None = None) -> None:
        """Initialize an IngredientConstraintError.
>>>>>>> 0d25e2769e93a16f5d8d0d058327506f2bc2ee73

        Args:
            constraint: Name of the database constraint that was
                violated, if available.
        """
        self.constraint = constraint

        super().__init__(
            "The ingredient violates a database constraint."
        )