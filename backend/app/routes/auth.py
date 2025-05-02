from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from bson import ObjectId

from ..utils.auth import (
    hash_pw, verify_pw, create_token,
    decode_token, get_current_user
)
from ..database import db

router = APIRouter(prefix="/auth", tags=["auth"])

# Input schemas
class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

# Signup endpoint
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(input: SignupIn):
    if await db.users.find_one({"email": input.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed = hash_pw(input.password)
    res = await db.users.insert_one({
        "name": input.name,
        "email": input.email,
        "password": hashed
    })
    return {"id": str(res.inserted_id), "email": input.email}

# Login endpoint
@router.post("/login")
async def login(input: LoginIn):
    user = await db.users.find_one({"email": input.email})
    if not user or not verify_pw(input.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token(str(user["_id"]), user["email"])
    return {"access_token": token, "token_type": "bearer"}

# "Who am I" endpoint
@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
    }