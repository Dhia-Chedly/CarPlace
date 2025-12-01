from fastapi import Depends, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
from sqlalchemy.orm import Session
from models import Auction, Version, Bid, User,AuctionStatus, UserRole 
from schemas import AuctionCreateRequest 
from database import get_db 
from .auth import role_required , get_current_user 
from datetime import datetime, timedelta


router = APIRouter(prefix="/auction", tags=["Auction System"])

# 1. Auction Creation (dealer only)
@router.post("/create")
def create_auction(request: AuctionCreateRequest,
                   db: Session = Depends(get_db),
                   current_dealer: User = Depends(role_required(UserRole.dealer))):
    version = db.query(Version).filter(Version.id == request.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    auction = Auction(
        vehicle_id=request.version_id,
        starting_bid=request.starting_bid,
        reserve_price=request.reserve_price,
        duration=request.duration,
        status=AuctionStatus.pending,
        created_at=datetime.utcnow(),
        ends_at = datetime.utcnow() + timedelta(minutes=request.duration)
    )
    db.add(auction)
    db.commit()
    db.refresh(auction)
    return {"message": f"Auction created for version {request.version_id}", "auction_id": auction.id}



# 2. Auction Start (dealer only)
@router.post("/start/{auction_id}")
def start_auction(auction_id: int, db: Session = Depends(get_db),
                  current_dealer: User = Depends(role_required(UserRole.dealer))):
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    auction.status = AuctionStatus.active
    db.commit()
    return {"message": f"Auction {auction_id} started"}


# 3. Live Bidding (seller only)
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/bid/{auction_id}")
async def bid(websocket: WebSocket, auction_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        token = websocket.query_params.get("token")
        if not token:
            await websocket.send_text("Missing token")
            await websocket.close()
            return

        # Decode token and get current user
        current_user = get_current_user(db=db, token=token)
        if current_user.role != UserRole.seller:
            await websocket.send_text("Only sellers can bid")
            await websocket.close()
            return

        while True:
            data = await websocket.receive_text()
            bid_amount = float(data)

            auction = db.query(Auction).filter(Auction.id == auction_id).first()
            if not auction or auction.status != AuctionStatus.active:
                await websocket.send_text("Auction not active")
                continue

            if auction.highest_bid is None or bid_amount > float(auction.highest_bid):
                auction.highest_bid = bid_amount
                auction.highest_bidder_id = current_user.id

                # persist bid history
                new_bid = Bid(auction_id=auction.id, user_id=current_user.id, amount=bid_amount)
                db.add(new_bid)
                db.commit()

                await manager.broadcast(f"New highest bid: {bid_amount} by user {current_user.id}")
            else:
                await websocket.send_text(f"Bid too low. Current highest: {auction.highest_bid}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)



# 4. Auction Monitoring
@router.get("/status/{auction_id}")
def auction_status(auction_id: int, db: Session = Depends(get_db)):
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    time_remaining = None
    if auction.status == AuctionStatus.active:
        time_remaining = auction.ends_at - datetime.utcnow()

    return {
        "auction_id": auction.id,
        "version_id": auction.vehicle_id,
        "current_highest_bid": auction.highest_bid,
        "highest_bidder": auction.highest_bidder_id,
        "time_remaining": str(time_remaining) if time_remaining else None,
        "status": auction.status.value
    }


# 5. Auction End (dealer only)
@router.post("/end/{auction_id}")
def end_auction(auction_id: int, db: Session = Depends(get_db),
                current_dealer: User = Depends(role_required(UserRole.dealer))):
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction.status = AuctionStatus.closed
    db.commit()

    winner = auction.highest_bidder_id if auction.highest_bid and auction.highest_bid >= auction.reserve_price else None
    return {"message": f"Auction {auction_id} ended", "winner": winner}
