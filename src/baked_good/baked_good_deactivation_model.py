from sqlalchemy import Column, Integer, Datetime, String
from database import AuditBase 
from datetime import datetime

class BakedGoodDeactivationRecord(AuditBase):
    __tablename__ = "baked_good_deactivation_records"

    id = Column(Integer, primary_key=True, index=True)
    baked_good_id = Column(Integer, nullable=False)
    deactivated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_by = Column(String, nullable=False)