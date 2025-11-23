from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from database import get_db
from models import Model, Brand
from schemas import ModelOut
from typing import List

router = APIRouter(prefix="/models", tags=["models"])

# --- List all models ---
@router.get("/", response_model=List[ModelOut])
def list_models(
    db: Session = Depends(get_db),
    brand: str | None = Query(None, description="Filter by brand name (case-insensitive)"),
    name: str | None = Query(None, description="Filter by model name (case-insensitive)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("name", description="Sort by field"),
    order_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
) -> List[ModelOut]:
    query = db.query(Model).join(Brand)
    if brand:
        query = query.filter(Brand.name.ilike(f"%{brand}%"))
    if name:
        query = query.filter(Model.name.ilike(f"%{name}%"))
    
    if hasattr(Model, order_by):
        col = getattr(Model, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    
    return query.offset(offset).limit(limit).all()

# --- Get model by ID ---
@router.get("/{model_id}", response_model=ModelOut)
def get_model(model_id: int, db: Session = Depends(get_db)) -> ModelOut:
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return model

# --- Get models by brand ID (Renamed endpoint from '/brand/{brand_id}' to '/by-brand/{brand_id}' to avoid ambiguity) ---
@router.get("/by-brand/{brand_id}", response_model=List[ModelOut])
def get_models_by_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ModelOut]:
    models_list = db.query(Model).filter(Model.brand_id == brand_id).offset(offset).limit(limit).all()
    if not models_list:
        # Check if the brand exists before saying no models were found
        if not db.query(Brand).filter(Brand.id == brand_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No models found for this brand")
        
    return models_list

# --- Search models by name ---
@router.get("/search/", response_model=List[ModelOut])
def search_models(
    q: str,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ModelOut]:
    models_list = db.query(Model).filter(Model.name.ilike(f"%{q}%")).offset(offset).limit(limit).all()
    if not models_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No models found matching the search criteria")
    return models_list