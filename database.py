from sqlalchemy import create_engine , MetaData, text 
from sqlalchemy.orm import sessionmaker, declarative_base , Session
from typing import Generator

# --- Database URL ---

DATABASE_URL = "postgresql://postgres:yeahdhia1@localhost:8000/car_api_db"

# --- Engine ---
engine = create_engine(DATABASE_URL, echo=False, future=True)

# --- Session ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base ---

metadata = MetaData(schema="CarPlace")
Base = declarative_base(metadata=metadata)

# --- Utility to create schema (NEW) ---
def create_schema_if_not_exists(engine):
    
    schema_name = metadata.schema
    
    with engine.connect() as connection:
        
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS \"{schema_name}\"")) 
        connection.commit()

# --- Dependency ---
def get_db() -> Generator[Session, None, None]:
    """Provides a database session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()