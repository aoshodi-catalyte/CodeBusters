"""
Defines the EmployeeRole enum used throughout the application for role validation
and normalization.
"""

from enum import Enum

from utils.enum_handler import enum_missing_handler


class EmployeeRole(str, Enum):
    """
    Enumeration of valid employee roles within the system.
    """

    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"

    @classmethod
    def _missing_(cls, value):
        return enum_missing_handler(cls, value)