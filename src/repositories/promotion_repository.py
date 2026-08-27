"""
Repository for managing promotion database operations.

This module defines the PromotionRepository class, which provides methods
for creating and retrieving promotion records using a SQLAlchemy database
session.
"""

from typing import List

from sqlalchemy.orm import Session

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
        """
        new_promotion= PromotionSchema(**promotion.model_dump())

        self.session.add(new_promotion)
        self.session.commit()
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

    def get_promotion_by_id(self, promotion_id: int) -> PromotionSchema | None:
        """
        Retrieves a promotion from the database by its unique ID.

        Args:
            promotion_id: The unique identifier of the promotion to retrieve.

        Returns:
            The matching PromotionSchema object if found, otherwise None.
        """
        return self.session.query(PromotionSchema).filter(
            PromotionSchema.id == promotion_id
        ).first()