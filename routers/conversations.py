from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import Dict, List, Tuple

from database import get_db
from models import Conversation, Car, Message, User
from routers.auth import get_current_user
from schemas import (
    ConversationCreate,
    ConversationOut,
    ConversationWithMessagesOut,
    MessageCreate,
    MessageOut,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _format_message(message: Message) -> MessageOut:
    # MessageOut is configured with from_attributes=True, so from_orm will nest sender
    return MessageOut.from_orm(message)


def _format_conversation(conv: Conversation, db: Session, include_messages: bool = False):
    # Load last message
    last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.sent_at.desc()).first()
    last_message_out = _format_message(last_msg) if last_msg else None

    base = ConversationOut.construct(
        id=conv.id,
        used_car_id=conv.used_car_id,
        buyer=conv.buyer,
        owner=conv.owner,
        created_at=conv.created_at,
        last_message_at=conv.last_message_at,
        last_message=last_message_out,
    )

    if include_messages:
        # ensure messages and senders are loaded in order
        conv_messages = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.sent_at).all()
        msgs = [_format_message(m) for m in conv_messages]
        return ConversationWithMessagesOut(**base.__dict__, messages=msgs)

    return base


@router.post("/", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationOut:
    # Validate used car exists
    car = db.query(Car).filter(Car.id == payload.used_car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Used car not found")

    # Ensure owner matches car seller if provided
    if payload.owner_id and payload.owner_id != car.seller_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="owner_id does not match listing owner")

    # Prevent duplicate conversation for same buyer and car
    existing = db.query(Conversation).filter(Conversation.used_car_id == payload.used_car_id, Conversation.buyer_id == current_user.id).first()
    if existing:
        # return existing conversation
        return _format_conversation(existing, db)

    conv = Conversation(used_car_id=payload.used_car_id, buyer_id=current_user.id, owner_id=car.seller_id)
    db.add(conv)
    db.flush()

    # Optional initial message
    if payload.initial_message:
        msg = Message(conversation_id=conv.id, sender_id=current_user.id, body=payload.initial_message, sent_at=datetime.utcnow())
        db.add(msg)
        conv.last_message_at = msg.sent_at

    db.commit()
    db.refresh(conv)
    return _format_conversation(conv, db)


@router.get("/", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ConversationOut]:
    convs = db.query(Conversation).options(joinedload(Conversation.buyer), joinedload(Conversation.owner)).filter(
        (Conversation.buyer_id == current_user.id) | (Conversation.owner_id == current_user.id)
    ).order_by(Conversation.last_message_at.desc()).all()

    return [_format_conversation(c, db) for c in convs]


@router.get("/{conversation_id}", response_model=ConversationWithMessagesOut)
def get_conversation(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ConversationWithMessagesOut:
    conv = db.query(Conversation).options(joinedload(Conversation.buyer), joinedload(Conversation.owner)).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if current_user.id not in (conv.buyer_id, conv.owner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant")

    return _format_conversation(conv, db, include_messages=True)

@router.patch("/messages/{message_id}/read", response_model=MessageOut)
def mark_read(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> MessageOut:
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
    if current_user.id not in (conv.buyer_id, conv.owner_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant")

    msg.read_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)
    return _format_message(msg)


# --- WebSocket chat for real-time messaging ---
class ChatConnectionManager:
    def __init__(self):
        # mapping: conversation_id -> list of (websocket, user_id)
        self.connections: Dict[int, List[Tuple[WebSocket, int]]] = {}

    async def connect(self, conv_id: int, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.connections.setdefault(conv_id, []).append((websocket, user_id))

    def disconnect(self, conv_id: int, websocket: WebSocket):
        conns = self.connections.get(conv_id, [])
        self.connections[conv_id] = [(ws, uid) for ws, uid in conns if ws is not websocket]
        if not self.connections[conv_id]:
            del self.connections[conv_id]

    async def broadcast_except(self, conv_id: int, message: str, exclude_user_id: int):
        conns = list(self.connections.get(conv_id, []))
        for ws, uid in conns:
            if uid == exclude_user_id:
                continue
            try:
                await ws.send_text(message)
            except Exception:
                # ignore failures; they will be cleaned up on disconnect
                pass

manager = ChatConnectionManager()


@router.websocket("/message/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: int, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept()
        await websocket.send_text("Missing token")
        await websocket.close()
        return

    # authenticate
    try:
        current_user = get_current_user(db=db, token=token)
    except Exception:
        await websocket.accept()
        await websocket.send_text("Invalid token")
        await websocket.close()
        return

    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        await websocket.accept()
        await websocket.send_text("Conversation not found")
        await websocket.close()
        return

    if current_user.id not in (conv.buyer_id, conv.owner_id):
        await websocket.accept()
        await websocket.send_text("Not a participant")
        await websocket.close()
        return

    await manager.connect(conversation_id, websocket, current_user.id)

    try:
        while True:
            data = await websocket.receive_text()
            # persist message
            msg = Message(conversation_id=conv.id, sender_id=current_user.id, body=data, sent_at=datetime.utcnow())
            db.add(msg)
            conv.last_message_at = msg.sent_at
            db.commit()
            db.refresh(msg)

            payload = MessageOut.from_orm(msg).json()

            # Broadcast to other participant(s)
            await manager.broadcast_except(conversation_id, payload, current_user.id)
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
    except Exception:
        manager.disconnect(conversation_id, websocket)
        try:
            await websocket.close()
        except Exception:
            pass
