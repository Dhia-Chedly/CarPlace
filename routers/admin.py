from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User, NewCar, UsedCar
from schemas import UserResponse, NewCarReadableResponse, UsedCarReadableResponse
from database import SessionLocal
from routers.auth import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    return db.query(User).all()

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Delete user
    db.delete(user)
    db.commit()

    # Log action
    log = AdminLog(
        admin_id=current_admin.id,
        action="delete_user",
        target_id=user_id
    )
    db.add(log)
    db.commit()
    return {"message": f"User with id {user_id} deleted successfully"}