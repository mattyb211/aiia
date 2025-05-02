
from fastapi import APIRouter, Depends, HTTPException
from ..database import db
from ..utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["user"])

@router.get("/prefs")
async def get_prefs(user = Depends(get_current_user)):
    return user.get("preferences", {})

@router.put("/prefs")
async def save_prefs(prefs: dict, user = Depends(get_current_user)):
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"preferences": prefs}})
    return {"ok": True}
