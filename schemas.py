from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID
from typing import Optional

# --- JWT/OAuth2 Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str = Field(..., description="Unique username for login")
    password: str = Field(..., min_length=6,max_length=72, description="Password for the user")
    role: str = Field(..., description="User role: 'seller' or 'dealer'")
    name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    name: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True

# --- New Car Schemas ---
class NewCarCreate(BaseModel):
    brand_name: str
    model_name: str
    category_name: str
    price_tnd: float
    valid_until: Optional[date] = None


class NewCarResponse(BaseModel):
    id: UUID
    model_id: int
    category_id: int
    dealer_id: int
    price_tnd: float
    valid_until: Optional[date] = None

    class Config:
        from_attributes = True

class NewCarUpdate(BaseModel):
    model_id: Optional[int] = None
    category_id: Optional[int] = None
    dealer_id: Optional[int] = None
    price_tnd: Optional[float] = None
    valid_until: Optional[date] = None

# --- New Car Readable Response ---
class NewCarReadableResponse(BaseModel):
    id: UUID
    brand: str
    model: str
    category: str
    dealer: str
    price_tnd: float
    valid_until: Optional[date] = None

    class Config:
        from_attributes = True

# --- Used Car Readable Response ---
class UsedCarReadableResponse(BaseModel):
    id: UUID
    brand: str
    model: str
    seller: str
    year: int
    mileage_km: int
    price_tnd: float
    condition: str

    class Config:
        from_attributes = True
# --- Used Car Schemas ---
class UsedCarCreate(BaseModel):
    brand_name: str
    model_name: str
    year: int
    mileage_km: int
    price_tnd: float
    condition: str


class UsedCarResponse(BaseModel):
    id: UUID
    model_id: int
    user_id: int
    year: int
    mileage_km: int
    price_tnd: float
    condition: str

    class Config:
        from_attributes = True

class UsedCarUpdate(BaseModel):
    model_id: Optional[int] = None
    user_id: Optional[int] = None
    year: Optional[int] = None
    mileage_km: Optional[int] = None
    price_tnd: Optional[float] = None
    condition: Optional[str] = None
