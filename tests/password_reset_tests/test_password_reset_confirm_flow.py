from employee.employee_model import Employee
from repositories.employee_repository import EmployeeRepository
from constants.employee_roles import EmployeeRole
from password_reset.password_reset_model import PasswordResetChannel
from repositories.password_reset_repository import PasswordResetRepository
from routers import password_reset_router
from services.password_reset_service import PasswordResetService


class FakeEmailService:
    def __init__(self):
        self.recipient = None
        self.code = None


    def send_password_reset_code(
        self,
        recipient_email,
        code,
    ):
        self.recipient = recipient_email
        self.code = code


class FakeSmsService:
    def __init__(self):
        self.recipient = None
        self.code = None

    def send_password_reset_code(
        self,
        recipient_phone,
        code,
    ):
        self.recipient = recipient_phone
        self.code = code


def create_reset_test_service():
    email_service = FakeEmailService()
    sms_service = FakeSmsService()

    service = PasswordResetService(
        repository=PasswordResetRepository(),
        email_service=email_service,
        sms_service=sms_service,
    )

    return service, email_service, sms_service


def create_test_employee(db):
    employee_repo = EmployeeRepository(db)

    employee_data = Employee(
        active=True,
        first_name="John",
        last_name="Reset",
        email="john.reset@example.com",
        phone_number="5551234567",
        role=EmployeeRole.MANAGER,
        hourly_rate=20.00,
        hire_date="09/11/2026",
    )

    return employee_repo.create_new_employee(employee_data)


def test_full_password_reset_flow_by_email(
    db,
    client,
):
    service, email_service, _ = create_reset_test_service()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: service

    try:
        employee = create_test_employee(db)

        response = client.post(
            "/password-reset/initiate",
            json={
                "username": employee.auth.username,
                "channel": PasswordResetChannel.EMAIL.value,
            },
        )

        assert response.status_code == 200

        assert email_service.recipient == (
            "john.reset@example.com"
        )

        assert email_service.code is not None
        assert len(email_service.code) == 6
        assert email_service.code.isdigit()

        reset_code = email_service.code

        response = client.post(
            "/password-reset/confirm",
            json={
                "username": employee.auth.username,
                "code": reset_code,
                "new_password": "Permanent123!",
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "message": "Password reset successfully"
        }

        db.expire_all()

        login_response = client.post(
            "/auth/login",
            data={
                "username": employee.auth.username,
                "password": "Permanent123!",
            },
        )

        assert login_response.status_code == 200

        login_data = login_response.json()

        assert "access_token" in login_data
        assert login_data["must_change_password"] is False

    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )


def test_full_password_reset_flow_by_phone(
    db,
    client,
):
    service, _, sms_service = create_reset_test_service()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: service

    try:
        employee = create_test_employee(db)

        response = client.post(
            "/password-reset/initiate",
            json={
                "username": employee.auth.username,
                "channel": PasswordResetChannel.PHONE.value,
            },
        )

        assert response.status_code == 200

        assert sms_service.recipient == "5551234567"

        assert sms_service.code is not None
        assert len(sms_service.code) == 6
        assert sms_service.code.isdigit()

        reset_code = sms_service.code

        response = client.post(
            "/password-reset/confirm",
            json={
                "username": employee.auth.username,
                "code": reset_code,
                "new_password": "Permanent456!",
            },
        )

        assert response.status_code == 200

        login_response = client.post(
            "/auth/login",
            data={
                "username": employee.auth.username,
                "password": "Permanent456!",
            },
        )

        assert login_response.status_code == 200

        assert (
            login_response.json()["must_change_password"]
            is False
        )

    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )


def test_password_reset_code_cannot_be_reused(
    db,
    client,
):
    service, email_service, _ = create_reset_test_service()

    client.app.dependency_overrides[
        password_reset_router.get_password_reset_service
    ] = lambda: service

    try:
        employee = create_test_employee(db)

        initiate_response = client.post(
            "/password-reset/initiate",
            json={
                "username": employee.auth.username,
                "channel": PasswordResetChannel.EMAIL.value,
            },
        )

        assert initiate_response.status_code == 200

        reset_code = email_service.code

        confirm_response = client.post(
            "/password-reset/confirm",
            json={
                "username": employee.auth.username,
                "code": reset_code,
                "new_password": "Permanent789!",
            },
        )

        assert confirm_response.status_code == 200

        reuse_response = client.post(
            "/password-reset/confirm",
            json={
                "username": employee.auth.username,
                "code": reset_code,
                "new_password": "AnotherPassword123!",
            },
        )

        assert reuse_response.status_code == 400

        assert reuse_response.json() == {
            "detail": (
                "Invalid or expired password reset request."
            )
        }

    finally:
        client.app.dependency_overrides.pop(
            password_reset_router.get_password_reset_service,
            None,
        )
