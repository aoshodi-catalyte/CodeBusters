from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship
# from database import Base

class BakedGoodSchema():

    __tablename__ = "baked_goods"
    
    id =   Column(Integer, primary_key=True) 
    active: Column[bool](Boolean, default=True)
    name: Column[str](String, nullable=False) 
    description: Column[str](String, nullable=False)
    purchasing_cost: Column[float](Float, nullable=False)
    retail_price: Column[float](Float, nullable=False)