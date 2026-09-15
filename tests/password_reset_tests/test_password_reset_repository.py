import pytest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from constants.employee_roles import EmployeeRole
from employee.employee_model import Employee
from repositories.employee_repository import EmployeeRepository
from password_reset.password_reset_model import PasswordResetChannel
from password_reset.password_reset_schema import PasswordResetToken
from repositories.password_reset_repository import PasswordResetRepository


repo = PasswordResetRepository()


class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        if isinstance(self._result, list):
            filtered = self._result

            for condition in args:
                # Handle the PasswordResetToken.used_at.is_(None)
                # condition used by the repository.
                condition_text = str(condition)

                if "used_at" in condition_text:
                    if "IS NULL" in condition_text.upper():
                        filtered = [
                            item
                            for item in filtered
                            if item.used_at is None
                        ]

                if "employee_id" in condition_text:
                    # The repository filters by employee_id.
                    # The test data already uses the correct employee,
                    # so no additional filtering is required here.
                    pass

            return FakeQuery(filtered)

        return self

    def filter_by(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        if isinstance(self._result, list):
            if not self._result:
                return None

            return self._result[0]

        return self._result

    def all(self):
        if isinstance(self._result, list):
            return self._result

        if self._result is None:
            return []

        return [self._result]


class FakeDB:
    def __init__(
        self,
        auth_record=None,
        reset_record=None,
        reset_records=None,
    ):
        self.auth_record = auth_record
        self.reset_record = reset_record
        self.reset_records = reset_records

        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, model):
        if model.__name__ == "EmployeeAuth":
            return FakeQuery(self.auth_record)

        if model.__name__ == "PasswordResetToken":
            if self.reset_records is not None:
                return FakeQuery(self.reset_records)

            return FakeQuery(self.reset_record)

        return FakeQuery(None)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)


def create_test_employee(db):
    """
    Create an employee using the real employee repository.

    This helper is used only by integration-style repository tests.
    """

    employee_repo = EmployeeRepository(db)

    employee_data = Employee(
        active=True,
        first_name="John",
        last_name="Reset",
        email="john.reset.repository@example.com",
        phone_number="5551234567",
        role=EmployeeRole.MANAGER,
        hourly_rate=20.00,
        hire_date="09/11/2026",
    )

    return employee_repo.create_new_employee(employee_data)


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

    db = FakeDB(
        auth_record=auth_record,
    )

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

    db = FakeDB(
        auth_record=auth_record,
    )

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
        attempt_count=0,
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
        "utils.password_reset_helpers.hash_password",
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
    db = FakeDB(
        auth_record=None,
    )

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


def test_confirm_reset_rejects_expired_code():
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
        attempt_count=0,
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
        attempt_count=0,
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
        attempt_count=0,
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
            code="111111",
            new_password="NewPassword123!",
        )

    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert reset_record.used_at is None
    assert db.committed is True


# ---------------------------------------------------------------------------
# Phase 6 Step 3
# Invalidate previous unused reset tokens
# ---------------------------------------------------------------------------


def test_initiate_reset_invalidates_previous_unused_tokens(
    monkeypatch,
):
    employee = SimpleNamespace(
        id=7,
        email="john@example.com",
        phone_number="5551234567",
    )

    auth_record = SimpleNamespace(
        employee_id=7,
        username="john.smith",
        employee=employee,
    )

    old_unused_token = SimpleNamespace(
        id=1,
        employee_id=7,
        token_hash="old-hash",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used_at=None,
        channel="email",
    )

    old_used_token_time = datetime.now(timezone.utc)

    old_used_token = SimpleNamespace(
        id=2,
        employee_id=7,
        token_hash="already-used",
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
        used_at=old_used_token_time,
        channel="email",
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_records=[
            old_unused_token,
            old_used_token,
        ],
    )

    monkeypatch.setattr(
        repo,
        "generate_reset_code",
        lambda: "654321",
    )

    monkeypatch.setattr(
        "repositories.password_reset_repository.hash_password",
        lambda value: f"hashed-{value}",
    )

    employee_result, code = repo.initiate_reset(
        db,
        username="john.smith",
        channel=PasswordResetChannel.EMAIL,
    )

    assert employee_result is employee
    assert code == "654321"

    assert old_unused_token.used_at is not None

    assert old_used_token.used_at == old_used_token_time

    assert len(db.added) == 1

    new_token = db.added[0]

    assert new_token.employee_id == employee.id
    assert new_token.token_hash == "hashed-654321"
    assert new_token.channel == "email"


# ---------------------------------------------------------------------------
# Phase 6 Step 4
# Reset-code brute-force protection
# ---------------------------------------------------------------------------


def test_confirm_reset_increments_attempt_count_on_invalid_code(
    monkeypatch,
):
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
        attempt_count=0,
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
            code="111111",
            new_password="NewPassword123!",
        )

    assert reset_record.attempt_count == 1
    assert reset_record.used_at is None
    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert db.committed is True


def test_confirm_reset_rejects_after_max_attempts(
    monkeypatch,
):
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
        attempt_count=5,
    )

    db = FakeDB(
        auth_record=auth_record,
        reset_record=reset_record,
    )

    verify_called = False

    def fake_verify(*_args):
        nonlocal verify_called
        verify_called = True
        return True

    monkeypatch.setattr(
        "repositories.password_reset_repository.verify_password",
        fake_verify,
    )

    with pytest.raises(ValueError):
        repo.confirm_reset(
            db,
            username="john.smith",
            code="482193",
            new_password="NewPassword123!",
        )

    assert verify_called is False
    assert reset_record.attempt_count == 5
    assert reset_record.used_at is None
    assert auth_record.password_hash == "old-hash"
    assert auth_record.is_temporary_password is True
    assert db.committed is False


def test_confirm_reset_allows_valid_code_before_max_attempts(
    monkeypatch,
):
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
        attempt_count=4,
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
        "utils.password_reset_helpers.hash_password",
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

    assert reset_record.attempt_count == 4

    assert db.committed is True
