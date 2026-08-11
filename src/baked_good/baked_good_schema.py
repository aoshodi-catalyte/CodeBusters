from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base

class BakedGoodSchema(Base):

    __tablename__ = "baked_goods"
    
    id = Column(Integer, primary_key=True) 
    active = Column(Boolean, default=True)
    name = Column(String, nullable=False) 
    description = Column(String, nullable=False)
    purchasing_cost = Column(Float, nullable=False)
    retail_price = Column(Float, nullable=False)

    vendor_id = Column(Integer, ForeignKey("vendor.id"), nullable=False)

    vendor = relationship("Vendor", back_populates="baked_goods")