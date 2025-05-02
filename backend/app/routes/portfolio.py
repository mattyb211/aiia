from fastapi import APIRouter, Depends
from ..database import db
from ..utils.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/")
async def latest(user=Depends(get_current_user)):
    doc = await db.portfolios.find_one({"user_id":user["_id"]}, sort=[("$natural",-1)])
    return doc or {}

@router.get("/history")
async def history(user=Depends(get_current_user)):
    cur = db.portfolios.find({"user_id":user["_id"]}).sort("$natural",1)
    return [d async for d in cur]

