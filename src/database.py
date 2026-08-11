"""SQLAlchemy database engine and session configuration.

Provides the database engine, SQLAlchemy session, base class,
database initialization function, and database session dependency.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import settings


DATABASE_URL = settings.DATABASE_URL


print(f"DATABASE URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def create_db() -> None:
    """
    Create all database tables.

    This uses the SQLAlchemy models registered with Base.metadata.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session for FastAPI endpoints.

    The session is automatically closed after the request completes.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()