"""
Tests for the profiles API.

Tests:
- Create a profile (success)
- Max 5 profiles per user (reject 6th)
- Cannot delete last profile
- Set-default switches default
- Validation: age out of range, missing name
"""

import asyncio
import sys
import os
import unittest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_profile(profile_id: str, uid: str = "user-1", name: str = "Leo",
                  age: int = 5, is_default: bool = False) -> dict:
    return {
        "profile_id": profile_id,
        "uid": uid,
        "name": name,
        "age": age,
        "favorite_themes": ["animals"],
        "avatar_color": "#6366f1",
        "created_at": datetime.now(timezone.utc),
        "is_default": is_default,
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestProfileValidation(unittest.TestCase):
    """Test Pydantic validation on ProfileCreate / ProfileUpdate models."""

    def test_valid_create(self):
        from app.routers.profiles import ProfileCreate
        p = ProfileCreate(name="Leo", age=5, favorite_themes=["animals", "space"])
        self.assertEqual(p.name, "Leo")
        self.assertEqual(p.age, 5)
        self.assertEqual(p.favorite_themes, ["animals", "space"])

    def test_name_required(self):
        from app.routers.profiles import ProfileCreate
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ProfileCreate(name="", age=5, favorite_themes=["animals"])

    def test_age_too_low(self):
        from app.routers.profiles import ProfileCreate
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ProfileCreate(name="Leo", age=1, favorite_themes=["animals"])

    def test_age_too_high(self):
        from app.routers.profiles import ProfileCreate
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ProfileCreate(name="Leo", age=13, favorite_themes=["animals"])

    def test_invalid_theme(self):
        from app.routers.profiles import ProfileCreate
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ProfileCreate(name="Leo", age=5, favorite_themes=["robots"])

    def test_max_3_themes_trimmed(self):
        from app.routers.profiles import ProfileCreate
        p = ProfileCreate(name="Leo", age=5,
                          favorite_themes=["animals", "space", "ocean", "farm"])
        self.assertEqual(len(p.favorite_themes), 3)

    def test_name_sanitized(self):
        from app.routers.profiles import ProfileCreate
        p = ProfileCreate(name="<script>alert('xss')</script>Leo", age=5, favorite_themes=[])
        self.assertNotIn("<script>", p.name)
        self.assertIn("Leo", p.name)


class TestMaxProfileLimit(unittest.TestCase):
    """Test that the 6th profile is rejected."""

    def test_max_5_limit(self):
        from app.routers.profiles import create_profile, ProfileCreate, MAX_PROFILES_PER_USER

        self.assertEqual(MAX_PROFILES_PER_USER, 5)

        # Simulate 5 existing profiles
        existing = [_make_profile(f"p-{i}") for i in range(5)]

        async def run():
            with patch("app.routers.profiles.firebase") as mock_fb:
                mock_fb.get_user_profiles = AsyncMock(return_value=existing)

                from fastapi import HTTPException
                body = ProfileCreate(name="Sixth", age=3, favorite_themes=["animals"])
                try:
                    await create_profile(body=body, user={"uid": "user-1"})
                    self.fail("Should have raised HTTPException")
                except HTTPException as e:
                    self.assertEqual(e.status_code, 400)
                    self.assertIn("Maximum", e.detail)

        asyncio.get_event_loop().run_until_complete(run())


class TestCannotDeleteLastProfile(unittest.TestCase):
    """Test that deleting the only profile fails."""

    def test_cannot_delete_only_profile(self):
        from app.routers.profiles import delete_profile

        only_profile = _make_profile("p-1", is_default=True)

        async def run():
            with patch("app.routers.profiles.firebase") as mock_fb:
                mock_fb.get_profile = AsyncMock(return_value=only_profile)
                mock_fb.get_user_profiles = AsyncMock(return_value=[only_profile])

                from fastapi import HTTPException
                try:
                    await delete_profile(profile_id="p-1", user={"uid": "user-1"})
                    self.fail("Should have raised HTTPException")
                except HTTPException as e:
                    self.assertEqual(e.status_code, 400)
                    self.assertIn("only profile", e.detail)

        asyncio.get_event_loop().run_until_complete(run())


class TestDeletePromotesDefault(unittest.TestCase):
    """When deleting the default profile, another one should become default."""

    def test_promotes_next_profile(self):
        from app.routers.profiles import delete_profile

        p1 = _make_profile("p-1", is_default=True, name="Leo")
        p2 = _make_profile("p-2", is_default=False, name="Mia")

        async def run():
            with patch("app.routers.profiles.firebase") as mock_fb:
                mock_fb.get_profile = AsyncMock(return_value=p1)
                mock_fb.get_user_profiles = AsyncMock(return_value=[p1, p2])
                mock_fb.delete_profile = AsyncMock()
                mock_fb.update_profile = AsyncMock()

                await delete_profile(profile_id="p-1", user={"uid": "user-1"})

                mock_fb.delete_profile.assert_called_once_with("p-1")
                mock_fb.update_profile.assert_called_once_with("p-2", {"is_default": True})

        asyncio.get_event_loop().run_until_complete(run())


class TestSetDefault(unittest.TestCase):
    """Test set-default endpoint clears old defaults and sets new one."""

    def test_set_default(self):
        from app.routers.profiles import set_default_profile

        p2 = _make_profile("p-2", is_default=False, name="Mia")

        async def run():
            with patch("app.routers.profiles.firebase") as mock_fb:
                mock_fb.get_profile = AsyncMock(return_value=p2)
                mock_fb.clear_default_profiles = AsyncMock()
                mock_fb.update_profile = AsyncMock()

                result = await set_default_profile(profile_id="p-2", user={"uid": "user-1"})

                mock_fb.clear_default_profiles.assert_called_once_with("user-1")
                mock_fb.update_profile.assert_called_once_with("p-2", {"is_default": True})
                self.assertTrue(result.is_default)

        asyncio.get_event_loop().run_until_complete(run())


class TestProfileResponseModel(unittest.TestCase):
    """Test that ProfileResponse accepts valid profile data."""

    def test_response_from_dict(self):
        from app.routers.profiles import ProfileResponse
        data = _make_profile("p-1", is_default=True)
        resp = ProfileResponse(**data)
        self.assertEqual(resp.profile_id, "p-1")
        self.assertEqual(resp.name, "Leo")
        self.assertTrue(resp.is_default)


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running profile tests...\n")
    passed = 0
    failures = 0

    for cls in [TestProfileValidation, TestMaxProfileLimit,
                TestCannotDeleteLastProfile, TestDeletePromotesDefault,
                TestSetDefault, TestProfileResponseModel]:
        instance = cls()
        for name in dir(instance):
            if name.startswith("test_"):
                try:
                    getattr(instance, name)()
                    print(f"  PASS: {cls.__name__}.{name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  FAIL: {cls.__name__}.{name} — {e}")
                    failures += 1
                except Exception as e:
                    print(f"  ERROR: {cls.__name__}.{name} — {e}")
                    failures += 1

    print(f"\n{passed} passed, {failures} failed.")
    if failures > 0:
        print(f"\n{failures} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
