"""
Custom exception classes used for employee-related operations.

These exceptions allow the repository layer to raise clear, typed errors
that the router can catch and translate into appropriate HTTP responses,
rather than relying on generic Exception handling.
"""


import employee


class EmployeeEmailAlreadyExistsError(Exception):
    """Raised when a employee with the given email already exists."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(
            f"A employee with the email '{email}' already exists."
        )

class EmployeeNotFoundError(Exception):
    """
    Raised when an employee cannot be found by its ID.

    Args:
        employee_id: The ID of the employee that could not be found.
    """

    def __init__(self, employee_id: int):
        self.employee_id = employee_id
        super().__init__(f"Employee with ID {employee_id} was not found.")

class EmployeeAlreadyDeactivatedError(Exception):
    """
    Raised when an employee is already deactivated.
    """
    def __init__(self, employee_id: int):
        self.employee_id = employee_id
        super().__init__(f"Employee with ID {employee_id} is already deactivated.")
