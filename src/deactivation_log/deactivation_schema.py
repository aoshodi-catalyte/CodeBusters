"""
SQLAlchemy model for recording deactivation events.

This model stores audit information whenever an entity is deactivated,
including who performed the action and when it occurred.
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import AuditBase

class DeactivationRecord(AuditBase):
    """
    Represents an audit log entry documenting the deactivation of an entity.

    Each record captures the vendor ID, the timestamp of deactivation,
    and the user responsible for performing the action.
    """
    __tablename__ = "deactivation_records"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, nullable=False)
    deactivated_at = Column(DateTime, default=datetime.now(UTC))
    deactivated_by = Column(String, nullable=False)
    entity_type_id = Column(Integer, ForeignKey("entity_type.id"), nullable=False)

    entity_type = relationship("EntityTypeSchema", back_populates="deactivation_records")
