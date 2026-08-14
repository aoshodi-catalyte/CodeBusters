from fastapi import Depends, status, APIRouter
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from typing import Generator, List
from baked_good.baked_good_model import BakedGood
from baked_good.baked_good_repository import BakedGoodRepository


def create_db() -> None:
    """
    Creates the database tables required by the application.

    Drops all existing tables before recreating them using the SQLAlchemy
    engine and Base metadata.

    Args:
        None

    Returns:
        None
    """

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

create_db()

def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for the duration of a request.

     Args:
        None

    Yields:
        A SQLAlchemy database session that can be used to query or modify
        database records.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/baked_goods", 
    tags=["baked_goods"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[BakedGood])
def get_baked_goods(db: Session = Depends(get_db)) -> List[BakedGood]:
    """
    Retrieves all baked goods from the database.

    Args:
        db: The SQLAlchemy database session used to access the
            baked goods stored in the database.

    Returns:
        A list of BakedGood objects representing all baked
        goods stored in the database.
    """

    repo = BakedGoodRepository(db)
    baked_goods = repo.get_baked_goods()

    return baked_goods


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BakedGood)
def post_baked_good(baked_good: BakedGood, db: Session = Depends(get_db)) -> BakedGood:
    """
    Creates and stores a new baked good in the database.

    Converts the validated BakedGood Pydantic model into a
    BakedGoodSchema SQLAlchemy model, adds it to the database,
    commits the transaction, and refreshes the object with its
    database-generated values.

    Args:
        baked_good: The validated baked good data received from the request.
        db: The SQLAlchemy database session provided by the get_db dependency.

    Returns:
        The newly created BakedGood object.
    """     
    repo = BakedGoodRepository(db)
    baked_good_create = repo.create_baked_good(baked_good)

    return baked_good_create
    