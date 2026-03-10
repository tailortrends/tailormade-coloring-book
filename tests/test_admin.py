"""
Tests for the admin API and analytics.

Tests:
- Admin stats returns correct shape
- Non-admin user gets 403
- Daily analytics doc is incremented correctly
- Failed book is recorded to Firestore
"""

import asyncio
import sys
import os
import unittest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock
from datetime import datetime, timezone


# ── Admin Auth Tests ─────────────────────────────────────────────────────────

class TestAdminAuth(unittest.TestCase):
    """Test that admin endpoints reject non-admin users."""

    def test_non_admin_gets_403(self):
        from app.middleware.auth import get_admin_user
        from fastapi import HTTPException

        async def run():
            user = {"uid": "random-user-123", "email": "user@test.com", "tier": "free"}
            with patch("app.middleware.auth.settings") as mock_settings:
                mock_settings.admin_uid_list = ["admin-uid-1"]
                try:
                    await get_admin_user(user=user)
                    self.fail("Should have raised HTTPException")
                except HTTPException as e:
                    self.assertEqual(e.status_code, 403)
                    self.assertIn("Admin", e.detail)

        asyncio.get_event_loop().run_until_complete(run())

    def test_admin_user_passes(self):
        from app.middleware.auth import get_admin_user

        async def run():
            user = {"uid": "admin-uid-1", "email": "admin@test.com", "tier": "free"}
            with patch("app.middleware.auth.settings") as mock_settings:
                mock_settings.admin_uid_list = ["admin-uid-1"]
                result = await get_admin_user(user=user)
                self.assertEqual(result["uid"], "admin-uid-1")

        asyncio.get_event_loop().run_until_complete(run())


# ── Admin Stats Shape Tests ──────────────────────────────────────────────────

class TestAdminStatsShape(unittest.TestCase):
    """Test that /admin/stats returns the expected fields."""

    def test_stats_empty_costs(self):
        from app.routers.admin import get_stats

        async def run():
            with patch("app.routers.admin.firebase") as mock_fb:
                mock_fb.get_all_costs = AsyncMock(return_value=[])
                result = await get_stats(user={"uid": "admin"})
                self.assertEqual(result["total_books"], 0)
                self.assertIn("books_this_month", result)
                self.assertIn("avg_cost_per_book", result)
                self.assertIn("library_hit_rate", result)
                self.assertIn("top_themes", result)
                self.assertIn("books_by_tier", result)
                self.assertIsNone(result["most_expensive_book"])

        asyncio.get_event_loop().run_until_complete(run())

    def test_stats_with_costs(self):
        from app.routers.admin import get_stats

        costs = [
            {
                "book_id": "b-1",
                "uid": "u-1",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_cost": 0.5,
                "image_cost": 0.4,
                "planning_cost": 0.1,
                "retry_count": 1,
                "theme": "animals",
                "title": "My Book",
                "library_hits": 3,
                "library_misses": 2,
            },
            {
                "book_id": "b-2",
                "uid": "u-2",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_cost": 0.3,
                "image_cost": 0.2,
                "planning_cost": 0.1,
                "retry_count": 0,
                "theme": "space",
                "title": "Space Book",
                "library_hits": 5,
                "library_misses": 0,
            },
        ]

        async def run():
            with patch("app.routers.admin.firebase") as mock_fb:
                mock_fb.get_all_costs = AsyncMock(return_value=costs)
                result = await get_stats(user={"uid": "admin"})
                self.assertEqual(result["total_books"], 2)
                self.assertGreater(result["total_spend"], 0)
                self.assertGreater(result["library_hit_rate"], 0)
                self.assertEqual(len(result["top_themes"]), 2)
                self.assertIsNotNone(result["most_expensive_book"])
                self.assertEqual(result["most_expensive_book"]["book_id"], "b-1")

        asyncio.get_event_loop().run_until_complete(run())


# ── Daily Analytics Tests ────────────────────────────────────────────────────

