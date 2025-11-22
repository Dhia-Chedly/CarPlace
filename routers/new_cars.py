from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import NewCar

router = APIRouter(prefix="/cars/new", tags=["new cars"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_new_car(car: dict, db: Session = Depends(get_db)):
    db_car = NewCar(**car)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

@router.get("/")
def list_new_cars(db: Session = Depends(get_db)):
    return db.query(NewCar).all()

@router.get("/{car_id}")
def get_new_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    return car

@router.put("/{car_id}")
def update_new_car(car_id: int, updated_data: dict, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    for key, value in updated_data.items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}")
def delete_new_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(NewCar).filter(NewCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="New car not found")
    db.delete(car)
    db.commit()
    return {"message": "New car deleted successfully"}
