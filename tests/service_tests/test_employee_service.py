import pytest
from types import SimpleNamespace

from services.employee_service import EmployeeService


def test_create_employee_sends_initial_credentials():
    captured = {}

    class FakeRepository:
        def create_new_employee(
            self,
            employee_data,
            return_credentials=False,
        ):
            assert return_credentials is True

            employee = SimpleNamespace(
                email="yemi@example.com"
            )

            return (
                employee,
                "yemi.o",
                "Temporary123!",
            )

    class FakeEmailService:
        def send_initial_credentials(
            self,
            recipient_email,
            username,
            temporary_password,
        ):
            captured["recipient_email"] = (
                recipient_email
            )
            captured["username"] = username
            captured["temporary_password"] = (
                temporary_password
            )

    service = EmployeeService(
        repository=FakeRepository(),
        email_service=FakeEmailService(),
    )

    result = service.create_employee(
        db=None,
        employee_data=SimpleNamespace(),
    )

    assert result.email == "yemi@example.com"

    assert captured["recipient_email"] == (
        "yemi@example.com"
    )

    assert captured["username"] == "yemi.o"

    assert captured["temporary_password"] == (
        "Temporary123!"
    )


def test_create_employee_propagates_email_failure():
    class FakeRepository:
        def create_new_employee(
            self,
            employee_data,
            return_credentials=False,
        ):
            return (
                SimpleNamespace(
                    email="yemi@example.com"
                ),
                "yemi.o",
                "Temporary123!",
            )

    class FakeEmailService:
        def send_initial_credentials(
            self,
            recipient_email,
            username,
            temporary_password,
        ):
            raise RuntimeError(
                "Email delivery failed"
            )

    service = EmployeeService(
        repository=FakeRepository(),
        email_service=FakeEmailService(),
    )

    with pytest.raises(RuntimeError):
        service.create_employee(
            db=None,
            employee_data=SimpleNamespace(),
        )
