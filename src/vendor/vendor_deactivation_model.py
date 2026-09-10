from sqlalchemy import Column, Integer, DateTime, String
from database import AuditBase  # separate Base for audit DB
from datetime import datetime

class VendorDeactivationRecord(AuditBase):
    __tablename__ = "vendor_deactivation_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, nullable=False)
    deactivated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_by = Column(String, nullable=False)
