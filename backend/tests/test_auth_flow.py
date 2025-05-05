"""
backend/tests/test_smoke.py
A single sanity-check to be sure the FastAPI app starts and /docs is reachable.
"""

# --- 1. Environment tweaks ----------------------------------------------------
# Supply dummy Mongo env-vars so `app.database` doesn’t raise the “MONGO_URI missing” error.
import os
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "aiia_test_db")

# --- 2. Import the FastAPI app -----------------------------------------------
import sys
from pathlib import Path

# Ensure `backend/` is on PYTHONPATH when tests run from the same folder
backend_root = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_root))

from fastapi.testclient import TestClient
from app.main import app   # <— this is your real application object

client = TestClient(app)


# --- 3. The actual test -------------------------------------------------------
def test_docs_endpoint_responds():
    """The OpenAPI docs should load (proves the app can start)."""
    resp = client.get("/docs")
    assert resp.status_code == 200

    