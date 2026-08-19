import re
from pydantic import BaseModel, Field, condecimal, field_validator, model_validator
from constants.employee_roles import EmployeeRole
from datetime import date, datetime

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ConstrainedMoney = condecimal(gt=0, decimal_places=2)


class Employee(BaseModel):
    active: bool
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: str
    role: EmployeeRole
    hourly_rate: ConstrainedMoney  # type: ignore
    hire_date: date
    term_date: date | None = None

    @field_validator("first_name", "last_name", "email")
    @classmethod
    def validate_not_blank(cls, value):
        """
        Ensure that string fields are not empty or composed solely of whitespace.

        This validator normalizes input by stripping leading and trailing whitespace
        and then verifies that the resulting value contains at least one non‑space
        character.

        Fields validated:
            - first_name
            - last_name
            - email

        Args:
            value (str): Raw string provided by the client.

        Returns:
            str: The cleaned, non‑blank string.

        Raises:
            ValueError: If the field is empty after stripping whitespace.
        """

        value = value.strip()
        if not value:
            raise ValueError("Must not be blank")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Validate that the email field contains a properly formatted email address.

        Uses a compiled regular expression to enforce:
            - exactly one '@' symbol
            - no whitespace characters
            - a valid domain structure (e.g., example.com)

        Args:
            value (str): The email address provided by the user.

        Returns:
            str: The validated email address.

        Raises:
            ValueError: If the email does not match the required pattern.
        """

        if not EMAIL_PATTERN.match(value):
            raise ValueError("email must be a valid email address")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, role_name):
        """
        Normalize and validate the employee role.

        Accepts either:
            - an EmployeeRole enum instance
            - a string that can be converted to a valid EmployeeRole value

        The validator lowercases string input to allow case‑insensitive matching.

        Args:
            role_name (str | EmployeeRole): The role value provided by the client.

        Returns:
            EmployeeRole: A valid EmployeeRole enum instance.

        Raises:
            ValueError: If the provided role does not match any known EmployeeRole.
        """

        if isinstance(role_name, EmployeeRole):
            return role_name

        normalized = str(role_name).lower()

        try:
            return EmployeeRole(normalized)
        except ValueError:
            valid = [r.value for r in EmployeeRole]
            raise ValueError(f"Invalid role: {role_name}. Valid roles are: {valid}")

    @field_validator("hire_date", "term_date", mode="before")
    @classmethod
    def validate_date(cls, value):
        """
        Parse and validate date fields provided as strings.

        Accepts dates in MM/DD/YYYY format and converts them into `datetime.date`
        objects. Allows `None` for nullable fields such as term_date.

        Fields validated:
            - hire_date
            - term_date

        Args:
            value (str | None): The raw date string or None.

        Returns:
            date | None: Parsed date object or None.

        Raises:
            ValueError: If the date string is not in MM/DD/YYYY format.
        """

        if value is None:
            return None

        try:
            return datetime.strptime(value, "%m/%d/%Y").date()
        except ValueError:
            raise ValueError("Date must be in MM/DD/YYYY format")

    @model_validator(mode="after")
    def check_term_date_rules(self):
        """
        Enforce business rules related to employee active status and term dates.

        Rules enforced:
            - Active employees cannot have a term_date.
            - Inactive employees must have a term_date.
            - term_date cannot be in the future.
            - term_date cannot be earlier than hire_date.

        These rules ensure logical consistency between employment status and
        lifecycle dates.

        Returns:
            Employee: The validated Employee instance.

        Raises:
            ValueError: If any rule is violated.
        """

        if self.active and self.term_date is not None:
            raise ValueError("Active employees cannot have a term_date.")

        if not self.active and self.term_date is None:
            raise ValueError("Inactive employees must have a term_date.")

        if self.term_date is not None and self.term_date > date.today():
            raise ValueError("term_date cannot be in the future.")

        if self.term_date is not None and self.term_date < self.hire_date:
            raise ValueError("term_date cannot be before hire_date.")

        return self
