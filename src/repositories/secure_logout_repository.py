from datetime import datetime, timezone

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)
from secure_logout.secure_logout_schema import TokenBlacklist

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


class SecureLogoutRepository:
    """
    Repository responsible for securely revoking JWT access tokens by
    blacklisting their unique JTI identifiers.

    This ensures that once a user logs out, the token cannot be reused
    even if it has not yet expired.
    """

    def logout(self, token: str, db: Session):
        """
        Blacklist the provided JWT token by extracting its JTI claim
        and storing it in the token_blacklist table.

        Args:
            token (str):
                The JWT access token provided by the client.
            db (Session):
                Active database session.

        Raises:
            TokenInvalidSignatureError:
                If the token signature is invalid.
            TokenDecodeError:
                If the token is malformed.
            TokenMissingClaimError:
                If the token does not contain a JTI claim.
        """

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            msg = str(exc).lower()
            if "signature" in msg or "invalid signature" in msg:
                raise TokenInvalidSignatureError() from exc
            raise TokenDecodeError(msg) from exc

        # Extract JTI
        jti = payload.get("jti")
        if jti is None:
            raise TokenMissingClaimError("jti")

        # Insert into blacklist
        db_token = TokenBlacklist(
            token_signature=jti,
            blacklisted_on=datetime.now(timezone.utc)
        )

        db.add(db_token)
        db.commit()

        return {"detail": "Token successfully revoked"}
