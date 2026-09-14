"""
SQLAlchemy ORM schema for the `entity_type` table used by the audit
logging system. This table stores the canonical list of entity types
(e.g., vendor, ingredient, baked good) along with their integer IDs.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import AuditBase

class EntityTypeSchema(AuditBase):
    """
    Represents a single entity type in the audit database.

    Each row defines:
    - `id`: the integer identifier (mapped from EntityType enum)
    - `name`: the human‑readable label (e.g., "vendor")
    """
    __tablename__ = "entity_type"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    deactivation_records = relationship("DeactivationRecord", back_populates="entity_type")
