"""
Custom exceptions for baked good operations.
"""

class VendorNotFoundError(Exception):
    """
    Raised when a baked good references a vendor that does not exist.
    """


class DuplicateBakedGoodError(Exception):
    """
    Raised when a vendor already has a baked good with the same name.
    """