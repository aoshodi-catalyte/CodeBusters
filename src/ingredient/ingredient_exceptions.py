class VendorNotFoundError(Exception):
    """Raised when the specified vendor does not exist."""

    def __init__(self, vendor_id: int):
        self.vendor_id = vendor_id

        super().__init__(
            f"Vendor with ID {vendor_id} does not exist."
        )


class IngredientAlreadyExistsError(Exception):
    """Raised when an ingredient with the same name already exists."""

    def __init__(self, name: str):
        self.name = name

        super().__init__(
            f"An ingredient with the name '{name}' already exists."
        )


class IngredientConstraintError(Exception):
    """Raised when an ingredient violates a database constraint."""

    def __init__(self, constraint: str | None = None):
        self.constraint = constraint

        super().__init__(
            "The ingredient violates a database constraint."
        )