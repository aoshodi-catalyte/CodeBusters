"""
Database schema for storing revoked JWT access tokens.

This module defines the `TokenBlacklist` table, which persists the JTI
(JWT ID) of any token that has been explicitly revoked. Authentication
middleware or repository logic can consult this table to prevent the
reuse of previously issued tokens.
"""

from sqlalchemy import Column, DateTime, Integer, String
from database import Base


class TokenBlacklist(Base):
    """
    ORM model representing a blacklisted JWT access token.

    Each entry stores the token's unique JTI signature and the UTC
    timestamp at which the token was revoked. Any token whose JTI
    appears in this table should be treated as invalid for future
    authentication attempts.
    """

    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token_signature = Column(String, nullable=False)
    blacklisted_on = Column(DateTime(timezone=True), nullable=False)
