"""
Secure Logout Repository

This module provides the data‑access layer responsible for securely revoking
JWT access tokens. A token is considered revoked when its unique JTI (JWT ID)
claim is extracted and persisted in the token_blacklist table. Any future
authentication checks can consult this blacklist to prevent the reuse of
previously issued tokens.

Key responsibilities:
- Decode and validate incoming JWT access tokens.
- Extract the JTI claim using shared JWT utility functions.
- Persist the revoked token signature along with a UTC timestamp.
- Provide a consistent, database‑backed mechanism for token invalidation
  across the authentication system.

This repository is intentionally stateless; all revocation state is stored
in the database so that logout behavior remains consistent across multiple
application instances or deployments.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from secure_logout.secure_logout_schema import TokenBlacklist
from utils.jwt_utils import decode_token, extract_jti


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
