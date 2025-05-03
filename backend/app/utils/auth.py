# backend/app/utils/auth.py
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

from ..core.config import settings
from ..database import db

bearer = HTTPBearer()

ALG = "HS256"
TTL_HOURS = 24

def hash_pw(raw: str) -> str:
    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

def verify_pw(raw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw.encode(), hashed.encode())

def create_token(sub: str, email: str) -> str:
    payload = {
        "sub": sub,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=TTL_HOURS)
    }
    return jwt.encode(payload, settings().JWT_SECRET, algorithm=ALG)

def decode_token(tok: str) -> dict:
    try:
        payload = jwt.decode(tok, settings().JWT_SECRET, algorithms=[ALG])
        return {"sub": payload.get("sub"), "email": payload.get("email")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer)
):
    """
    Dependency that returns the full user document from MongoDB,
    or raises 401 if invalid.
    """
    token = creds.credentials
    data = decode_token(token)
    user = await db.users.find_one({"_id": ObjectId(data["sub"])})
    if not user or user.get("email") != data["email"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

