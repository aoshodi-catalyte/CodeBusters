"""
Custom exceptions for baked good operations.
"""

class VendorNotFoundError(Exception):
    """
    Raised when a baked good references a vendor that does not exist.
    """
    def __init__(self, vendor_id: int):
        self.vendor_id = vendor_id
        super().__init__(
            f"Vendor with ID {vendor_id} was not found."
        )


class DuplicateBakedGoodError(Exception):
    """
    Raised when a vendor already has a baked good with the same name.
    """
    def __init__(self, baked_good_name: str):
        self.baked_good_name = baked_good_name
        super().__init__(
            f"A baked good with name '{baked_good_name}' already exists."
        )


class BakedGoodNotFoundError(Exception):
    """
    Raised when a baked good cannot be found by its ID.

    Args:
        baked_good_id: The ID of the baked good that could not be found.
    """

    def __init__(self, baked_good_id: int):
        self.baked_good_id = baked_good_id
        super().__init__(f"Baked good with ID {baked_good_id} was not found.")


class BakedGoodAlreadyDeactivatedError(Exception):
    """
    Raised when a baked good is already deactivated.
    """
    def __init__(self, baked_good_id: int):
        self.baked_good_id = baked_good_id
        super().__init__(f"Baked good with ID {baked_good_id} is already deactivated.")
