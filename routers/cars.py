from fastapi import APIRouter , HTTPException
from pydantic import BaseModel
class Car(BaseModel):
    id: int
    brand: str
    model: str
    year: int

router = APIRouter(prefix="/cars", tags=["cars"])

# Dummy data
cars_db = [
    {"id": 1, "brand": "Toyota", "model": "Corolla", "year": 2025},
    {"id": 2, "brand": "Peugeot", "model": "208", "year": 2025}
]
# --- Endpoints ---

# GET all cars
@router.get("/")
def list_cars():
    return cars_db

# GET single car
@router.get("/{car_id}")
def get_car(car_id: int):
    car = next((c for c in cars_db if c["id"] == car_id), None)
    if car:
        return car
    return {"error": "Car not found"}

# POST: Add new car
@router.post("/")
def add_car(car: Car):
    # Check if ID already exists
    if any(c["id"] == car.id for c in cars_db):
        raise HTTPException(status_code=400, detail="Car with this ID already exists")
    cars_db.append(car.dict())
    return {"message": "Car added successfully", "car": car}

# PUT: Update existing car
@router.put("/{car_id}")
def update_car(car_id: int, updated_car: Car):
    for idx, c in enumerate(cars_db):
        if c["id"] == car_id:
            cars_db[idx] = updated_car.dict()
            return {"message": "Car updated successfully", "car": updated_car}
    raise HTTPException(status_code=404, detail="Car not found")

# DELETE: Remove car
@router.delete("/{car_id}")
def delete_car(car_id: int):
    for idx, c in enumerate(cars_db):
        if c["id"] == car_id:
            deleted = cars_db.pop(idx)
            return {"message": "Car deleted successfully", "car": deleted}
    raise HTTPException(status_code=404, detail="Car not found")
