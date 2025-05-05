"""
backend/tests/test_auth_flow.py
Smoke-test: user can sign up then log in.

This version is self-contained and adds the backend folder to PYTHONPATH
so `from app.main import app` works in CI.
"""
from __future__ import annotations

import sys
import pathlib
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# -------------------------------------------------------------------------
# Put backend/ on sys.path  >>> app.main is now importable
# -------------------------------------------------------------------------
BACKEND_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app           # noqa: E402  (import after sys.path tweak)
import app.routes.auth as auth_routes  # noqa: E402


# -------------------------------------------------------------------------
# Fake in-memory users collection
# -------------------------------------------------------------------------
class _FakeUsersCollection:
    def __init__(self) -> None:
        self._db: dict[str, dict] = {}

    # mimic async PyMongo methods with plain functions --------------------
    async def find_one(self, query):  # route calls `await db.users.find_one`
        return self._db.get(query.get("email"))

    async def insert_one(self, doc):
        self._db[doc["email"]] = doc
        return SimpleNamespace(inserted_id="fake_id")


# -------------------------------------------------------------------------
# Auto-used fixture that monkey-patches the db in auth routes
# -------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _patch_db(monkeypatch):
    fake_db = SimpleNamespace(users=_FakeUsersCollection())
    monkeypatch.setattr(auth_routes, "db", fake_db)
    yield


# -------------------------------------------------------------------------
# The actual test
# -------------------------------------------------------------------------
def test_signup_then_login():
    client = TestClient(app)

    email = f"ci_{uuid4().hex[:8]}@example.com"
    password = "Secret123!"
    name = "CI User"

    # sign-up -------------------------------------------------------------
    res_signup = client.post("/auth/signup", json={"email": email,
                                                   "password": password,
                                                   "name": name})
    assert res_signup.status_code == 201

    # log-in --------------------------------------------------------------
    res_login = client.post("/auth/login", json={"email": email,
                                                 "password": password})
    assert res_login.status_code == 200

    body = res_login.json()
    assert body.get("token_type") == "bearer"
    assert "access_token" in body
    