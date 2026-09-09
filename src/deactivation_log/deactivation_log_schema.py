from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class DeactivationLogSchema(Base):
    __tablename__ = "deactivation_log"

    id = Column(Integer, primary_key=True, autoincrement=True)

    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    entity_name = Column(String(255), nullable=False)

    related_entity_type = Column(String(100), nullable=False)
    related_entity_id = Column(Integer, nullable=False)
    related_entity_name = Column(String(255), nullable=False)

    reason = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)

    deactivated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
