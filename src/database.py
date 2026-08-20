"""SQLAlchemy database engine and session configuration.

Provides the database engine, SQLAlchemy session, base class,
database initialization function, and database session dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # pylint: disable=invalid-name

Base = declarative_base()


def create_db() -> None:
    """
    Create all database tables.

    This uses the SQLAlchemy models registered with Base.metadata.
    """
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Provide a database session for request scoped dependency injection.

    Creates a new SQLAlchemy session, yields it to the request handler, and
    ensures the session is properly closed after the request completes.

    Yields:
        Session: An active SQLAlchemy session used for database operations.

    Raises:
        SQLAlchemyError: If the session fails to initialize or close properly.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
