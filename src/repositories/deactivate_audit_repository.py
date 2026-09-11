
from sqlalchemy.orm import Session

from deactivation_log.deactivation_schema import DeactivationRecord

class AuditRepository:
    """
    Handles audit logging for deactivation events.
    """
    def __init__(self, audit_db: Session):
        self.audit_db = audit_db

    def record_deactivation(self, entity_id: int, user: str):
        """
        Create and persist an audit record documenting that an entity
        was deactivated by a specific user.

        Args:
            entity_id: ID of the entity being deactivated.
            user: Email of the actor performing the deactivation.

        Returns:
            The persisted DeactivationRecord.
        """
        record = DeactivationRecord(
            entity_id=entity_id,
            deactivated_by=user
        )
        self.audit_db.add(record)
        self.audit_db.commit()
        self.audit_db.refresh(record)
        return record
