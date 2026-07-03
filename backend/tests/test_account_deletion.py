"""
Tests for DELETE /api/v1/account — the real cascading account deletion.

Verifies: full cascade removes books/characters/profiles (+ R2 assets), the
users doc, and finally the Auth record; a user with no data still succeeds; and
a partial failure (R2 delete raises) does NOT delete the Auth record so the user
is never locked out with orphaned data. No real Firebase/R2/Stripe calls.
"""

import os
from unittest.mock import patch, AsyncMock, MagicMock

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

    from fastapi.testclient import TestClient
    from app.main import app
    from app.routers import account as account_mod


def _client(uid="user-1"):
    app.dependency_overrides[account_mod.get_current_user] = lambda: {
        "uid": uid, "email": "u@t.dev", "tier": "free",
    }
    return TestClient(app, raise_server_exceptions=False)


def _patch_deletion(**overrides):
    """Patch every collaborator the endpoint touches; return the patch context
    plus the mocks so tests can assert on them. Defaults are the happy path."""
    fb = account_mod.firebase
    st = account_mod.storage
    defaults = {
        "get_user_stripe_info": AsyncMock(return_value={}),
        "get_user_books": AsyncMock(return_value=[]),
        "get_user_characters": AsyncMock(return_value=[]),
        "get_user_profiles": AsyncMock(return_value=[]),
        "delete_book": AsyncMock(),
        "delete_character": AsyncMock(),
        "delete_profile": AsyncMock(),
        "delete_user_document": AsyncMock(),
        "delete_auth_user": AsyncMock(),
    }
    defaults.update({k: v for k, v in overrides.items() if k in defaults})
    storage_defaults = {
        "delete_book_assets": overrides.get("delete_book_assets", AsyncMock()),
        "delete_character_assets": overrides.get("delete_character_assets", AsyncMock()),
    }

    patchers = [patch.object(fb, name, m) for name, m in defaults.items()]
    patchers += [patch.object(st, name, m) for name, m in storage_defaults.items()]
    return patchers, defaults, storage_defaults


def _run(patchers, fn):
    started = [p.start() for p in patchers]
    try:
        return fn()
    finally:
        for p in patchers:
            p.stop()


def test_full_cascade_deletes_everything_then_auth():
    patchers, fb_mocks, st_mocks = _patch_deletion(
        get_user_stripe_info=AsyncMock(return_value={"stripe_subscription_id": None}),
        get_user_books=AsyncMock(return_value=[{"book_id": "b1"}, {"book_id": "b2"}]),
        get_user_characters=AsyncMock(return_value=[{"character_id": "c1"}]),
        get_user_profiles=AsyncMock(return_value=[{"profile_id": "p1"}, {"profile_id": "p2"}]),
    )

    def go():
        resp = _client().delete("/api/v1/account")
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "deleted"
        # R2 + Firestore removed for each book/character
        assert st_mocks["delete_book_assets"].await_count == 2
        assert fb_mocks["delete_book"].await_count == 2
        assert st_mocks["delete_character_assets"].await_count == 1
        assert fb_mocks["delete_character"].await_count == 1
        assert fb_mocks["delete_profile"].await_count == 2
        # users doc deleted, then auth LAST
        fb_mocks["delete_user_document"].assert_awaited_once_with("user-1")
        fb_mocks["delete_auth_user"].assert_awaited_once_with("user-1")

    _run(patchers, go)
    app.dependency_overrides.clear()


def test_user_with_no_data_still_succeeds():
    patchers, fb_mocks, st_mocks = _patch_deletion()  # all-empty happy path

    def go():
        resp = _client().delete("/api/v1/account")
        assert resp.status_code == 200
        assert st_mocks["delete_book_assets"].await_count == 0
        fb_mocks["delete_user_document"].assert_awaited_once_with("user-1")
        fb_mocks["delete_auth_user"].assert_awaited_once_with("user-1")

    _run(patchers, go)
    app.dependency_overrides.clear()


def test_r2_failure_does_not_delete_auth():
    patchers, fb_mocks, st_mocks = _patch_deletion(
        get_user_books=AsyncMock(return_value=[{"book_id": "b1"}]),
        delete_book_assets=AsyncMock(side_effect=RuntimeError("R2 unavailable")),
    )

    def go():
        resp = _client().delete("/api/v1/account")
        assert resp.status_code == 500
        # The Auth record and users doc must NOT have been deleted.
        fb_mocks["delete_auth_user"].assert_not_awaited()
        fb_mocks["delete_user_document"].assert_not_awaited()

    _run(patchers, go)
    app.dependency_overrides.clear()


def test_users_doc_failure_does_not_delete_auth():
    patchers, fb_mocks, st_mocks = _patch_deletion(
        delete_user_document=AsyncMock(side_effect=RuntimeError("firestore down")),
    )

    def go():
        resp = _client().delete("/api/v1/account")
        assert resp.status_code == 500
        fb_mocks["delete_auth_user"].assert_not_awaited()

    _run(patchers, go)
    app.dependency_overrides.clear()
