from jose import jwt
from secure_logout.secure_logout_schema import TokenBlacklist
from utils.jwt_utils import SECRET_KEY, ALGORITHM


def create_test_token(jti: str):
    return jwt.encode({"sub": "user123", "jti": jti}, SECRET_KEY, algorithm=ALGORITHM)


def test_logout_success(client, db):
    jti_value = "ROUTER-JTI-123"
    token = create_test_token(jti_value)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json() == {"detail": "Token successfully revoked"}

    saved = db.query(TokenBlacklist).filter_by(
        token_signature=jti_value).first()
    assert saved is not None


def test_logout_missing_authorization_header(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.json()[
        "detail"] == "Missing or invalid Authorization header"


def test_logout_invalid_authorization_format(client):
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Token abc123"}
    )

    assert response.status_code == 401
    assert response.json()[
        "detail"] == "Missing or invalid Authorization header"


def test_logout_invalid_signature(client):
    bad_token = jwt.encode(
        {"sub": "user123", "jti": "BAD-JTI"},
        "wrong-secret",
        algorithm=ALGORITHM,
    )

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {bad_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_logout_missing_jti(client):
    token = jwt.encode({"sub": "user123"}, SECRET_KEY, algorithm=ALGORITHM)

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token missing required claim: jti"


def test_logout_duplicate_calls(client, db):
    jti_value = "DUPLICATE-JTI-ROUTER"
    token = create_test_token(jti_value)

    # First logout
    r1 = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r1.status_code == 200

    # Second logout
    r2 = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.status_code == 200

    rows = db.query(TokenBlacklist).filter_by(token_signature=jti_value).all()
    assert len(rows) == 2
