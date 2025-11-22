from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Brand, Model, User, UsedCar
from schemas import UsedCarCreateWithNames, UsedCarResponse, UsedCarUpdate

router = APIRouter(prefix="/cars/used", tags=["used cars"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create a used car (with brand/model/user names) ---
@router.post("/", response_model=UsedCarResponse)
def add_used_car(car: UsedCarCreateWithNames, db: Session = Depends(get_db)):
    # Ensure brand exists
    brand = db.query(Brand).filter(Brand.name == car.brand).first()
    if not brand:
        brand = Brand(name=car.brand)
        db.add(brand)
        db.commit()
        db.refresh(brand)

    # Ensure model exists
    model = db.query(Model).filter(Model.name == car.model, Model.brand_id == brand.id).first()
    if not model:
        model = Model(name=car.model, brand_id=brand.id)
        db.add(model)
        db.commit()
        db.refresh(model)

    # Ensure user exists
    user = db.query(User).filter(User.name == car.user).first()
    if not user:
        user = User(name=car.user, type="private")  
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create used car with UUID
    db_car = UsedCar(
        model_id=model.id,
        user_id=user.id,
        year=car.year,
        mileage_km=car.mileage_km,
        price_tnd=car.price_tnd,
        condition=car.condition
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# --- List all used cars ---
@router.get("/", response_model=list[UsedCarResponse])
def list_used_cars(db: Session = Depends(get_db)):
    return db.query(UsedCar).all()

# --- Get a single used car by UUID ---
@router.get("/{car_id}", response_model=UsedCarResponse)
def get_used_car(car_id: str, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    return car

# --- Update a used car by UUID ---
@router.put("/{car_id}", response_model=UsedCarResponse)
def update_used_car(car_id: str, updated_data: UsedCarUpdate, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

# --- Delete a used car by UUID ---
@router.delete("/{car_id}")
def delete_used_car(car_id: str, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    db.delete(car)
    db.commit()
    return {"message": "Used car deleted successfully"}
