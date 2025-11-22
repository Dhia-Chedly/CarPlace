from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import UsedCar

router = APIRouter(prefix="/cars/used", tags=["used cars"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_used_car(car: dict, db: Session = Depends(get_db)):
    db_car = UsedCar(**car)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

@router.get("/")
def list_used_cars(db: Session = Depends(get_db)):
    return db.query(UsedCar).all()

@router.get("/{car_id}")
def get_used_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    return car

@router.put("/{car_id}")
def update_used_car(car_id: int, updated_data: dict, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    for key, value in updated_data.items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car

@router.delete("/{car_id}")
def delete_used_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(UsedCar).filter(UsedCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Used car not found")
    db.delete(car)
    db.commit()
    return {"message": "Used car deleted successfully"}
