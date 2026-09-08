from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)
from repositories.secure_logout_repository import SecureLogoutRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

logout_repo = SecureLogoutRepository()

@router.post("/logout")
def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        result = logout_repo.logout(token, db)
        return result
    except (TokenInvalidSignatureError, TokenDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    except TokenMissingClaimError:
        raise HTTPException(status_code=401, detail="Token missing required claim: jti")
