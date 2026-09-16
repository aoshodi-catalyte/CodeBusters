"""
Router for securely logging out users by revoking JWT access tokens.

This module exposes the `/auth/logout` endpoint, which accepts a JWT access
token via the Authorization header, extracts its JTI claim, and stores that
identifier in the token blacklist. Any future authentication checks can use
this blacklist to prevent reuse of previously issued tokens.

The router delegates revocation logic to `SecureLogoutRepository`, and
translates JWT‑related exceptions into appropriate HTTP 401 responses.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)
from repositories.secure_logout_repository import SecureLogoutRepository

router = APIRouter(prefix="/auth", tags=["auth"])
logout_repo = SecureLogoutRepository()


@router.post("/logout")
def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Logout endpoint that revokes the current JWT access token.

    The client must send the token in the Authorization header using the
    format: `Bearer <token>`. The token is decoded, its JTI extracted, and
    the JTI is stored in the blacklist table. Any JWT missing required
    claims or containing an invalid signature results in a 401 response.
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = authorization.split(" ")[1]

    try:
        return logout_repo.logout(token, db)

    except (TokenInvalidSignatureError, TokenDecodeError) as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        ) from exc

    except TokenMissingClaimError as exc:
        raise HTTPException(
            status_code=401,
            detail="Token missing required claim: jti"
        ) from exc