class TestDailyAnalytics(unittest.TestCase):
    """Test daily analytics recording in firebase."""

    def test_record_daily_analytics_calls_firestore(self):
        from app.services.firebase import record_daily_analytics

        async def run():
            with patch("app.services.firebase.firestore") as mock_fs:
                mock_db = MagicMock()
                mock_fs.client.return_value = mock_db
                mock_ref = MagicMock()
                mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_ref

                await record_daily_analytics({
                    "books_generated": 1,
                    "pages_generated": 6,
                    "library_hits": 3,
                    "library_misses": 3,
                    "total_cost": 0.5,
                    "failures": 0,
                    "themes": {"animals": 1},
                    "tiers": {"free": 1},
                })

                mock_ref.set.assert_called_once()
                call_args = mock_ref.set.call_args
                # Verify merge=True
                self.assertTrue(call_args[1].get("merge", False))

        asyncio.get_event_loop().run_until_complete(run())


# ── Failure Recording Tests ──────────────────────────────────────────────────

class TestFailureRecording(unittest.TestCase):
    """Test that generation failures are saved to Firestore."""

    def test_record_failed_book(self):
        from app.routers.books import _record_failed_book
        from app.models.book import BookRequest

        request = BookRequest(
            title="Test Book",
            theme="animals",
            age_range="6-9",
            page_count=6,
        )

        async def run():
            with patch("app.routers.books.firebase") as mock_fb:
                mock_fb.save_book = AsyncMock()
                await _record_failed_book("b-fail", "u-1", request, "Test error")
                mock_fb.save_book.assert_called_once()
                saved_data = mock_fb.save_book.call_args[0][1]
                self.assertEqual(saved_data["status"], "failed")
                self.assertEqual(saved_data["error"], "Test error")
                self.assertEqual(saved_data["book_id"], "b-fail")

        asyncio.get_event_loop().run_until_complete(run())


class TestAnalyticsHelper(unittest.TestCase):
    """Test the _record_analytics helper."""

    def test_record_analytics_success(self):
        from app.routers.books import _record_analytics
        from app.models.book import BookRequest

        request = BookRequest(
            title="Test Book",
            theme="animals",
            age_range="6-9",
            page_count=6,
        )

        class FakeMetrics:
            library_hits = 3
            library_misses = 3

        async def run():
            with patch("app.routers.books.firebase") as mock_fb:
                mock_fb.record_daily_analytics = AsyncMock()
                await _record_analytics(request, "free", FakeMetrics(), 0.5, failed=False)
                mock_fb.record_daily_analytics.assert_called_once()
                data = mock_fb.record_daily_analytics.call_args[0][0]
                self.assertEqual(data["books_generated"], 1)
                self.assertEqual(data["failures"], 0)
                self.assertEqual(data["themes"], {"animals": 1})

        asyncio.get_event_loop().run_until_complete(run())

    def test_record_analytics_failure(self):
        from app.routers.books import _record_analytics
        from app.models.book import BookRequest

        request = BookRequest(
            title="Test Book",
            theme="space",
            age_range="6-9",
            page_count=6,
        )

        async def run():
            with patch("app.routers.books.firebase") as mock_fb:
                mock_fb.record_daily_analytics = AsyncMock()
                await _record_analytics(request, "free", None, 0.0, failed=True)
                mock_fb.record_daily_analytics.assert_called_once()
                data = mock_fb.record_daily_analytics.call_args[0][0]
                self.assertEqual(data["books_generated"], 0)
                self.assertEqual(data["failures"], 1)

        asyncio.get_event_loop().run_until_complete(run())

    def test_record_analytics_never_raises(self):
        from app.routers.books import _record_analytics
        from app.models.book import BookRequest

        request = BookRequest(
            title="Test Book",
            theme="animals",
            age_range="6-9",
            page_count=6,
        )

        async def run():
            with patch("app.routers.books.firebase") as mock_fb:
                mock_fb.record_daily_analytics = AsyncMock(side_effect=RuntimeError("DB down"))
                # Should NOT raise
                await _record_analytics(request, "free", None, 0.0, failed=True)

        asyncio.get_event_loop().run_until_complete(run())


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running admin & analytics tests...\n")
    passed = 0
    failures = 0

    for cls in [TestAdminAuth, TestAdminStatsShape, TestDailyAnalytics,
                TestFailureRecording, TestAnalyticsHelper]:
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
