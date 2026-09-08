from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from purchase.purchase_model import PurchaseCreate, PurchaseResponse
from purchase.purchase_service_logic import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post(
    "",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_purchase(payload: PurchaseCreate, db: Session = Depends(get_db)):
    service = PurchaseService(db)
    purchase = service.create_purchase(payload)
    return purchase


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK
)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    service = PurchaseService(db)
    purchase = service.repo.get_purchase(purchase_id)

    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase ID {purchase_id} not found"
        )

    return purchase


@router.get(
    "",
    response_model=list[PurchaseResponse],
    status_code=status.HTTP_200_OK
)
def list_purchases(db: Session = Depends(get_db)):
    service = PurchaseService(db)
    return service.repo.list_purchases()
