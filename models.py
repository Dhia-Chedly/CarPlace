from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean, Date, Text, TIMESTAMP, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
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
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Ownership relations
    used_cars = relationship("Car", back_populates="seller", cascade="all, delete")
    dealer_versions = relationship("Version", back_populates="dealer", cascade="all, delete")
    bids = relationship("Bid", back_populates="user")
    auctions_won = relationship("Auction", back_populates="winner")
    conversations_as_buyer = relationship("Conversation", foreign_keys="[Conversation.buyer_id]", back_populates="buyer", cascade="all, delete-orphan")
    conversations_as_owner = relationship("Conversation", foreign_keys="[Conversation.owner_id]", back_populates="owner", cascade="all, delete-orphan")
    messages_sent = relationship("Message",foreign_keys="[Message.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    dealer_meta = relationship("Dealer", back_populates="user", uselist=False, cascade="all, delete-orphan")

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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    contact = Column(String(100))

    user = relationship("User", back_populates="dealer_meta")

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

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    # Conversation is only for used car listings
    used_car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)

    # Participants
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_message_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    used_car = relationship("Car")

    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="conversations_as_buyer")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="conversations_as_owner")

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.sent_at"
    )
    __table_args__ = (
        UniqueConstraint("used_car_id", "buyer_id", name="_conv_usedcar_buyer_uc"),
    )

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    used_car_id = Column(Integer, ForeignKey("cars.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    used_car = relationship("Car")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.sent_at")

class AIMessage(Base):
    __tablename__ = "ai_messages"
    id = Column(Integer, primary_key=True, index=True)
    ai_conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, default=datetime.utcnow)

    conversation = relationship("AIConversation", back_populates="messages")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)

    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    body = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP, default=datetime.utcnow)
    read_at = Column(TIMESTAMP, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")

