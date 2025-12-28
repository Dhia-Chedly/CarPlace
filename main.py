from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from routers import auth, new_cars, used_cars, admin, brands, dealers, public_models, vin_decoder , compare , auction, conversations , chat

from database import Base, engine, create_schema_if_not_exists 


app = FastAPI(title="Car API", version="1.0")

# --- Ensure the schema exists before creating tables ---
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
app.include_router(vin_decoder.router)
app.include_router(compare.router)
app.include_router(auction.router)
app.include_router(conversations.router)
app.include_router(chat.router)
@app.get("/")
def root():
    return {"message": "Welcome to the Car API 🚗"}