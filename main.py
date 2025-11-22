from fastapi import FastAPI
from routers import  new_cars, used_cars , dealers , users

from database import Base, engine


app = FastAPI(title="Car API", version="1.0")
Base.metadata.create_all(bind=engine)

# routers
app.include_router(used_cars.router)
app.include_router(new_cars.router)
app.include_router(dealers.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Car API 🚗"}
