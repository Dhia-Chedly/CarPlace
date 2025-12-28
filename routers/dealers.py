from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from database import get_db
from models import User, UserRole, Version , Dealer
from schemas import UserOut, VersionOut , DealerMetaOut, DealerMetaUpdate, DealerWithMetaOut
from .auth import get_current_user, role_required
from typing import List, Union

router = APIRouter(prefix="/dealers", tags=["dealers"])

# --- List all dealers ---
@router.get("/", response_model=List[Union[DealerWithMetaOut, UserOut]])
def list_dealers(
    db: Session = Depends(get_db),
    include_meta: bool = Query(False, description="Include dealer metadata"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("full_name", description="Sort by field"),
    order_dir: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
) -> List[Union[DealerWithMetaOut, UserOut]]:
    query = db.query(User).filter(User.role == UserRole.dealer, User.is_active == True)
    if hasattr(User, order_by):
        col = getattr(User, order_by)
        query = query.order_by(asc(col) if order_dir == "asc" else desc(col))
    
    dealers = query.offset(offset).limit(limit).all()
    
    if include_meta:
        return [DealerWithMetaOut.from_orm(d) for d in dealers]
    return dealers

# --- Get dealer by ID ---
@router.get("/{dealer_id}", response_model=UserOut)
def get_dealer(dealer_id: int, db: Session = Depends(get_db)) -> UserOut:
    dealer = db.query(User).filter(User.id == dealer_id, User.role == UserRole.dealer).first()
    if not dealer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dealer not found")
    return dealer

# --- List cars (versions) owned by dealer ---
@router.get("/{dealer_id}/cars", response_model=List[VersionOut])
def list_cars_by_dealer(
    dealer_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[VersionOut]:
    dealer = db.query(User).filter(User.id == dealer_id, User.role == UserRole.dealer).first()
    if not dealer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dealer not found")
    
    return db.query(Version).filter(Version.dealer_id == dealer_id).offset(offset).limit(limit).all()

# --- Search dealers by name/email ---
@router.get("/search/", response_model=List[UserOut])
def search_dealers(
    q: str,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[UserOut]:
    dealers_list = db.query(User).filter(
        User.role == UserRole.dealer,
        # Use .ilike for case-insensitive search
        (User.full_name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
    ).offset(offset).limit(limit).all()
    if not dealers_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No dealers found matching the search criteria")
    return dealers_list

# --- Get dealer metadata ---
@router.get("/{dealer_id}/meta", response_model=DealerMetaOut)
def get_dealer_meta(dealer_id: int, db: Session = Depends(get_db)):
    dealer_meta = db.query(Dealer).filter(Dealer.user_id == dealer_id).first()
    if not dealer_meta:
        raise HTTPException(status_code=404, detail="Dealer metadata not found")
    return dealer_meta

# --- Update dealer metadata (Self) ---
@router.put("/me/meta", response_model=DealerMetaOut)
def update_my_meta(
    payload: DealerMetaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(UserRole.dealer))
):
    dealer_meta = db.query(Dealer).filter(Dealer.user_id == current_user.id).first()
    if not dealer_meta:
        if not payload.name:
             raise HTTPException(status_code=400, detail="Name is required for initialization")
        dealer_meta = Dealer(user_id=current_user.id, **payload.dict(exclude_unset=True))
        db.add(dealer_meta)
    else:
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(dealer_meta, key, value)
    db.commit()
    db.refresh(dealer_meta)
    return dealer_meta
