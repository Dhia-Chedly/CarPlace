from pydantic import BaseModel, EmailStr
from typing import Optional, List, Set, Dict, Any
from datetime import datetime, date
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
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DealerMetaOut(BaseModel):
    id: int
    name: str
    location: Optional[str]
    contact: Optional[str]
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