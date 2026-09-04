from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from repositories.secure_logout_repository import SecureLogoutRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

logout_repo = SecureLogoutRepository()


@router.post("/logout")
def logout(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Logout endpoint that revokes the current JWT access token by blacklisting
    its JTI claim. The client must send the token in the Authorization header.
    """

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    result = logout_repo.logout(token, db)
    return result
