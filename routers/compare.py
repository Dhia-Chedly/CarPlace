from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.used_cars import get_car_with_relations, format_used_car_output
from models import Car
from services.AIComparision import generate_comparison

router = APIRouter(prefix="/compare", tags=["AI Comparison"])

@router.get("/")
def compare_cars(car1_id: int, car2_id: int, db: Session = Depends(get_db)):
    car1 = get_car_with_relations(db, car1_id)
    car2 = get_car_with_relations(db, car2_id)
    if not car1 or not car2:
        raise HTTPException(status_code=404, detail="Car not found")

    car1_dict = format_used_car_output(car1).dict()
    car2_dict = format_used_car_output(car2).dict()

    ai_summary = generate_comparison(car1_dict, car2_dict)


    return {
        "ai_summary": ai_summary
    }