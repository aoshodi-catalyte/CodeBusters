"""Repository for creating and retrieving deactivation log entries."""

from sqlalchemy.orm import Session

from deactivation_log.deactivation_log_schema import DeactivationLogSchema


class DeactivationLogRepository:
    """Provide database operations for deactivation logs."""

    def __init__(self, db: Session):
        """Initialize the repository with a database session."""
        self.db = db

    def create(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        entity_type: str,
        entity_id: int,
        entity_name: str,
        related_entity_type: str,
        related_entity_id: int,
        related_entity_name: str,
        reason: str,
        error_message: str,
    ) -> DeactivationLogSchema:
        """Create a new deactivation log entry."""
        log = DeactivationLogSchema(
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            related_entity_name=related_entity_name,
            reason=reason,
            error_message=error_message,
        )

        self.db.add(log)
        return log

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[DeactivationLogSchema]:
        """Return deactivation logs ordered from newest to oldest."""
        return (
            self.db.query(DeactivationLogSchema)
            .order_by(
                DeactivationLogSchema.deactivated_at.desc(),
                DeactivationLogSchema.id.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, log_id: int) -> DeactivationLogSchema | None:
        """Return a deactivation log by ID, or None if it does not exist."""
        return (
            self.db.query(DeactivationLogSchema)
            .filter(DeactivationLogSchema.id == log_id)
            .first()
        )
