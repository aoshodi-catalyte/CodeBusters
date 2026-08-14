"""SQLAlchemy database engine and session configuration.

Provides the database engine, SQLAlchemy session, base class,
database initialization function, and database session dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

DATABASE_URL = settings.DATABASE_URL

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


# def get_db() -> Generator[Session, None, None]:
#     """
#     Provides a database session for FastAPI endpoints.

#     The session is automatically closed after the request completes.
#     """

#     db = SessionLocal()

# Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
