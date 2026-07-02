"""
Ported from the stale root-level tests/ suite (which never bootstrapped env and
so couldn't import the app). Covers the security-relevant admin gating and the
child-profile input validation. No external calls.
"""

import os
import asyncio
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
    from app.middleware import auth as auth_mod
    from app.routers.profiles import ProfileCreate


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


# ── Admin gating ─────────────────────────────────────────────────────────────

def test_non_admin_gets_403():
    user = {"uid": "random-user", "email": "u@t.com", "tier": "free"}
    with patch.object(auth_mod, "settings", MagicMock(admin_uid_list=["admin-1"])):
        with pytest.raises(HTTPException) as exc:
            _run(auth_mod.get_admin_user(user=user))
    assert exc.value.status_code == 403


def test_admin_allowed():
    user = {"uid": "admin-1", "email": "a@t.com", "tier": "free"}
    with patch.object(auth_mod, "settings", MagicMock(admin_uid_list=["admin-1"])):
        result = _run(auth_mod.get_admin_user(user=user))
    assert result["uid"] == "admin-1"


# ── Child-profile validation ─────────────────────────────────────────────────

def test_profile_age_bounds():
    with pytest.raises(ValueError):
        ProfileCreate(name="Kid", age=1)      # below 2
    with pytest.raises(ValueError):
        ProfileCreate(name="Kid", age=13)     # above 12
    ok = ProfileCreate(name="Kid", age=6)
    assert ok.age == 6


def test_profile_name_sanitized():
    p = ProfileCreate(name="<script>alert(1)</script>Mia", age=5)
    assert "<" not in p.name and "script" not in p.name.lower()


def test_profile_invalid_theme_rejected():
    with pytest.raises(ValueError):
        ProfileCreate(name="Kid", age=5, favorite_themes=["not-a-theme"])


def test_profile_valid_themes_trimmed_to_three():
    p = ProfileCreate(name="Kid", age=5,
                      favorite_themes=["animals", "space", "ocean"])
    assert p.favorite_themes == ["animals", "space", "ocean"]
