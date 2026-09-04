from sqlalchemy import Column, DateTime, Integer, String
from database import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token_signature = Column(String, nullable=False)
    blacklisted_on = Column(DateTime, nullable=False)