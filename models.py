import uuid
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base

# --- Brand ---
class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

# --- Model ---
class Model(Base):
    __tablename__ = "models"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("CarPlace.brands.id"))

# --- Category ---
class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

# --- Dealer ---
class Dealer(Base):
    __tablename__ = "dealers"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    contact = Column(String)

# --- User ---
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    type = Column(String)  

# --- New Car ---
class NewCar(Base):
    __tablename__ = "new_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(Integer, ForeignKey("CarPlace.models.id"))
    category_id = Column(Integer, ForeignKey("CarPlace.categories.id"))
    dealer_id = Column(Integer, ForeignKey("CarPlace.dealers.id"))
    price_tnd = Column(Float)
    valid_until = Column(Date)

# --- Used Car ---
class UsedCar(Base):
    __tablename__ = "used_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(Integer, ForeignKey("CarPlace.models.id"))
    user_id = Column(Integer, ForeignKey("CarPlace.users.id"))
    year = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=False)
    price_tnd = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
