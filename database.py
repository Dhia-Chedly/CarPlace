import os
from dotenv import load_dotenv
from sqlalchemy import create_engine , MetaData, text 
from sqlalchemy.orm import sessionmaker, declarative_base , Session
from typing import Generator

load_dotenv()

# --- Database URL ---

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yeahdhia1@localhost:8000/car_api_db")

# --- Engine ---
# Use a short connect timeout so app startup doesn't hang if DB is unreachable
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args={"connect_timeout": 5})

# --- Session ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base ---

metadata = MetaData(schema="CarPlace")
Base = declarative_base(metadata=metadata)

# --- Utility to create schema (NEW) ---
def create_schema_if_not_exists(engine):
    
    schema_name = metadata.schema
    try:
        with engine.connect() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS \"{schema_name}\""))
            connection.commit()
    except Exception as e:
        # Don't block app startup on DB/schema errors; log and continue.
        print(f"Warning: could not create schema '{schema_name}' at startup: {e}")

# --- Dependency ---
def get_db() -> Generator[Session, None, None]:
    """Provides a database session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()