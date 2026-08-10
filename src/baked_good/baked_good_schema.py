from sqlalchemy import Boolean, Column, Float, Integer, String
from database import Base

class BakedGoodSchema(Base):

    __tablename__ = "baked_goods"
    
    id = Column(Integer, primary_key=True) 
    active = Column(Boolean, default=True)
    name = Column(String, nullable=False) 
    description = Column(String, nullable=False)
    purchasing_cost = Column(Float, nullable=False)
    retail_price = Column(Float, nullable=False)