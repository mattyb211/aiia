import httpx, yfinance, time
from ..core.config import settings

async def _alpha(symbol:str) -> float|None:
    if not settings().ALPHA_KEY: return None
    url = "https://www.alphavantage.co/query"
    p = {"function":"GLOBAL_QUOTE","symbol":symbol,"apikey":settings().ALPHA_KEY}
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            j = (await c.get(url, params=p)).json()
            return float(j["Global Quote"]["05. price"])
        except Exception:
            return None

async def price(symbol:str) -> float:
    p = await _alpha(symbol)
    if p: return p
    return yfinance.Ticker(symbol).info["regularMarketPrice"]

async def enrich(holdings:list[dict]) -> list[dict]:
    out=[]
    for h in holdings:
        out.append({**h,"price":await price(h["ticker"]),"ts":int(time.time())})
    return out