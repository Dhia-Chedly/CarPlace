# routers/chat.py
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from routers.auth import get_current_user
from models import User, Car, AIConversation, AIMessage
from schemas import AIConversationOut

router = APIRouter(prefix="/chat", tags=["chat"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

class ChatIn(BaseModel):
    used_car_id: int | None = None
    message: str

class ChatOut(BaseModel):
    ai_conversation_id: int
    reply: str

@router.post("", response_model=ChatOut)
async def chat(
    payload: ChatIn, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_text = payload.message.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message")

    # 1. Get or create AI Conversation automatically
    conv = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.id,
        AIConversation.used_car_id == payload.used_car_id
    ).first()

    if not conv:
        conv = AIConversation(user_id=current_user.id, used_car_id=payload.used_car_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 2. Build history and context
    history = db.query(AIMessage).filter(AIMessage.ai_conversation_id == conv.id).order_by(AIMessage.sent_at.asc()).all()
    
    system_prompt = (
        "You are 'Antigravity Car Assistant', a helpful AI for the CarPlace marketplace. "
        "Your goal is to help users with car-related questions, listing details, and car buying advice. "
        "IMPORTANT: Only discuss cars, listings, and automotive topics. Politely decline other topics. "
        "Keep responses concise and suitable for text-to-speech."
    )

    if conv.used_car_id:
        car = db.query(Car).get(conv.used_car_id)
        if car:
            system_prompt += (
                f"\n\nCONTEXT - CURRENT LISTING:\n"
                f"- Car: {car.year} {car.model.brand.name} {car.model.name}\n"
                f"- Price: ${car.price}\n"
                f"- Mileage: {car.mileage}km\n"
                f"- Fuel: {car.fuel_type}, Trans: {car.transmission}\n"
                f"- Description: {car.description}"
            )

    # 3. Prepare Gemini request
    # Convert history for Gemini (limited to last 10 messages for token efficiency)
    gemini_contents = [{"role": "user", "parts": [{"text": system_prompt}]}]
    gemini_contents.append({"role": "model", "parts": [{"text": "Understood. I am your CarPlace assistant. How can I help you today?"}]})

    for msg in history[-10:]:
        role = "user" if msg.role == "user" else "model"
        gemini_contents.append({"role": role, "parts": [{"text": msg.content}]})

    gemini_contents.append({"role": "user", "parts": [{"text": user_text}]})

    # 4. Call Gemini
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    body = {"contents": gemini_contents}

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=headers, params=params, json=body)
    
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Gemini error: {r.text}")

    data = r.json()
    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=502, detail="Unexpected Gemini response format")

    # 5. Save to database
    user_msg = AIMessage(ai_conversation_id=conv.id, role="user", content=user_text)
    assistant_msg = AIMessage(ai_conversation_id=conv.id, role="assistant", content=reply_text)
    db.add_all([user_msg, assistant_msg])
    db.commit()

    return ChatOut(ai_conversation_id=conv.id, reply=reply_text)

@router.get("/conversations", response_model=List[AIConversationOut])
def list_ai_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AIConversation).filter(AIConversation.user_id == current_user.id).all()


