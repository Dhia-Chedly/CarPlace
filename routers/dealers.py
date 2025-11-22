from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Dealer
from schemas import DealerCreate, DealerResponse, DealerUpdate

router = APIRouter(prefix="/dealers", tags=["dealers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Create a dealer ---
@router.post("/", response_model=DealerResponse)
def add_dealer(dealer: DealerCreate, db: Session = Depends(get_db)):
    db_dealer = Dealer(**dealer.dict())
    db.add(db_dealer)
    db.commit()
    db.refresh(db_dealer)
    return db_dealer

# --- List all dealers ---
@router.get("/", response_model=list[DealerResponse])
def list_dealers(db: Session = Depends(get_db)):
    return db.query(Dealer).all()

# --- Get a dealer by ID ---
@router.get("/{dealer_id}", response_model=DealerResponse)
def get_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer

# --- Update a dealer ---
@router.put("/{dealer_id}", response_model=DealerResponse)
def update_dealer(dealer_id: int, updated_data: DealerUpdate, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(dealer, key, value)
    db.commit()
    db.refresh(dealer)
    return dealer

# --- Delete a dealer ---
@router.delete("/{dealer_id}")
def delete_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    db.delete(dealer)
    db.commit()
    return {"message": "Dealer deleted successfully"}
