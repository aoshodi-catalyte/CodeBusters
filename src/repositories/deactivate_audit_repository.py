
from sqlalchemy.orm import Session

from deactivation_log.deactivation_schema import DeactivationRecord
from constants.entity_types import EntityType

class AuditRepository:
    """
    Handles audit logging for deactivation events.
    """
    def __init__(self, audit_db: Session):
        self.audit_db = audit_db

    def record_deactivation(self, item_id: int, item_name: str, user: str, item_type: EntityType):
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
            item_id=item_id,
            item_name=item_name,
            deactivated_by=user,
            entity_type_id=item_type.value
        )
        self.audit_db.add(record)
        self.audit_db.commit()
        self.audit_db.refresh(record)
        return record
