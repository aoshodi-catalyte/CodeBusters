import pytest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from routers import password_reset_router
from tests.password_reset_tests.test_password_reset_confirm_flow import create_reset_test_service, create_test_employee
from utils.password_utils import (
    hash_password,
    verify_password,
)
from password_reset.password_reset_model import PasswordResetChannel
from password_reset.password_reset_schema import PasswordResetToken
from repositories.password_reset_repository import PasswordResetRepository
from secure_login.secure_login_schema import EmployeeAuth
from exceptions.secure_login_exceptions import (
    IncorrectPasswordError,
)
from password_reset.password_reset_schema import PasswordResetToken

repo = PasswordResetRepository()


class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def filter_by(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class FakeDB:
    def __init__(
        self,
        auth_record=None,
        reset_record=None,
    ):
        self.auth_record = auth_record
        self.reset_record = reset_record

        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, model):
        if model.__name__ == "EmployeeAuth":
            return FakeQuery(self.auth_record)

        if model.__name__ == "PasswordResetToken":
            return FakeQuery(self.reset_record)

        return FakeQuery(None)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)


def test_generate_reset_code_returns_six_digits():
    code = repo.generate_reset_code()

    assert len(code) == 6
    assert code.isdigit()


def test_initiate_reset_returns_none_for_unknown_username():
    db = FakeDB(auth_record=None)

    employee, code = repo.initiate_reset(
        db,
        username="does.not.exist",
        channel=PasswordResetChannel.EMAIL,
    )

    assert employee is None
    assert code is None
    assert db.committed is False


def test_initiate_reset_returns_none_without_email():
    employee = SimpleNamespace(
        id=7,
        email=None,
        phone_number="5551234567",
    )

    auth_record = SimpleNamespace(
        employee_id=7,
        employee=employee,
    )

    db = FakeDB(auth_record=auth_record)

    employee_result, code = repo.initiate_reset(
        db,
        username="john.smith",
        channel=PasswordResetChannel.EMAIL,
    )

    assert employee_result is None
    assert code is None
    assert db.committed is False


def test_initiate_reset_returns_none_without_phone():
    employee = SimpleNamespace(
        id=7,
        email="john@example.com",
        phone_number=None,
    )

    auth_record = SimpleNamespace(
        employee_id=7,
        employee=employee,
    )

    db = FakeDB(auth_record=auth_record)

    employee_result, code = repo.initiate_reset(
        db,
        username="john.smith",
        channel=PasswordResetChannel.PHONE,
    )

    assert employee_result is None
    assert code is None
    assert db.committed is False


def test_confirm_reset_success(monkeypatch):
    employee = SimpleNamespace(
        id=7,
    )

    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
        password_hash="old-hash",
        is_temporary_password=True,
        employee=employee,
    )

    reset_record = SimpleNamespace(
        employee_id=7,
        token_hash="reset-hash",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used_at=None,
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=reset_record,
    )

    monkeypatch.setattr(
        "repositories.password_reset_repository.verify_password",
        lambda code, token_hash: (
            code == "482193"
            and token_hash == "reset-hash"
        ),
    )

    monkeypatch.setattr(
        "repositories.password_reset_repository.hash_password",
        lambda password: f"hashed-{password}",
    )

    repo.confirm_reset(
        db,
        username="john.smith",
        code="482193",
        new_password="NewPassword123!",
    )

    assert auth_record.password_hash == (
        "hashed-NewPassword123!"
    )

    assert auth_record.is_temporary_password is False

    assert reset_record.used_at is not None

    assert db.committed is True

    assert auth_record in db.refreshed
    assert reset_record in db.refreshed


def test_confirm_reset_rejects_unknown_username():
    db = FakeDB(auth_record=None)

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="does.not.exist",
            code="482193",
            new_password="NewPassword123!",
        )

    assert db.committed is False


def test_confirm_reset_rejects_missing_reset_token():
    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=None,
    )

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="john.smith",
            code="482193",
            new_password="NewPassword123!",
        )

    assert db.committed is False


def test_confirm_reset_rejects_expired_code(monkeypatch):
    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
        password_hash="old-hash",
        is_temporary_password=True,
    )

    reset_record = SimpleNamespace(
        employee_id=7,
        token_hash="reset-hash",
        expires_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ),
        used_at=None,
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=reset_record,
    )

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="john.smith",
            code="482193",
            new_password="NewPassword123!",
        )

    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert db.committed is False


def test_confirm_reset_rejects_used_code():
    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
        password_hash="old-hash",
        is_temporary_password=True,
    )

    reset_record = SimpleNamespace(
        employee_id=7,
        token_hash="reset-hash",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used_at=datetime.now(timezone.utc),
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=reset_record,
    )

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="john.smith",
            code="482193",
            new_password="NewPassword123!",
        )

    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert db.committed is False


def test_confirm_reset_rejects_invalid_code(monkeypatch):
    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
        password_hash="old-hash",
        is_temporary_password=True,
    )

    reset_record = SimpleNamespace(
        employee_id=7,
        token_hash="reset-hash",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used_at=None,
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=reset_record,
    )

    monkeypatch.setattr(
        "repositories.password_reset_repository.verify_password",
        lambda *_args: False,
    )

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="john.smith",
            code="wrong!",
            new_password="NewPassword123!",
        )

    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert reset_record.used_at is None
    assert db.committed is False

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

        assert reset_code is not None

        # First use of the reset code.
        confirm_response = client.post(
            "/password-reset/confirm",
            json={
                "username": employee.auth.username,
                "code": reset_code,
                "new_password": "Permanent789!",
            },
        )

        assert confirm_response.status_code == 200

        assert confirm_response.json() == {
            "message": "Password reset successfully"
        }

        # Confirm that the reset token was marked as used.
        db.expire_all()

        reset_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.employee_id == employee.id
            )
            .order_by(
                PasswordResetToken.id.desc()
            )
            .first()
        )

        assert reset_token is not None
        assert reset_token.used_at is not None

        # Attempt to reuse the exact same reset code.
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
