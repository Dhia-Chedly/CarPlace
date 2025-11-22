from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Brand, Model, Category, Dealer, NewCar
from schemas import NewCarCreateWithNames, NewCarResponse, NewCarUpdate

router = APIRouter(prefix="/cars/new", tags=["new cars"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create a new car (with brand/model/category/dealer names) ---
@router.post("/", response_model=NewCarResponse)
def add_new_car(car: NewCarCreateWithNames, db: Session = Depends(get_db)):
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

    # Ensure category exists
    category = db.query(Category).filter(Category.name == car.category).first()
    if not category:
        category = Category(name=car.category)
        db.add(category)
        db.commit()
        db.refresh(category)

    # Ensure dealer exists
    dealer = db.query(Dealer).filter(Dealer.name == car.dealer).first()
    if not dealer:
        dealer = Dealer(name=car.dealer)
        db.add(dealer)
        db.commit()
        db.refresh(dealer)

    # Create car with UUID
    db_car = NewCar(
        model_id=model.id,
        category_id=category.id,
        dealer_id=dealer.id,
        price_tnd=car.price_tnd,
        valid_until=car.valid_until
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# --- List all cars ---
@router.get("/", response_model=list[NewCarResponse])
def list_new_cars(db: Session = Depends(get_db)):
    return db.query(NewCar).all()

# --- Get a single car by UUID ---
@router.get("/{car_id}", response_model=NewCarResponse)
def get_new_car(car_id: str, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    return car

# --- Update a car by UUID ---
@router.put("/{car_id}", response_model=NewCarResponse)
def update_new_car(car_id: str, updated_data: NewCarUpdate, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

# --- Delete a car by UUID ---
@router.delete("/{car_id}")
def delete_new_car(car_id: str, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    db.delete(car)
    db.commit()
    return {"message": "New car deleted successfully"}
