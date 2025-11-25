from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from database import get_db
from models import Brand, Model
from schemas import BrandOut, ModelOut
from typing import List

router = APIRouter(prefix="/brands", tags=["brands"])

# --- List all brands with optional filtering ---
@router.get("/", response_model=List[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    name: str | None = Query(None, description="Filter by brand name (case-insensitive)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("name", description="Sort by field"),
    order_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
) -> List[BrandOut]:
    query = db.query(Brand)
    if name:
        query = query.filter(Brand.name.ilike(f"%{name}%"))
    if hasattr(Brand, order_by):
        col = getattr(Brand, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.offset(offset).limit(limit).all()

# --- Get brand by ID ---
@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)) -> BrandOut:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand

# --- List models for a brand ---
@router.get("/{brand_id}/models", response_model=List[ModelOut])
def list_models_by_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("name"),
    order_dir: str = Query("asc", regex="^(asc|desc)$")
) -> List[ModelOut]:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
        
    query = db.query(Model).filter(Model.brand_id == brand_id)
    if hasattr(Model, order_by):
        col = getattr(Model, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.offset(offset).limit(limit).all()