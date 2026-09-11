"""
SQLAlchemy model for recording vendor deactivation events.

This model stores audit information whenever a vendor is deactivated,
including who performed the action and when it occurred.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import AuditBase

class VendorDeactivationRecord(AuditBase):
    """
    Represents an audit log entry documenting the deactivation of a vendor.

    Each record captures the vendor ID, the timestamp of deactivation,
    and the user responsible for performing the action.
    """
    __tablename__ = "vendor_deactivation_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, nullable=False)
    deactivated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_by = Column(String, nullable=False)
