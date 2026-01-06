from datetime import datetime, timedelta
from typing import Optional, Set
from fastapi import APIRouter, Depends, HTTPException, status ,Form
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User, UserRole
from schemas import UserOut, UserCreate, Token, OTPVerify, LoginResponse, LoginRequest
from database import get_db
from services.email_service import send_otp_email
import random

import os
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
SECRET_KEY = os.getenv("SECRET_KEY", "eyyyyyyy")  
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# --- Security ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Auth utils ---

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Optional[str] = None, db: Session = Depends(get_db), auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> User:
    # Use the manually passed token or the one from the bearer scheme
    final_token = token
    if not final_token and auth and hasattr(auth, 'credentials'):
        final_token = auth.credentials

    
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not final_token:
        raise cred_exc

    try:
        payload = jwt.decode(final_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
        
    # Check for user existence and active status
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise cred_exc
    return user


def role_required(*allowed: UserRole):
    allowed_roles: Set[UserRole] = set(allowed)
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return checker

# --- Router ---
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    if db.query(User).filter(User.email.ilike(payload.email)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest, 
    db: Session = Depends(get_db)
) -> LoginResponse:

    user = db.query(User).filter(User.email == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if user.is_2fa_enabled:
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
        
        try:
            send_otp_email(user.email, otp)
        except Exception as e:
            # In a real scenario, we might log this and still require OTP if we can't send it,
            # but for this demo, we'll let it fail if email sending fails.
            raise HTTPException(status_code=500, detail=f"Failed to send 2FA email: {str(e)}")

        return LoginResponse(
            message="2FA required. Please check your email for the OTP.",
            two_factor_required=True,
            user=UserOut.from_orm(user)
        )

    token = create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )

    return LoginResponse(
        message="Login successful",
        two_factor_required=False,
        access_token=token,
        user=UserOut.from_orm(user)
    )

@router.post("/verify-otp", response_model=Token)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.otp_code or user.otp_code != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Clear OTP after successful verification
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    token = create_access_token(
        {"sub": str(user.id), "role": user.role.value}
    )
    return Token(access_token=token)
