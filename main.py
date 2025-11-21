from fastapi import FastAPI
from routers import cars, dealers

app = FastAPI(title="Car API", version="1.0")

# Include routers
app.include_router(cars.router)
app.include_router(dealers.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Car API 🚗"}
