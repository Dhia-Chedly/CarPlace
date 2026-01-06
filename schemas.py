from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- Auth / User ---

class UserRole(str, Enum):
    admin = "admin"
    seller = "seller"
    dealer = "dealer"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str]

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_2fa_enabled: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    two_factor_required: bool = False
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    user: Optional[UserOut] = None

class DealerMetaBase(BaseModel):
    name: str
    location: Optional[str]
    contact: Optional[str]

class DealerMetaCreate(DealerMetaBase):
    pass

class DealerMetaUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    contact: Optional[str]

class DealerMetaOut(DealerMetaBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class DealerWithMetaOut(UserOut):
    dealer_meta: Optional[DealerMetaOut] = None
    class Config:
        from_attributes = True


# --- Reference Schemas ---

class BrandBase(BaseModel):
    name: str
    country: Optional[str]

class BrandOut(BrandBase):
    id: int
    class Config: from_attributes = True

class ModelBase(BaseModel):
    name: str
    brand_id: int

class ModelOut(BaseModel):
    id: int
    name: str
    brand_id: int
    brand: BrandOut
    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    id: int
    name: str
    class Config: from_attributes=True

class FeatureOut(BaseModel):
    id: int
    name: str
    class Config: from_attributes=True

# --- Admin ---
class AdminStatsOut(BaseModel):
    total_brands: int
    total_models: int
    total_categories: int
    total_new_cars: int
    total_users: int

# --- New Cars (Version) ---

class VersionBase(BaseModel):
    name: str
    model_id: int
    year: int
    transmission: str
    fuel_type: str
    horsepower: int
    price: float

class VersionCreate(VersionBase):
    pass

class VersionUpdate(BaseModel):
    name: Optional[str]
    year: Optional[int]
    transmission: Optional[str]
    fuel_type: Optional[str]
    horsepower: Optional[int]
    price: Optional[float]

class VersionOut(VersionBase):
    id: int
    dealer_id: int
    class Config: from_attributes = True

# --- Used Cars (Car) ---

class UsedCarCreate(BaseModel):
    brand_name: str
    model_name: str
    
    year: int
    mileage: int
    transmission: str
    fuel_type: str
    horsepower: int
    price: float
    location: Optional[str]
    description: Optional[str]
    # Fields to handle many-to-many relationship creation
    category_ids: List[int] = [] 
    feature_ids: List[int] = []

class UsedCarUpdate(BaseModel):
    year: Optional[int]
    mileage: Optional[int]
    transmission: Optional[str]
    fuel_type: Optional[str]
    horsepower: Optional[int]
    price: Optional[float]
    location: Optional[str]
    description: Optional[str]

class UsedCarOut(BaseModel):
    id: int
    brand_name: str
    model_name: str
    seller_id: int
    year: int
    mileage: int
    transmission: str
    fuel_type: str
    horsepower: int
    price: float
    location: Optional[str]
    description: Optional[str]
    posted_at: datetime
    # Nested lists for M2M relations
    categories: List[CategoryOut] = []
    features: List[FeatureOut] = []
    class Config: 
        from_attributes = True

class AuctionCreateRequest(BaseModel):
    version_id: int
    starting_bid: float
    reserve_price: float
    duration: int


# --- Messaging / Conversations ---
class MessageBase(BaseModel):
    body: str

class MessageCreate(MessageBase):
    conversation_id: int

class MessageUpdate(BaseModel):
    read_at: Optional[datetime] = None

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender: UserOut
    body: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    used_car_id: int
    owner_id: Optional[int] = None
    initial_message: Optional[str] = None


class ConversationOut(BaseModel):
    id: int
    used_car_id: int
    buyer: UserOut
    owner: UserOut
    created_at: datetime
    last_message_at: datetime
    last_message: Optional[MessageOut] = None

    class Config:
        from_attributes = True

class ConversationWithMessagesOut(ConversationOut):
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True

# --- AI Messaging ---
class AIMessageBase(BaseModel):
    role: str
    content: str

class AIMessageOut(AIMessageBase):
    id: int
    sent_at: datetime
    class Config:
        from_attributes = True

class AIConversationBase(BaseModel):
    used_car_id: Optional[int] = None

class AIConversationOut(AIConversationBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AIConversationWithMessagesOut(AIConversationOut):
    messages: List[AIMessageOut] = []
    class Config:
        from_attributes = True

