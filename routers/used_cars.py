from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Brand, Model, User, UsedCar
from routers.auth import get_seller_user, get_current_user
from schemas import UsedCarCreate, UsedCarResponse, UsedCarUpdate , UsedCarReadableResponse
from uuid import UUID

router = APIRouter(prefix="/cars/used", tags=["used cars (Seller Only)"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create a used car (Seller Only) ---
@router.post("/", response_model=UsedCarReadableResponse)
def add_used_car(car: UsedCarCreate, db: Session = Depends(get_db), current_seller: User = Depends(get_seller_user)):
    brand = db.query(Brand).filter(Brand.name == car.brand_name).first()
    if not brand:
        raise HTTPException(status_code=400, detail=f"Brand '{car.brand_name}' does not exist.")

    model = db.query(Model).filter(Model.name == car.model_name, Model.brand_id == brand.id).first()
    if not model:
        raise HTTPException(status_code=400, detail=f"Model '{car.model_name}' does not exist for brand '{car.brand_name}'.")

    db_car = UsedCar(
        model_id=model.id,
        user_id=current_seller.id,
        year=car.year,
        mileage_km=car.mileage_km,
        price_tnd=car.price_tnd,
        condition=car.condition
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return {
        "id": db_car.id,
        "brand": brand.name,
        "model": model.name,
        "seller": current_seller.username,
        "year": db_car.year,
        "mileage_km": db_car.mileage_km,
        "price_tnd": db_car.price_tnd,
        "condition": db_car.condition
    }


@router.get("/", response_model=list[UsedCarReadableResponse])
def list_used_cars(db: Session = Depends(get_db)):
    cars = db.query(UsedCar).all()
    return [
        {
            "id": car.id,
            "brand": car.model_ref.brand.name,
            "model": car.model_ref.name,
            "seller": car.user_ref.username,  # seller is a User
            "year": car.year,
            "mileage_km": car.mileage_km,
            "price_tnd": car.price_tnd,
            "condition": car.condition
        }
        for car in cars
    ]

@router.get("/{car_id}", response_model=UsedCarReadableResponse)
def get_used_car(car_id: UUID, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    return {
        "id": car.id,
        "brand": car.model_ref.brand.name,
        "model": car.model_ref.name,
        "seller": car.user_ref.username,
        "year": car.year,
        "mileage_km": car.mileage_km,
        "price_tnd": car.price_tnd,
        "condition": car.condition
    }


# --- Update a used car by UUID (Seller Only, must own) ---
@router.put("/{car_id}", response_model=UsedCarResponse)
def update_used_car(car_id: str, updated_data: UsedCarUpdate, db: Session = Depends(get_db), current_seller: User = Depends(get_seller_user)):
    """Updates a used car listing. Accessible only by the creating seller."""
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
        
    # Check if the authenticated user is the one who listed the car
    if car.user_id != current_seller.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this listing.")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

# --- Delete a used car by UUID (Seller Only, must own) ---
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_used_car(car_id: str, db: Session = Depends(get_db), current_seller: User = Depends(get_seller_user)):
    """Deletes a used car listing. Accessible only by the creating seller."""
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        return # Idempotent deletion

    # Check if the authenticated user is the one who listed the car
    if car.user_id != current_seller.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this listing.")

    db.delete(car)
    db.commit()