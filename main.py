from fastapi import FastAPI
# Renamed 'modeels' to 'public_models' and added 'brands' and 'dealers'
from routers import auth, new_cars, used_cars, admin, brands, dealers, public_models 

# ADDED 'create_schema_if_not_exists'
from database import Base, engine, create_schema_if_not_exists 


app = FastAPI(title="Car API", version="1.0")

# --- FIX: Ensure the schema exists before creating tables ---
create_schema_if_not_exists(engine)

# Ensure all models are loaded before creating tables
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(brands.router)
app.include_router(dealers.router)
app.include_router(public_models.router)
app.include_router(new_cars.router)
app.include_router(used_cars.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Car API 🚗"}