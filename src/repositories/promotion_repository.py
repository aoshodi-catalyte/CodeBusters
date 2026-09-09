"""
Repository for managing promotion database operations.

This module defines the PromotionRepository class, which provides methods
for creating, retrieving, updating, and deactivating promotion records
using a SQLAlchemy database session. API-specific logic, such as HTTP
status codes and HTTP exceptions, belongs in the router layer — this
module raises typed domain exceptions instead.
"""

from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions.promotion_exceptions import (
    PromotionCodeAlreadyExistsError,
    PromotionConstraintError,
    PromotionNotFoundError,
)
from promotion.promotion_model import Promotion
from promotion.promotion_schema import PromotionSchema


class PromotionRepository:
    """
    Provides database operations for promotion records.

    The repository uses a SQLAlchemy database session to create and
    manage PromotionSchema objects in the database.

    Args:
        session (Session): SQLAlchemy database session used to interact
            with the promotion table.
    """
    def __init__(self, session: Session) -> None:
        """
        Initialize the PromotionRepository with a database session.

        Args:
            session (Session): SQLAlchemy database session used for
                database operations.
        """
        self.session = session

    def _raise_duplicate_error(
        self,
        exc: IntegrityError,
        promo_code: str,
    ) -> None:
        """
        Inspect an integrity error and raise the appropriate typed
        exception.

        Falls back to a generic constraint error when the offending
        field cannot be determined from the database error.
        """
        error_text = str(exc.orig).lower()

        if "promo_code" in error_text:
            raise PromotionCodeAlreadyExistsError(promo_code) from exc

        raise PromotionConstraintError() from exc

    def create_promotion(self, promotion: Promotion) -> PromotionSchema:
        """
        Create and save a new promotion in the database.

        Converts the Pydantic Promotion model into a SQLAlchemy
        PromotionSchema object, adds it to the database session,
        commits the transaction, and refreshes the object with
        database-generated values.

        Args:
            promotion (Promotion): Pydantic promotion object containing
                the promotion data to be stored.

        Returns:
            PromotionSchema: The newly created promotion database object.

        Raises:
            PromotionCodeAlreadyExistsError:
                If a promotion with the same promo code already exists.
            PromotionConstraintError:
                If the record violates another database constraint.
        """
        new_promotion = PromotionSchema(**promotion.model_dump())

        self.session.add(new_promotion)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            self._raise_duplicate_error(exc, promotion.promo_code)

        self.session.refresh(new_promotion)

        return new_promotion

    def get_all_promotions(self) -> List[PromotionSchema]:
        """
        Retrieve all promotions from the database.

        Queries the PromotionSchema table and returns all promotion records
        currently stored in the database.

        Args:
            None.

        Returns:
            List[PromotionSchema]: A list containing all promotion records
            retrieved from the database.
        """
        return self.session.query(PromotionSchema).all()

    def get_promotion_by_id(self, promotion_id: int) -> PromotionSchema:
        """
        Retrieves a promotion from the database by its unique ID.

        Args:
            promotion_id: The unique identifier of the promotion to retrieve.

        Returns:
            The matching PromotionSchema object.

        Raises:
            PromotionNotFoundError:
                If no promotion exists with the given ID.
        """
        promotion = (
            self.session.query(PromotionSchema)
            .filter(PromotionSchema.id == promotion_id)
            .first()
        )

        if promotion is None:
            raise PromotionNotFoundError(promotion_id)

        return promotion

    def update_promotion(
        self,
        promotion_id: int,
        promotion: Promotion,
    ) -> PromotionSchema:
        """
        Update an existing promotion's properties.

        Args:
            promotion_id: The unique identifier of the promotion to
                update.
            promotion: Validated promotion data to apply.

        Returns:
            The updated PromotionSchema object.

        Raises:
            PromotionNotFoundError:
                If no promotion exists with the given ID.
            PromotionCodeAlreadyExistsError:
                If another promotion already has the given promo code.
            PromotionConstraintError:
                If the update violates another database constraint.
        """
        db_promotion = self.get_promotion_by_id(promotion_id)

        update_data = promotion.model_dump()

        for field, value in update_data.items():
            setattr(db_promotion, field, value)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            self._raise_duplicate_error(exc, promotion.promo_code)

        self.session.refresh(db_promotion)

        return db_promotion

    def deactivate_promotion(self, promotion_id: int) -> PromotionSchema:
        """
        Deactivate a promotion by setting active to False (soft delete).

        The promotion record is preserved for historical purposes;
        only its active status is updated.

        Args:
            promotion_id: The unique identifier of the promotion to
                deactivate.

        Returns:
            The deactivated PromotionSchema object.

        Raises:
            PromotionNotFoundError:
                If no promotion exists with the given ID.
        """
        promotion = self.get_promotion_by_id(promotion_id)

        promotion.active = False

        self.session.commit()
        self.session.refresh(promotion)

        return promotion
