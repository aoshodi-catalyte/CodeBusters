from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from database import get_db
from main import app
from routers import secure_login_router


@pytest.fixture
def client():
    def override_get_db():
        yield SimpleNamespace()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def employee_auth():
    return SimpleNamespace(
        employee=SimpleNamespace(
            id=7,
            role=SimpleNamespace(role="manager"),
        )
    )


def test_login_returns_access_token(client, monkeypatch, employee_auth):
    def authenticate_user(_db, username, password):
        assert (username, password) == ("jane", "secret")
        return employee_auth

    monkeypatch.setattr(
        secure_login_router.auth_repo, "authenticate_user", authenticate_user
    )
    monkeypatch.setattr(
        secure_login_router.auth_repo,
        "create_access_token",
        lambda payload: payload,
    )

    response = client.post(
        "/auth/login", data={"username": "jane", "password": "secret"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": {"employee_id": 7, "role": "manager"},
        "token_type": "bearer",
    }


def test_login_rejects_invalid_credentials(client, monkeypatch):
    monkeypatch.setattr(
        secure_login_router.auth_repo, "authenticate_user", lambda *_args: None
    )

    response = client.post(
        "/auth/login", data={"username": "jane", "password": "wrong"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_requires_form_fields(client):
    response = client.post("/auth/login", data={"username": "jane"})

    assert response.status_code == 422


def test_me_returns_current_employee(client, monkeypatch):
    employee = {"id": 7, "email": "jane@example.com"}
    monkeypatch.setattr(
        secure_login_router.auth_repo,
        "get_current_employee",
        lambda _token, _db: employee,
    )

    response = client.get("/auth/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json() == employee


def test_me_rejects_invalid_token(client, monkeypatch):
    def reject_token(_token, _db):
        raise ValueError("Invalid or expired token")

    monkeypatch.setattr(
        secure_login_router.auth_repo, "get_current_employee", reject_token
    )

    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_me_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_me_rejects_missing_employee(client, monkeypatch):
    monkeypatch.setattr(
        secure_login_router.auth_repo, "get_current_employee", lambda *_args: None
    )

    response = client.get("/auth/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_register_returns_success_message(client, monkeypatch):
    captured = {}

    def register(_db, data):
        captured["data"] = data

    monkeypatch.setattr(
        secure_login_router.auth_repo, "register_employee_auth", register
    )

    response = client.post(
        "/auth/register",
        json={"employee_id": 7, "username": "jane", "password": "secret"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Login credentials created successfully"}
    assert captured["data"].employee_id == 7


def test_register_translates_validation_error(client, monkeypatch):
    def reject_registration(*_args):
        raise ValueError("Username already taken")

    monkeypatch.setattr(
        secure_login_router.auth_repo, "register_employee_auth", reject_registration
    )

    response = client.post(
        "/auth/register",
        json={"employee_id": 7, "username": "jane", "password": "secret"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_register_rejects_password_over_bcrypt_limit(client):
    response = client.post(
        "/auth/register",
        json={"employee_id": 7, "username": "jane", "password": "x" * 73},
    )

    assert response.status_code == 422
