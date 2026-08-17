from promotion.promotion_model import Promotion
from promotion.promotion_schema import PromotionSchema
from sqlalchemy.orm import Session


class PromotionRepository():
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