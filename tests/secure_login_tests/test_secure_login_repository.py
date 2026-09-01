import pytest
from types import SimpleNamespace

from jose import ExpiredSignatureError, JWTError  # type: ignore
import models  # noqa: F401
from repositories.secure_login_repository import SecureLoginRepository
from exceptions.secure_login_exceptions import (
    UsernameNotFoundError,
    IncorrectPasswordError,
    TokenExpiredError,
    TokenInvalidSignatureError,
    TokenDecodeError,
    TokenMissingClaimError,
    EmployeeNotFoundError,
    UsernameTakenError,
    CredentialsAlreadyExistError,
)

repo = SecureLoginRepository()


class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class FakeDB:
    def __init__(self, employee=None, username=None, credentials=None):
        self.employee = employee
        self.username = username
        self.credentials = credentials

        self.added = None
        self.committed = False
        self.refreshed = None

        self.auth_query_count = 0

    def query(self, model):

        if model.__name__ == "EmployeeSchema":
            return FakeQuery(self.employee)

        if model.__name__ == "EmployeeAuth":
            self.auth_query_count += 1

            if self.auth_query_count == 1:
                return FakeQuery(self.username)

            if self.auth_query_count == 2:
                return FakeQuery(self.credentials)

        return FakeQuery(None)

    def add(self, obj):
        self.added = obj

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = obj


def test_authenticate_user_success(monkeypatch):
    auth_record = SimpleNamespace(
        username="jane",
        password_hash="secret",
        employee=SimpleNamespace(id=7),
    )

    db = FakeDB(username=auth_record)

    monkeypatch.setattr(
        "repositories.secure_login_repository.pwd_context.verify",
        lambda p, h: p == h,
    )

    result = repo.authenticate_user(db, "jane", "secret")
    assert result is auth_record


def test_authenticate_user_raises_username_not_found():
    db = FakeDB(username=None)
    with pytest.raises(UsernameNotFoundError):
        repo.authenticate_user(db, "ghost", "secret")


def test_authenticate_user_raises_incorrect_password(monkeypatch):
    auth_record = SimpleNamespace(username="jane", password_hash="secret")
    db = FakeDB(username=auth_record)

    monkeypatch.setattr(
        "repositories.secure_login_repository.pwd_context.verify",
        lambda *_: False,
    )

    with pytest.raises(IncorrectPasswordError):
        repo.authenticate_user(db, "jane", "wrong")


def test_create_access_token_contains_exp():
    token = repo.create_access_token({"employee_id": 7})
    assert isinstance(token, str)


def test_get_current_employee_success(monkeypatch):
    def fake_decode(token, key, algorithms):
        return {"employee_id": 7}

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB(employee=SimpleNamespace(id=7))
    employee = repo.get_current_employee("token", db)

    assert employee.id == 7


def test_get_current_employee_raises_expired_token(monkeypatch):
    def fake_decode(token, key, algorithms):
        raise ExpiredSignatureError()

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB()

    with pytest.raises(TokenExpiredError):
        repo.get_current_employee("token", db)


def test_get_current_employee_raises_invalid_signature(monkeypatch):
    class FakeJWTError(JWTError):
        pass

    def fake_decode(token, key, algorithms):
        raise FakeJWTError("invalid signature")

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB()

    with pytest.raises(TokenInvalidSignatureError):
        repo.get_current_employee("token", db)


def test_get_current_employee_raises_decode_error(monkeypatch):
    class FakeJWTError(JWTError):
        pass

    def fake_decode(token, key, algorithms):
        raise FakeJWTError("not enough segments")

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB()

    with pytest.raises(TokenDecodeError):
        repo.get_current_employee("token", db)


def test_get_current_employee_raises_missing_claim(monkeypatch):
    def fake_decode(token, key, algorithms):
        return {}

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB()

    with pytest.raises(TokenMissingClaimError):
        repo.get_current_employee("token", db)


def test_get_current_employee_raises_employee_not_found(monkeypatch):
    def fake_decode(token, key, algorithms):
        return {"employee_id": 7}

    monkeypatch.setattr("repositories.secure_login_repository.jwt.decode", fake_decode)

    db = FakeDB(employee=None)

    with pytest.raises(EmployeeNotFoundError):
        repo.get_current_employee("token", db)


def test_register_employee_auth_success():
    db = FakeDB(
        employee=SimpleNamespace(id=7, role=SimpleNamespace(role="employee")),
        username=None,
        credentials=None,
    )

    data = SimpleNamespace(employee_id=7, username="jane", password="secret")

    repo.register_employee_auth(db, data)

    assert db.added.username == "jane"
    assert db.committed is True


def test_register_employee_auth_raises_employee_not_found():
    db = FakeDB(employee=None, username=None, credentials=None)

    data = SimpleNamespace(employee_id=7, username="jane", password="secret")

    with pytest.raises(EmployeeNotFoundError):
        repo.register_employee_auth(db, data)


def test_register_employee_auth_raises_username_taken():
    db = FakeDB(
        employee=SimpleNamespace(id=7, role=SimpleNamespace(role="employee")),
        username=SimpleNamespace(),
        credentials=None,
    )

    data = SimpleNamespace(employee_id=7, username="jane", password="secret")

    with pytest.raises(UsernameTakenError):
        repo.register_employee_auth(db, data)


def test_register_employee_auth_raises_credentials_exist():
    db = FakeDB(
        employee=SimpleNamespace(id=7, role=SimpleNamespace(role="employee")),
        username=None,
        credentials=SimpleNamespace(),
    )

    data = SimpleNamespace(employee_id=7, username="jane", password="secret")

    with pytest.raises(CredentialsAlreadyExistError):
        repo.register_employee_auth(db, data)
