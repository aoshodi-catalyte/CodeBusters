"""
Defines the EmployeeRole enum used throughout the application for role validation
and normalization.
"""

from enum import Enum


class EmployeeRole(str, Enum):
    """
    Enumeration of valid employee roles within the system.
    """

    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"

    @classmethod
    def _missing_(cls, value):
        """
        Provide case‑insensitive fallback behavior when an enum value is not found.

        This method is invoked automatically by the Enum machinery when a lookup
        fails (e.g., EmployeeRole("MANAGER") or EmployeeRole("Manager")). It attempts
        to normalize string input by lowercasing it and checking whether the
        normalized value exists in the enum’s value map.

        Args:
            value (Any):
                The raw value provided during enum construction or lookup.

        Returns:
            EmployeeRole | None:
                The matching enum member if a case‑insensitive match is found;
                otherwise None, allowing Enum to raise its standard ValueError.
        """

        if isinstance(value, str):
            value = value.lower()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None
