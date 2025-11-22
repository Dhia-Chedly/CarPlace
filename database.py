from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your actual PostgreSQL credentials
DATABASE_URL = "postgresql://postgres:yeahdhia1@localhost:8000/car_api_db"
__table_args__ = {"schema": "CarPlace"}
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

