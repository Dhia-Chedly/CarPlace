from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, Date, Text, TIMESTAMP, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime 
import enum
from database import Base 

# --- User & Roles ---

class UserRole(str, enum.Enum):
    admin = "admin"
    seller = "seller"
    dealer = "dealer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Ownership relations
    used_cars = relationship("Car", back_populates="seller", cascade="all, delete")
    dealer_versions = relationship("Version", back_populates="dealer", cascade="all, delete")
    bids = relationship("Bid", back_populates="user")
    auctions_won = relationship("Auction", back_populates="winner")

# --- Reference Tables ---

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    country = Column(String(100))
    wmi = Column(String(4), unique=True, nullable=True)
    models = relationship("Model", back_populates="brand", cascade="all, delete-orphan")

class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    vds = Column(String(10), nullable=True)
    brand = relationship("Brand", back_populates="models")
    versions = relationship("Version", back_populates="model", cascade="all, delete-orphan")
    cars = relationship("Car", back_populates="model", cascade="all, delete-orphan")
    
    __table_args__ = (UniqueConstraint('name', 'brand_id', name='_name_brand_uc'),)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    # No direct relationship to Car, uses CarCategoryMap for M2M

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

# --- New Cars (Version) ---

class Version(Base):
    __tablename__ = "versions"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    dealer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) 
    name = Column(String(100), nullable=False)
    year = Column(Integer)
    transmission = Column(String(50))
    fuel_type = Column(String(50))
    horsepower = Column(Integer)
    price = Column(DECIMAL(10, 2), nullable=False)

    model = relationship("Model", back_populates="versions")
    dealer = relationship("User", back_populates="dealer_versions")
    auctions = relationship("Auction", back_populates="vehicle", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('name', 'model_id', name='_version_name_model_uc'),)


# --- Used Cars (Car) ---

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) 
    
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=False)
    transmission = Column(String(50))
    fuel_type = Column(String(50))
    horsepower = Column(Integer)
    price = Column(DECIMAL(10, 2), nullable=False)
    location = Column(String(100))
    description = Column(Text)
    posted_at = Column(TIMESTAMP, default=datetime.utcnow)

    model = relationship("Model", back_populates="cars")
    seller = relationship("User", back_populates="used_cars")
    
    # Many-to-Many relationships via association tables
    categories = relationship("CarCategoryMap", back_populates="car", cascade="all, delete-orphan")
    features = relationship("CarFeature", back_populates="car", cascade="all, delete-orphan")


# --- Used Cars M2M Association Tables ---

class CarCategoryMap(Base):
    __tablename__ = "car_category_map"
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

    car = relationship("Car", back_populates="categories")
    category = relationship("Category")

class CarFeature(Base):
    __tablename__ = "car_features"
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), primary_key=True)
    feature_id = Column(Integer, ForeignKey("features.id", ondelete="CASCADE"), primary_key=True)

    car = relationship("Car", back_populates="features")
    feature = relationship("Feature")


# --- Dealers & Showrooms ---

class Dealer(Base):
    __tablename__ = "dealers_meta" 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    contact = Column(String(100))

# --- BIDS TABLE ---
class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", back_populates="bids")

class AuctionStatus(enum.Enum):
    pending = "pending"
    active = "active"
    closed = "closed"
# --- AUCTIONS TABLE ---
class Auction(Base):
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    starting_bid = Column(DECIMAL(10, 2), nullable=False)
    reserve_price = Column(DECIMAL(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    status = Column(Enum(AuctionStatus), default=AuctionStatus.pending)
    highest_bid = Column(DECIMAL(10, 2))
    highest_bidder_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    ends_at = Column(TIMESTAMP)

    vehicle = relationship("Version", back_populates="auctions")
    bids = relationship("Bid", back_populates="auction")
    winner = relationship("User", back_populates="auctions_won")

