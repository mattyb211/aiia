"""
backend/tests/test_auth_flow.py
--------------------------------
Smoke-test that a user can sign-up and immediately log-in.

The real FastAPI app is imported, but we monkey-patch the global
`db` object used inside the auth routes with an in-memory fake so
no external services (Mongo, OpenAI, etc.) are required.
"""
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.routes.auth as auth_routes  # the module that uses `db`


# ------------------------------------------------------------------
# 1️⃣  FAKE in-memory collection
# ------------------------------------------------------------------
class _FakeUsersCollection:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    # mimics `await db.users.find_one(...)` in the routes -------------
    def find_one(self, query):
        return self._store.get(query.get("email"))

    # mimics `await db.users.insert_one(...)`
    def insert_one(self, document):
        self._store[document["email"]] = document

        class _Result:
            inserted_id = "fake_id"

        return _Result()


# ------------------------------------------------------------------
# 2️⃣  PyTest fixture that patches the real `db`
# ------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _patch_db(monkeypatch):
    fake_db = SimpleNamespace(users=_FakeUsersCollection())
    # Replace the `db` used INSIDE the auth routes
    monkeypatch.setattr(auth_routes, "db", fake_db)
    yield


# ------------------------------------------------------------------
# 3️⃣  The actual test
# ------------------------------------------------------------------
def test_signup_then_login():
    client = TestClient(app)

    email = f"ci_{uuid4().hex[:8]}@example.com"
    password = "Secret123!"
    name = "CI User"

    # ---- Sign-up ---------------------------------------------------
    res_signup = client.post(
        "/auth/signup",
        json={"email": email, "password": password, "name": name},
    )
    assert res_signup.status_code == 201

    # ---- Log-in ----------------------------------------------------
    res_login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res_login.status_code == 200
    body = res_login.json()
    # the route returns {"access_token": "...", "token_type": "bearer"}
    assert "access_token" in body
    assert body.get("token_type") == "bearer"
    