from pydantic import BaseModel
from datetime import date
from uuid import UUID

# --- New Car Creation ---
class NewCarCreateWithNames(BaseModel):
    brand: str
    model: str
    category: str
    dealer: str   
    price_tnd: float
    valid_until: date | None = None

# --- New Car Response ---
class NewCarResponse(BaseModel):
    id: UUID  
    model_id: int
    category_id: int
    dealer_id: int
    price_tnd: float
    valid_until: date | None = None

    class Config:
        orm_mode = True

# --- New Car Update ---
class NewCarUpdate(BaseModel):
    model_id: int | None = None
    category_id: int | None = None
    dealer_id: int | None = None
    price_tnd: float | None = None
    valid_until: date | None = None


# --- Used Car Creation ---
class UsedCarCreateWithNames(BaseModel):
    brand: str
    model: str
    user: str   
    year: int
    mileage_km: int
    price_tnd: float
    condition: str

# --- Used Car Response ---
class UsedCarResponse(BaseModel):
    id: UUID   
    model_id: int
    user_id: int
    year: int
    mileage_km: int
    price_tnd: float
    condition: str

    class Config:
        orm_mode = True

# --- Used Car Update ---
class UsedCarUpdate(BaseModel):
    model_id: int | None = None
    user_id: int | None = None
    year: int | None = None
    mileage_km: int | None = None
    price_tnd: float | None = None
    condition: str | None = None


# --- Dealer Schemas ---
class DealerCreate(BaseModel):
    name: str
    contact: str | None = None

class DealerResponse(BaseModel):
    id: int
    name: str
    contact: str | None = None

    class Config:
        orm_mode = True

class DealerUpdate(BaseModel):
    name: str | None = None
    contact: str | None = None
