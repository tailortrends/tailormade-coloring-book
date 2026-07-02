"""
Tests for the per-user/day generation ceiling that gates paid fal.ai calls
(shared by book and character generation). The concurrency test proves the
reservation is atomic: with a ceiling of 1, N simultaneous reservations yield
exactly one success. No real Firestore or fal.ai calls are made.
"""

import os
import types
import asyncio
import threading
from unittest.mock import patch, MagicMock

import pytest

mock_firebase = MagicMock()
mock_firebase._apps = {"default": True}

with patch.dict("sys.modules", {
    "firebase_admin": mock_firebase,
    "firebase_admin.auth": MagicMock(),
    "firebase_admin.credentials": MagicMock(),
    "firebase_admin.firestore": MagicMock(),
    "google.cloud.firestore_v1": MagicMock(),
    "sentry_sdk": MagicMock(),
}):
    os.environ.setdefault("FAL_KEY", "test")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test")
    os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
    os.environ.setdefault("R2_ACCOUNT_ID", "test")
    os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
    os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
    os.environ.setdefault("R2_BUCKET_NAME", "test")
    os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")

    from fastapi import HTTPException
    from fastapi.testclient import TestClient
    from unittest.mock import AsyncMock
    from app.middleware import rate_limit
    from app.main import app
    from app.routers import characters as characters_mod


# ── A tiny thread-safe fake Firestore that serializes transactions ───────────

class _FakeSnapshot:
    def __init__(self, data):
        self.exists = data is not None
        self._data = data or {}

    def to_dict(self):
        return dict(self._data)


class _FakeDocRef:
    def __init__(self, store, key):
        self._store = store
        self._key = key

    def get(self, transaction=None):
        return _FakeSnapshot(self._store.get(self._key))


class _FakeCollection:
    def __init__(self, store):
        self._store = store

    def document(self, key):
        return _FakeDocRef(self._store, key)


class _FakeTransaction:
    def __init__(self, store):
        self._store = store

    def set(self, doc_ref, data, merge=False):
        key = doc_ref._key
        if merge and key in self._store:
            self._store[key] = {**self._store[key], **data}
        else:
            self._store[key] = dict(data)


class _FakeDB:
    def __init__(self):
        self._store = {}
        self.lock = threading.Lock()

    def collection(self, _name):
        return _FakeCollection(self._store)

    def transaction(self):
        return _FakeTransaction(self._store)


def _fake_firestore():
    db = _FakeDB()

    def transactional(fn):
        # Serialize the read-check-write, modeling Firestore transaction isolation.
        def wrapper(transaction, *args, **kwargs):
            with db.lock:
                return fn(transaction, *args, **kwargs)
        return wrapper

    fake = types.SimpleNamespace(client=lambda: db, transactional=transactional)
    return fake, db


@pytest.mark.asyncio
async def test_daily_ceiling_reservation_is_atomic():
    """Ceiling=1, 20 concurrent reservations → exactly one succeeds."""
    fake_fs, db = _fake_firestore()
    with patch.object(rate_limit, "firestore", fake_fs), \
         patch.object(rate_limit.settings, "daily_generation_ceiling", 1):

        async def attempt():
            try:
                await rate_limit.reserve_daily_generation("user-1")
                return True
            except HTTPException as e:
                assert e.status_code == 429
                return False

        results = await asyncio.gather(*[attempt() for _ in range(20)])

    assert sum(results) == 1
    assert db._store["user-1"]["daily_count"] == 1


def test_create_character_rejects_over_cap():
    """At the per-user character cap, creation is refused BEFORE any fal.ai call."""
    reserve_called = []

    async def spy_reserve(uid):
        reserve_called.append(uid)

    app.dependency_overrides[characters_mod.get_current_user] = lambda: {
        "uid": "user-1", "email": "u@t.dev", "tier": "free",
    }
    with patch.object(characters_mod.firebase, "get_user_characters",
                      AsyncMock(return_value=[{"character_id": str(i)} for i in range(5)])), \
         patch.object(characters_mod, "reserve_daily_generation", spy_reserve):
        client = TestClient(app)
        resp = client.post(
            "/api/v1/characters/",
            data={"name": "Mia", "relationship": "daughter", "character_type": "person"},
            files={"image": ("photo.png", b"\x89PNG\r\n", "image/png")},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 400
    assert "Maximum" in resp.json()["detail"]
    assert reserve_called == []  # never reached the paid reservation/generation


@pytest.mark.asyncio
async def test_release_returns_a_slot():
    """A released reservation frees a slot so the next call succeeds."""
    fake_fs, db = _fake_firestore()
    with patch.object(rate_limit, "firestore", fake_fs), \
         patch.object(rate_limit.settings, "daily_generation_ceiling", 1):
        await rate_limit.reserve_daily_generation("user-1")
        # Ceiling reached
        with pytest.raises(HTTPException):
            await rate_limit.reserve_daily_generation("user-1")
        # Release, then a new reservation fits
        await rate_limit.release_daily_generation("user-1")
        await rate_limit.reserve_daily_generation("user-1")

    assert db._store["user-1"]["daily_count"] == 1
