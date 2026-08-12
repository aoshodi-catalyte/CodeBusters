from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from src.database import Base, engine, SessionLocal
from typing import Generator, List
from src.baked_good.baked_good_model import BakedGood
from src.baked_good.baked_good_schema import BakedGoodSchema

def create_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

create_db()

router = APIRouter()

def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for the duration of a request.

    Yields:
        A database session that is closed when the request completes.
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

@router.get("/baked_goods")
def home_page() -> dict[str, str]:

    return {"message": "Hello! You are in Baked Goods. Baked Goods table is currently empty."}

@router.post("/bakedgoods/create", status_code=status.HTTP_201_CREATED, response_model=BakedGood)
def post_baked_good(baked_good: BakedGood, db: Session = Depends(get_db)) -> BakedGoodSchema:
        new_baked_good = BakedGoodSchema(**baked_good.model_dump())
        db.add(new_baked_good)
        db.commit()
        db.refresh(new_baked_good)
        return new_baked_good
