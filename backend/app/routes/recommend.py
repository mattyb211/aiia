# backend/app/routes/recommend.py
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..utils.auth import get_current_user
from ..utils.ai    import get_portfolio
from ..database    import db

router = APIRouter(tags=["recommend"])


# ───────────────────────── models ──────────────────────────
class RecommendInput(BaseModel):
    budget:      float
    horizon:     int
    risk:        str
    preferences: List[str]
    broker:      Optional[str] = None


class Holding(BaseModel):
    ticker:     str
    allocation: float
    price:      float


class RecommendOutput(BaseModel):
    holdings:     List[Holding]
    generated_at: str


# ───────────────────────── endpoints ───────────────────────
@router.post("/recommend", response_model=RecommendOutput)
async def recommend_endpoint(
    inp: RecommendInput,
    current_user: dict = Depends(get_current_user),
):
    # ⟪ was: inp.model_dump() ⟫
    rec = await get_portfolio(inp.dict())

    await db.history.insert_one(
        {
            "user_id":      ObjectId(current_user["_id"]),
            # ⟪ was: inp.model_dump() ⟫
            "input":        inp.dict(),
            "holdings":     rec["holdings"],
            "generated_at": rec["generated_at"],
        }
    )
    return rec


@router.get("/recommend", response_model=list[RecommendOutput])
async def get_history_endpoint(
    current_user: dict = Depends(get_current_user),
):
    """Return *all* previously generated portfolios for the user."""
    cursor = db.history.find({"user_id": ObjectId(current_user["_id"])})
    docs   = await cursor.to_list(length=None)
    # strip Mongo-specific fields that Pydantic can’t encode
    for d in docs:
        d.pop("_id", None)
        d.pop("user_id", None)
    return docs