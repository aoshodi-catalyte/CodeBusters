"""
FastAPI router for purchase-related endpoints.

Provides API routes for creating purchases, retrieving a single purchase,
and listing all purchases. Business logic is delegated to the
PurchaseService, keeping the router lightweight and focused on request
handling and response formatting.
"""

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
    """
    Create a new purchase.

    Args:
        payload (PurchaseCreate): Incoming purchase request body.
        db (Session): Database session dependency.

    Returns:
        PurchaseResponse: The created purchase record.
    """
    service = PurchaseService(db)

    try:
        return service.create_purchase(payload)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e


@router.get(
    "/{purchase_id}",
    response_model=PurchaseResponse,
    status_code=status.HTTP_200_OK
)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single purchase by ID.

    Args:
        purchase_id (int): ID of the purchase to retrieve.
        db (Session): Database session dependency.

    Returns:
        PurchaseResponse: The requested purchase record.

    Raises:
        HTTPException: If the purchase does not exist.
    """
    service = PurchaseService(db)
    purchase = service.repo.get_purchase(purchase_id)

    if purchase is None:
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
    """
    Retrieve all purchases.

    Args:
        db (Session): Database session dependency.

    Returns:
        list[PurchaseResponse]: All purchase records.
    """
    service = PurchaseService(db)
    return service.repo.list_purchases()
