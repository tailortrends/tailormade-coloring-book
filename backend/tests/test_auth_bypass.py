"""
Tests for the dev-test-token auth bypass hardening.

The bypass must be structurally inert outside an explicit debug context:
it requires BOTH settings.debug AND a non-production APP_ENV. Under
APP_ENV=production it must be rejected regardless of any other setting.
No Firebase calls are made — the real verifier is stubbed to reject.
"""

import os
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

# ── Patch Firebase + set env BEFORE importing the app ────────────────────────

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
    # Match the dev-context env other suites rely on. The auth module binds its
    # module-level `settings` on first import, and this suite is imported first;
    # without these the cached settings would carry debug=False and break the
    # dev-test-token path used by sibling test modules.
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("DEBUG", "true")

    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    import app.middleware.auth as auth_mod

# firebase_admin is a MagicMock here, so its exceptions.FirebaseError is not a
# real exception class. Give the middleware a real one to catch.
auth_mod.firebase_admin.exceptions.FirebaseError = type(
    "FirebaseError", (Exception,), {}
)


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _settings(app_env: str, debug: bool):
    return SimpleNamespace(
        app_env=app_env,
        debug=debug,
        is_production=(app_env == "production"),
    )


@pytest.mark.asyncio
async def test_bypass_honored_in_debug_dev():
    """debug=True + APP_ENV=development → dev-test-token is accepted."""
    with patch.object(auth_mod, "settings", _settings("development", True)):
        user = await auth_mod.get_current_user(_creds("dev-test-token"))
    assert user["uid"] == "test-user-123"


@pytest.mark.asyncio
async def test_bypass_rejected_without_debug():
    """debug=False → bypass is inert even in development."""
    with patch.object(auth_mod, "settings", _settings("development", False)), \
         patch.object(auth_mod.firebase_auth, "verify_id_token",
                      side_effect=Exception("not a real token")):
        with pytest.raises(HTTPException) as exc:
            await auth_mod.get_current_user(_creds("dev-test-token"))
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_bypass_rejected_in_production_even_with_debug():
    """APP_ENV=production must reject dev-test-token regardless of debug."""
    with patch.object(auth_mod, "settings", _settings("production", True)), \
         patch.object(auth_mod.firebase_auth, "verify_id_token",
                      side_effect=Exception("not a real token")):
        with pytest.raises(HTTPException) as exc:
            await auth_mod.get_current_user(_creds("dev-test-token"))
    assert exc.value.status_code == 401
