from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload 
from sqlalchemy import asc, desc, func
from database import get_db
from models import Brand, Model, User, UserRole, Car, CarCategoryMap, CarFeature, Category, Feature 
from schemas import UsedCarCreate, UsedCarUpdate, UsedCarOut, CategoryOut, FeatureOut
from .auth import role_required
from typing import List, Optional
router = APIRouter(prefix="/cars/used", tags=["used cars (Seller Only)"])


# Helper function for consistent data fetching
def get_car_with_relations(db: Session, car_id: int) -> Optional[Car]:
    
    return db.query(Car).options(
        joinedload(Car.model).joinedload(Model.brand),
        joinedload(Car.categories).joinedload(CarCategoryMap.category),
        joinedload(Car.features).joinedload(CarFeature.feature)
    ).filter(Car.id == car_id).first()

# Helper function for formatting the output
def format_used_car_output(car: Car) -> UsedCarOut:

    if not car.model or not car.model.brand:
        raise Exception("Car model or brand data is missing.") 
        
    return UsedCarOut.construct(
        id=car.id,
        seller_id=car.seller_id,
        year=car.year,
        mileage=car.mileage,
        transmission=car.transmission,
        fuel_type=car.fuel_type,
        horsepower=car.horsepower,
        price=car.price,
        location=car.location,
        description=car.description,
        posted_at=car.posted_at,
        brand_name=car.model.brand.name,
        model_name=car.model.name,
        categories=[CategoryOut.from_orm(m.category) for m in car.categories],
        features=[FeatureOut.from_orm(f.feature) for f in car.features],
    )


# --- Create a used car (Seller Only) ---
@router.post("/", response_model=UsedCarOut, status_code=status.HTTP_201_CREATED)
def add_used_car(
    payload: UsedCarCreate,
    db: Session = Depends(get_db),
    current_seller: User = Depends(role_required(UserRole.seller))
) -> UsedCarOut:
    # 1. Validation and ID lookups
    brand = db.query(Brand).filter(Brand.name.ilike(payload.brand_name)).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Brand '{payload.brand_name}' does not exist.")

    model = db.query(Model).filter(Model.name.ilike(payload.model_name), Model.brand_id == brand.id).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Model '{payload.model_name}' does not exist for brand '{payload.brand_name}'.")

    # 2. Create the Car (UsedCar) object
    car_data = payload.dict(exclude_unset=True, exclude={'brand_name', 'model_name', 'category_ids', 'feature_ids'})
    car = Car(
        model_id=model.id,
        seller_id=current_seller.id,
        **car_data
    )
    db.add(car)
    db.flush() # Flushed to get car.id before commit to use for M2M tables

    # 3. Handle Categories (M2M Link)
    if payload.category_ids:
        categories = db.query(Category).filter(Category.id.in_(payload.category_ids)).all()
        if len(categories) != len(set(payload.category_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more category IDs are invalid.")
        for cat in categories:
            # Append to the ORM relationship list
            car.categories.append(CarCategoryMap(category=cat))

    # 4. Handle Features (M2M Link)
    if payload.feature_ids:
        features = db.query(Feature).filter(Feature.id.in_(payload.feature_ids)).all()
        if len(features) != len(set(payload.feature_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more feature IDs are invalid.")
        for feat in features:
            # Append to the ORM relationship list
            car.features.append(CarFeature(feature=feat))

    db.commit()
    
    # Reload the car with relations and format the output
    car_with_relations = get_car_with_relations(db, car.id)
    return format_used_car_output(car_with_relations)


# --- List all used cars ---
@router.get("/", response_model=List[UsedCarOut])
def list_used_cars(
    db: Session = Depends(get_db),
    brand: str | None = Query(None),
    model: str | None = Query(None),
    fuel_type: str | None = Query(None),
    transmission: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str | None = Query("posted_at"),
    order_dir: str = Query("desc", regex="^(asc|desc)$")
) -> List[UsedCarOut]:
    
    # Use the helper function's joinedload logic
    query = db.query(Car).join(Model).join(Brand).options(
        joinedload(Car.model).joinedload(Model.brand),
        joinedload(Car.categories).joinedload(CarCategoryMap.category),
        joinedload(Car.features).joinedload(CarFeature.feature)
    )
    
    # Filtering (using ilike)
    if brand:
        query = query.filter(Brand.name.ilike(f"%{brand}%"))
    if model:
        query = query.filter(Model.name.ilike(f"%{model}%"))
    if fuel_type:
        query = query.filter(Car.fuel_type.ilike(f"%{fuel_type}%"))
    if transmission:
        query = query.filter(Car.transmission.ilike(f"%{transmission}%"))
    
    # Sorting
    if order_by and hasattr(Car, order_by):
        col = getattr(Car, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    
    cars = query.offset(offset).limit(limit).all()
    
    # Format and return using the helper
    return [format_used_car_output(car) for car in cars]


# --- Get a used car by ID ---
@router.get("/{car_id}", response_model=UsedCarOut)
def get_used_car(car_id: int, db: Session = Depends(get_db)) -> UsedCarOut:
    car = get_car_with_relations(db, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Used car not found")
    return format_used_car_output(car)


# --- Update a used car (Seller Only, must own) ---
@router.put("/{car_id}", response_model=UsedCarOut)
def update_used_car(
    car_id: int,
    payload: UsedCarUpdate,
    db: Session = Depends(get_db),
    current_seller: User = Depends(role_required(UserRole.seller))
) -> UsedCarOut:
    # Filter by car_id AND seller_id to ensure ownership
    car = db.query(Car).filter(Car.id == car_id, Car.seller_id == current_seller.id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or car not found")
    
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(car, k, v)
        
    db.commit()
    db.refresh(car) # Refresh needed to get the updated fields
    
    # Reload with relations and format
    car_with_relations = get_car_with_relations(db, car.id)
    return format_used_car_output(car_with_relations)


# --- Delete a used car (Seller Only, must own) ---
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_used_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_seller: User = Depends(role_required(UserRole.seller))
) -> None:
    car = db.query(Car).filter(Car.id == car_id, Car.seller_id == current_seller.id).first()
    if not car:
        return  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized or car not found")
    db.delete(car)
    db.commit()

# --- List my used cars (Seller Only) ---
@router.get("/mine", response_model=List[UsedCarOut])
def list_my_used_cars(
    db: Session = Depends(get_db),
    current_seller: User = Depends(role_required(UserRole.seller)),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[UsedCarOut]:
    cars = db.query(Car).filter(Car.seller_id == current_seller.id).offset(offset).limit(limit).all()
    return [format_used_car_output(car) for car in cars]

# --- Seller Stats for current seller ---
@router.get("/stats/mine")
def seller_stats(
    db: Session = Depends(get_db),
    current_seller: User = Depends(role_required(UserRole.seller))
):
    total_listings = db.query(Car).filter(Car.seller_id == current_seller.id).count()
    avg_price = db.query(func.avg(Car.price)).filter(Car.seller_id == current_seller.id).scalar()
    newest_listing_date = db.query(func.max(Car.posted_at)).filter(Car.seller_id == current_seller.id).scalar()
    return {"seller_id": current_seller.id, "total_listings": total_listings, "avg_price": avg_price, "newest_listing_date": newest_listing_date}