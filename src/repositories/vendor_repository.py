from src.vendor.vendor_model import VendorBase
from src.vendor.vendor_schema import Vendor
from sqlalchemy.orm import Session

class VendorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_new_vendor(self, vendor_data: VendorBase) -> Vendor:
        db_vendor = Vendor(
            active=vendor_data.active,
            name=vendor_data.name,
            contact_name=vendor_data.contact_name,
            contact_role=vendor_data.contact_role,
            email=vendor_data.email,
            phone=vendor_data.phone
        )
        self.db.add(db_vendor)
        self.db.commit()
        self.db.refresh(db_vendor)

        return db_vendor

    def get_all_vendors(self) -> list[Vendor]:
        return self.db.query(Vendor).all()

    def get_vendor_by_id(self, vendor_id: int) -> Vendor | None:
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()