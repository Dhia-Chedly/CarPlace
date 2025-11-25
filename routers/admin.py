from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc , func
from database import get_db
from models import Brand, Model, Category, User, Version, UserRole , Car 
from schemas import BrandBase, BrandOut, ModelBase, ModelOut, CategoryOut, AdminStatsOut , UserOut
from .auth import role_required
from typing import Dict, List

router = APIRouter(prefix="/admin", tags=["admin"])

# --- Stats ---

@router.get("/stats", response_model=AdminStatsOut, dependencies=[Depends(role_required(UserRole.admin))])
def get_stats(db: Session = Depends(get_db)) -> AdminStatsOut:
    return AdminStatsOut(
        total_brands=db.query(Brand).count(),
        total_models=db.query(Model).count(),
        total_categories=db.query(Category).count(),
        total_new_cars=db.query(Version).count(),
        total_users=db.query(User).count()
    )

# --- Dealer Stats ---
@router.get("/dealers/{dealer_id}/stats",dependencies=[Depends(role_required(UserRole.admin))])
def dealer_stats(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(User).filter(User.id == dealer_id, User.role == UserRole.dealer).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    total_versions = db.query(Version).filter(Version.dealer_id == dealer_id).count()
    avg_price = db.query(func.avg(Version.price)).filter(Version.dealer_id == dealer_id).scalar()
    return {"dealer_id": dealer.id, "dealer_name": dealer.full_name, "total_versions": total_versions, "avg_price": avg_price}

# --- Seller Stats ---
@router.get("/sellers/{seller_id}/stats",dependencies=[Depends(role_required(UserRole.admin))])
def seller_stats(seller_id: int, db: Session = Depends(get_db)):
    seller = db.query(User).filter(User.id == seller_id, User.role == UserRole.seller).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    total_cars = db.query(func.count()).select_from(Car).filter(Car.seller_id == seller_id).scalar()
    avg_price = db.query(func.avg(Car.price)).filter(Car.seller_id == seller_id).scalar()
    return {"seller_id": seller.id, "seller_name": seller.full_name, "total_cars": total_cars, "avg_price": avg_price}


# --- Brands ---

@router.post("/brands", response_model=BrandOut)
def create_brand(payload: BrandBase, db: Session = Depends(get_db), user=Depends(role_required(UserRole.admin))) -> BrandOut:
    # Unique check for case-insensitive brand name
    if db.query(Brand).filter(Brand.name.ilike(payload.name)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Brand name already exists.")

    brand = Brand(**payload.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.get("/{brand_id}/stats")
def brand_stats(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {
        "brand_id": brand.id,
        "brand_name": brand.name,
        "total_models": db.query(Model).filter(Model.brand_id == brand_id).count()
    }

@router.get("/brands", response_model=List[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    user=Depends(role_required(UserRole.admin)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str | None = Query("name"),
    order_dir: str = Query("asc", regex="^(asc|desc)$")
) -> List[BrandOut]:
    query = db.query(Brand)
    if order_by and hasattr(Brand, order_by):
        col = getattr(Brand, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.offset(offset).limit(limit).all()

@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required(UserRole.admin))])
def delete_brand(brand_id: int, db: Session = Depends(get_db)) -> None:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    db.delete(brand)
    db.commit()

@router.put("/brands/{brand_id}", response_model=BrandOut)
def update_brand(brand_id: int, payload: BrandBase, db: Session = Depends(get_db), user=Depends(role_required(UserRole.admin))) -> BrandOut:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    for key, value in payload.dict().items():
        setattr(brand, key, value)
    db.commit()
    db.refresh(brand)
    return brand

# --- Models ---

@router.post("/{brand_id}/models", response_model=ModelOut)
def create_model_for_brand(brand_id: int, payload: ModelBase, db: Session = Depends(get_db)):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    model = Model(name=payload.name, brand_id=brand_id)
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

@router.put("/{model_id}", response_model=ModelOut)
def update_model(model_id: int, payload: ModelBase, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    for key, value in payload.dict().items():
        setattr(model, key, value)
    db.commit()
    db.refresh(model)
    return model


@router.get("/models", response_model=List[ModelOut])
def list_models( # Renamed internally for consistency, route is fine
    db: Session = Depends(get_db),
    user=Depends(role_required(UserRole.admin)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str | None = Query("name"),
    order_dir: str = Query("asc", regex="^(asc|desc)$")
) -> List[ModelOut]:
    query = db.query(Model)
    if order_by and hasattr(Model, order_by):
        col = getattr(Model, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.offset(offset).limit(limit).all()


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required(UserRole.admin))])
def delete_model(model_id: int, db: Session = Depends(get_db)) -> None:
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    db.delete(model)
    db.commit()

# --- Categories ---

@router.post("/categories", response_model=CategoryOut)
def create_category(name: str, db: Session = Depends(get_db), user=Depends(role_required(UserRole.admin))) -> CategoryOut:
    if db.query(Category).filter(Category.name.ilike(name)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    user=Depends(role_required(UserRole.admin)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str | None = Query("name"),
    order_dir: str = Query("asc", regex="^(asc|desc)$")
) -> List[CategoryOut]:
    query = db.query(Category)
    if order_by and hasattr(Category, order_by):
        col = getattr(Category, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    return query.offset(offset).limit(limit).all()

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required(UserRole.admin))])
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()

# --- Users ---

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_required(UserRole.admin))])
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()

@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    user=Depends(role_required(UserRole.admin)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[UserOut]:
    return db.query(User).offset(offset).limit(limit).all()