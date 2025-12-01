from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, func
from database import get_db
from models import Brand, Model, Version, User, UserRole
from schemas import VersionCreate, VersionUpdate, VersionOut
from .auth import role_required
from typing import List

router = APIRouter(prefix="/cars/new", tags=["new cars (Dealer Only)"])

# --- Create a new car version (Dealer Only) ---
@router.post("/", response_model=VersionOut, status_code=status.HTTP_201_CREATED)
def add_new_car(
    payload: VersionCreate,
    db: Session = Depends(get_db),
    current_dealer: User = Depends(role_required(UserRole.dealer))
) -> VersionOut:
    # 1. Validate model existence
    model = db.query(Model).filter(Model.id == payload.model_id).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model does not exist.")
    
    # 2. Unique Constraint Check for Version Name
    existing_version = db.query(Version).filter(
        Version.model_id == payload.model_id,
        Version.name.ilike(payload.name) 
    ).first()
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="A version with this name already exists for this model."
        )

    # 3. Create
    version = Version(**payload.dict(), dealer_id=current_dealer.id)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version

# --- List all new cars ---
@router.get("/", response_model=List[VersionOut])
def list_new_cars(
    db: Session = Depends(get_db),
    brand: str | None = Query(None),
    model: str | None = Query(None),
    fuel_type: str | None = Query(None),
    transmission: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str | None = Query("name"),
    order_dir: str = Query("asc", regex="^(asc|desc)$")
) -> List[VersionOut]:
    query = db.query(Version).join(Model).join(Brand)
    if brand:
        query = query.filter(Brand.name.ilike(f"%{brand}%"))
    if model:
        query = query.filter(Model.name.ilike(f"%{model}%"))
    if fuel_type:
        query = query.filter(Version.fuel_type.ilike(f"%{fuel_type}%"))
    if transmission:
        query = query.filter(Version.transmission.ilike(f"%{transmission}%"))
    
    if order_by and hasattr(Version, order_by):
        col = getattr(Version, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    
    return query.offset(offset).limit(limit).all()

# --- Get a new car version by ID ---
@router.get("/{version_id}", response_model=VersionOut)
def get_new_car(version_id: int, db: Session = Depends(get_db)) -> VersionOut:
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="New car not found")
    return version

# --- Update a car version (Dealer Only, must own) ---
@router.put("/{version_id}", response_model=VersionOut)
def update_new_car(
    version_id: int,
    payload: VersionUpdate,
    db: Session = Depends(get_db),
    current_dealer: User = Depends(role_required(UserRole.dealer))
) -> VersionOut:
    version = db.query(Version).filter(Version.id == version_id, Version.dealer_id == current_dealer.id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or version not found")
    
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(version, k, v)
        
    db.commit()
    db.refresh(version)
    return version

# --- Delete a car version (Dealer Only, must own) ---
@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_new_car(
    version_id: int,
    db: Session = Depends(get_db),
    current_dealer: User = Depends(role_required(UserRole.dealer))
) -> None:
    version = db.query(Version).filter(Version.id == version_id, Version.dealer_id == current_dealer.id).first()
    if not version:
        return  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or version not found")
    db.delete(version)
    db.commit()

# --- List my new cars (Dealer Only) ---
@router.get("/mine", response_model=List[VersionOut])
def list_my_new_cars(
    db: Session = Depends(get_db),
    current_dealer: User = Depends(role_required(UserRole.dealer)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[VersionOut]:
    return db.query(Version).filter(Version.dealer_id == current_dealer.id).offset(offset).limit(limit).all()

# --- Dealer Stats for current dealer ---
@router.get("/stats/mine")
def dealer_stats(
    db: Session = Depends(get_db),
    current_dealer: User = Depends(role_required(UserRole.dealer))
):
    total_versions = db.query(Version).filter(Version.dealer_id == current_dealer.id).count()
    avg_price = db.query(func.avg(Version.price)).filter(Version.dealer_id == current_dealer.id).scalar()
    return {"dealer_id": current_dealer.id, "total_versions": total_versions, "avg_price": avg_price}