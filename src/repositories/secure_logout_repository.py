from datetime import datetime, timezone
from sqlalchemy.orm import Session

from utils.jwt_utils import decode_token, extract_jti
from secure_logout.secure_logout_schema import TokenBlacklist
from exceptions.secure_login_exceptions import (
    TokenDecodeError,
    TokenInvalidSignatureError,
    TokenMissingClaimError,
)


class SecureLogoutRepository:
    """
    Repository responsible for securely revoking JWT access tokens by
    blacklisting their unique JTI identifiers.
    """

    def logout(self, token: str, db: Session):
        """
        Blacklist the provided JWT token by extracting its JTI claim
        and storing it in the token_blacklist table.
        """

        # Decode token using shared utility
        payload = decode_token(token)

        # Extract JTI using shared utility
        jti = extract_jti(payload)

        # Insert JTI into blacklist
        db_token = TokenBlacklist(
            token_signature=jti,
            blacklisted_on=datetime.now(timezone.utc)
        )

        db.add(db_token)
        db.commit()

        return {"detail": "Token successfully revoked"}
