from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Brand, Model, Category, NewCar, User
from routers.auth import get_dealer_user, get_current_user 
from schemas import NewCarCreate, NewCarResponse, NewCarUpdate , NewCarReadableResponse
from uuid import UUID

router = APIRouter(prefix="/cars/new", tags=["new cars (Dealer Only)"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create a new car (Dealer Only) ---
@router.post("/", response_model=NewCarReadableResponse)
def add_new_car(car: NewCarCreate, db: Session = Depends(get_db), current_dealer: User = Depends(get_dealer_user)):
    # Find brand
    brand = db.query(Brand).filter(Brand.name == car.brand_name).first()
    if not brand:
        raise HTTPException(status_code=400, detail=f"Brand '{car.brand_name}' does not exist.")

    # Find model under that brand
    model = db.query(Model).filter(Model.name == car.model_name, Model.brand_id == brand.id).first()
    if not model:
        raise HTTPException(status_code=400, detail=f"Model '{car.model_name}' does not exist for brand '{car.brand_name}'.")

    # Find category
    category = db.query(Category).filter(Category.name == car.category_name).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Category '{car.category_name}' does not exist.")

    db_car = NewCar(
        model_id=model.id,
        category_id=category.id,
        dealer_id=current_dealer.id,
        price_tnd=car.price_tnd,
        valid_until=car.valid_until
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return {
        "id": db_car.id,
        "brand": brand.name,
        "model": model.name,
        "category": category.name,
        "dealer": current_dealer.username,
        "price_tnd": db_car.price_tnd,
        "valid_until": db_car.valid_until
    }



@router.get("/", response_model=list[NewCarReadableResponse])
def list_new_cars(db: Session = Depends(get_db)):
    cars = db.query(NewCar).all()
    return [
        {
            "id": car.id,
            "brand": car.model_ref.brand.name,
            "model": car.model_ref.name,
            "category": car.category_ref.name,
            "dealer": car.dealer_ref.username,  # dealer is a User
            "price_tnd": car.price_tnd,
            "valid_until": car.valid_until
        }
        for car in cars
    ]

@router.get("/{car_id}", response_model=NewCarReadableResponse)
def get_new_car(car_id: UUID, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    return {
        "id": car.id,
        "brand": car.model_ref.brand.name,
        "model": car.model_ref.name,
        "category": car.category_ref.name,
        "dealer": car.dealer_ref.username,
        "price_tnd": car.price_tnd,
        "valid_until": car.valid_until
    }

# --- Update a car by UUID (Dealer Only, must own) ---
@router.put("/{car_id}", response_model=NewCarResponse)
def update_new_car(car_id: str, updated_data: NewCarUpdate, db: Session = Depends(get_db), current_dealer: User = Depends(get_dealer_user)):
    """Updates a new car listing. Accessible only by the creating dealer."""
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
        
    # Check if the authenticated dealer is the one who listed the car
    db_dealer = db.query(Dealer).filter(Dealer.name == current_dealer.name).first()
    if not db_dealer or car.dealer_id != db_dealer.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this listing.")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

# --- Delete a car by UUID (Dealer Only, must own) ---
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_new_car(car_id: str, db: Session = Depends(get_db), current_dealer: User = Depends(get_dealer_user)):
    """Deletes a new car listing. Accessible only by the creating dealer."""
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        return # Idempotent deletion

    # Check if the authenticated dealer is the one who listed the car
    db_dealer = db.query(Dealer).filter(Dealer.name == current_dealer.name).first()
    if not db_dealer or car.dealer_id != db_dealer.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this listing.")

    db.delete(car)
    db.commit()