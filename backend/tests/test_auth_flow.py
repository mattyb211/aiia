"""
backend/tests/test_auth_flow.py
Smoke-test: sign-up ➜ login round-trip without touching a real DB.
"""

from __future__ import annotations

import os
import sys
import pathlib
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Ensure env-vars expected by app/database.py are present
#    (values don't matter – we will monkey-patch the actual client later)
# ──────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("MONGO_URI", "mongodb://localhost/test")
os.environ.setdefault("MONGO_DB_NAME", "test")

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Put backend/ on PYTHONPATH so "import app.main" works
# ──────────────────────────────────────────────────────────────────────────────
BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# ──────────────────────────────────────────────────────────────────────────────
# 3.  Fake in-memory “collection” & fake Motor client
# ──────────────────────────────────────────────────────────────────────────────
class _FakeCollection:
    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    async def find_one(self, query):          # matches Motor API used in routes
        return self._docs.get(query.get("email"))

    async def insert_one(self, doc):
        self._docs[doc["email"]] = doc
        return SimpleNamespace(inserted_id="fake-id")


class _FakeMotorClient(dict):
    """Behaves like MotorClient()['dbname'] → returns object with .users"""

    def __getitem__(self, name):
        return SimpleNamespace(users=_FakeCollection())


# ──────────────────────────────────────────────────────────────────────────────
# 4.  Patch the real Motor client **before** app.main finishes importing
# ──────────────────────────────────────────────────────────────────────────────
import importlib
motor_asyncio = importlib.import_module("motor.motor_asyncio")  # type: ignore
motor_asyncio.AsyncIOMotorClient = _FakeMotorClient            # type: ignore

from app.main import app                       # noqa: E402
import app.routes.auth as auth_routes          # noqa: E402
import app.database as database_module         # noqa: E402

# replace the db object everywhere it’s referenced
fake_db = SimpleNamespace(users=_FakeCollection())
auth_routes.db = fake_db
database_module.db = fake_db

# ──────────────────────────────────────────────────────────────────────────────
# 5.  The actual test
# ──────────────────────────────────────────────────────────────────────────────
def test_signup_and_login():
    client = TestClient(app)

    email = f"ci_{uuid4().hex[:8]}@example.com"
    password = "StrongP@ss1"
    name = "CI User"

    # sign-up
    res = client.post("/auth/signup", json={"email": email, "password": password, "name": name})
    assert res.status_code == 201

    # login
    res = client.post("/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    body = res.json()
    assert body.get("token_type") == "bearer"
    assert "access_token" in body and body["access_token"]