"""
Utility functions for decoding and validating JWT access tokens.

This module centralizes JWT handling logic used throughout the authentication
system. It provides helpers for securely decoding tokens, translating JWT
library exceptions into domain‑specific authentication errors, and extracting
required claims such as the JTI (JWT ID). These utilities ensure consistent
error handling and validation behavior across repositories and routers.
"""

from fastapi import HTTPException, Request, status
from jose import ExpiredSignatureError, JWTError, jwt

from config import settings
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenExpiredError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def decode_token(token: str) -> dict:
    """
    Decode a JWT access token and translate JWT library exceptions into
    domain‑specific authentication errors.

    This function validates the token signature, checks for expiration,
    and returns the decoded payload. Any signature issues, malformed tokens,
    or expiration errors are converted into custom exceptions used by the
    authentication layer.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise TokenExpiredError() from exc
    except JWTError as exc:
        msg = str(exc).lower()
        if "signature" in msg or "invalid signature" in msg:
            raise TokenInvalidSignatureError() from exc
        raise TokenDecodeError(msg) from exc

    return payload


def extract_jti(payload: dict) -> str:
    """
    Extract the JTI (JWT ID) claim from a decoded JWT payload.

    The JTI uniquely identifies a token and is required for blacklist‑based
    revocation. If the claim is missing, a domain‑specific error is raised
    to signal that the token cannot be processed for logout or validation.
    """
    jti = payload.get("jti")
    if jti is None:
        raise TokenMissingClaimError("jti")
    return jti


def get_token_from_header(request: Request) -> str:
    """
    Extract the raw JWT token from the Authorization header.

    The header must follow the format: `Bearer <token>`. If the header is
    missing or malformed, a 401 Unauthorized error is raised.

    Args:
        request: The incoming FastAPI request containing headers.

    Returns:
        str: The extracted JWT token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )

    return parts[1]