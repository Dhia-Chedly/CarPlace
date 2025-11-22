from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class NewCar(Base):
    __tablename__ = "new_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price_tnd = Column(Float, nullable=False)
    fuel_type = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    power_hp = Column(Integer)
    co2_emissions = Column(Integer)
    consumption_l_100km = Column(Float)
    discount_percent = Column(Float)
    valid_until = Column(Date)

class UsedCar(Base):
    __tablename__ = "used_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=False)
    price_tnd = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    seller_type = Column(String, nullable=False)
    seller_contact = Column(String, nullable=False)
    valuation = Column(String)
