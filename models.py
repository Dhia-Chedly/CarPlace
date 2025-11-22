import uuid
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey , DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

# --- Brand ---
class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    models = relationship("Model", back_populates="brand")

# --- Model ---
class Model(Base):
    __tablename__ = "models"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("CarPlace.brands.id"))

    brand = relationship("Brand", back_populates="models")
    new_cars = relationship("NewCar", back_populates="model_ref")
    used_cars = relationship("UsedCar", back_populates="model_ref")

# --- Category ---
class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    new_cars = relationship("NewCar", back_populates="category_ref")

# --- User ---
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Auth fields
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="seller", nullable=False)  # seller, dealer, admin

    # Optional profile info
    name = Column(String)
    phone = Column(String)

    # Relationships
    used_cars = relationship("UsedCar", back_populates="user_ref")
    new_cars = relationship("NewCar", back_populates="dealer_ref")

# --- New Car ---
class NewCar(Base):
    __tablename__ = "new_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(Integer, ForeignKey("CarPlace.models.id"))
    category_id = Column(Integer, ForeignKey("CarPlace.categories.id"))
    dealer_id = Column(Integer, ForeignKey("CarPlace.users.id"))  
    price_tnd = Column(Float)
    valid_until = Column(Date)

    model_ref = relationship("Model", back_populates="new_cars")
    category_ref = relationship("Category", back_populates="new_cars")
    dealer_ref = relationship("User", back_populates="new_cars")

# --- Used Car ---
class UsedCar(Base):
    __tablename__ = "used_cars"
    __table_args__ = {"schema": "CarPlace"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(Integer, ForeignKey("CarPlace.models.id"))
    user_id = Column(Integer, ForeignKey("CarPlace.users.id")) 
    year = Column(Integer)
    mileage_km = Column(Integer)
    price_tnd = Column(Float)
    condition = Column(String)

    model_ref = relationship("Model", back_populates="used_cars")
    user_ref = relationship("User", back_populates="used_cars")

# --- Admin logs table ---
class AdminLog(Base):
    __tablename__ = "admin_logs"
    __table_args__ = {"schema": "CarPlace"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("CarPlace.users.id"), nullable=False)
    action = Column(String, nullable=False)          
    target_id = Column(Integer, nullable=False)      
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship("User")