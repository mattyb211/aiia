# backend/app/utils/ai.py
import os, re, json, asyncio
from datetime import datetime
from pathlib   import Path
from typing    import Any, Dict, List

import requests, yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv

# ───────────────── load .env ─────────────────
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL      = os.getenv("OPENAI_MODEL",   "gpt-4o-mini")
ALPHA_KEY  = os.getenv("ALPHA_VANTAGE_KEY", "")
AV_URL     = "https://www.alphavantage.co/query"

client = OpenAI(api_key=OPENAI_KEY)

# ───────────────── helpers ───────────────────
async def fetch_live_prices(tickers: List[str]) -> Dict[str, float]:
    """Alpha Vantage first, fallback to yfinance."""
    if ALPHA_KEY:
        def _av():
            out: Dict[str, float] = {}
            for t in tickers:
                r = requests.get(
                    AV_URL,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol":   t,
                        "apikey":   ALPHA_KEY,
                    },
                    timeout=10,
                )
                price = float(r.json().get("Global Quote", {}).get("05. price", 0) or 0)
                out[t] = price
            return out
        return await asyncio.to_thread(_av)

    def _yf():
        df = yf.download(tickers, period="1d", interval="1d", progress=False)
        close = df["Close"]
        if isinstance(close, float):  # single ticker
            return {tickers[0]: float(close)}
        return {t: float(close[t].iloc[-1]) for t in tickers}
    return await asyncio.to_thread(_yf)


# ───────────────── core ──────────────────────
async def get_portfolio(profile: Dict[str, Any]) -> Dict[str, Any]:
    """ChatGPT → JSON → live prices."""
    system = {
        "role": "system",
        "content": (
            "You are an expert portfolio strategist.\n"
            "Return ONLY valid JSON like:\n"
            '{ "holdings": [ { "ticker": "XYZ", "allocation": 25 }, ... ] }'
        ),
    }
    user = {"role": "user", "content": json.dumps(profile)}

    def _chat():
        return client.chat.completions.create(
            model=MODEL,
            messages=[system, user],
            temperature=0.0,
            max_tokens=512,
        )

    resp = await asyncio.to_thread(_chat)
    raw  = resp.choices[0].message.content.strip()

    # remove ``` fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", raw, flags=re.DOTALL).strip()

    # grab first {...}
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"LLM did not return JSON:\n{raw}")
    data = json.loads(match.group(0))

    holdings = data.get("holdings", [])
    tickers  = [h["ticker"] for h in holdings]

    prices = await fetch_live_prices(tickers)
    for h in holdings:
        h["price"] = prices.get(h["ticker"], 0.0)

    return {
        "holdings": holdings,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }