from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import AuditBase

class EntityTypeSchema(AuditBase):
    __tablename__ = "entity_type"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    deactivation_records = relationship("DeactivationRecord", back_populates="entity_type")