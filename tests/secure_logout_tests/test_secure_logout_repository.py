from datetime import datetime, timezone

import jwt
import pytest

from exceptions.secure_login_exceptions import (
    TokenInvalidSignatureError,
    TokenMissingClaimError
)
from repositories.secure_logout_repository import SecureLogoutRepository
from secure_logout.secure_logout_schema import TokenBlacklist
from utils.jwt_utils import ALGORITHM, SECRET_KEY


def create_test_token(jti: str):
    payload = {
        "sub": "user123",
        "jti": jti,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_logout(db):
    """
    Full integration-style test:
    - real JWT
    - real decode_token()
    - real extract_jti()
    - real DB insert
    """

    repo = SecureLogoutRepository()
    jti_value = "REAL-JTI-999"
    token = create_test_token(jti_value)

    result = repo.logout(token, db)

    saved = db.query(TokenBlacklist).filter_by(token_signature=jti_value).first()

    assert saved.blacklisted_on is not None
    assert saved.token_signature == jti_value

    normalized = saved.blacklisted_on.replace(tzinfo=timezone.utc)
    assert normalized.tzinfo == timezone.utc

    assert result == {"detail": "Token successfully revoked"}


def test_logout_invalid_signature(db):
    repo = SecureLogoutRepository()

    bad_token = jwt.encode(
        {"sub": "user123", "jti": "BAD-JTI"},
        "wrong-secret",
        algorithm=ALGORITHM,
    )

    with pytest.raises(TokenInvalidSignatureError):
        repo.logout(bad_token, db)


def test_logout_missing_jti(db):
    repo = SecureLogoutRepository()

    # Valid token but missing JTI
    token = jwt.encode({"sub": "user123"}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(TokenMissingClaimError):
        repo.logout(token, db)


def test_logout_duplicate_blacklist_entries(db):
    repo = SecureLogoutRepository()
    jti_value = "DUPLICATE-JTI"

    token = create_test_token(jti_value)

    repo.logout(token, db)
    repo.logout(token, db)

    rows = db.query(TokenBlacklist).filter_by(token_signature=jti_value).all()

    assert len(rows) == 2
    for row in rows:
        assert row.token_signature == jti_value
        assert isinstance(row.blacklisted_on, datetime)
