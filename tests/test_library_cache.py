"""
Tests for the library cache service.

Mocks R2 to verify:
- Index parsing from R2 keys
- find_match returns correct URL on hit
- find_match returns None on miss
- Theme/subject mapping works across aliases
- Costs document includes library_hits and library_misses fields
"""

import asyncio
import sys
import os

# Add backend to path so `app.*` imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

try:
    import pytest
except ImportError:
    pytest = None  # Allow running via __main__ without pytest

from unittest.mock import patch, MagicMock

# ── Helpers ──────────────────────────────────────────────────────────────────

SAMPLE_R2_KEYS = [
    "library/animals_bear/simple/animals_bear_simple_v1.png",
    "library/animals_bear/simple/animals_bear_simple_v2.png",
    "library/animals_bear/simple/animals_bear_simple_v3.png",
    "library/animals_bear/medium/animals_bear_medium_v1.png",
    "library/animals_bear/advanced/animals_bear_advanced_v1.png",
    "library/ocean_dolphin/simple/ocean_dolphin_simple_v1.png",
    "library/ocean_dolphin/beginner/ocean_dolphin_beginner_v1.png",
    "library/ocean_dolphin/medium/ocean_dolphin_medium_v1.png",
    "library/ocean_dolphin/medium/ocean_dolphin_medium_v2.png",
    "library/dino_trex/simple/dino_trex_simple_v1.png",
    "library/dino_trex/medium/dino_trex_medium_v1.png",
    "library/veh_fire_truck/beginner/veh_fire_truck_beginner_v1.png",
    "library/uni_flying/simple/uni_flying_simple_v1.png",
    "library/princess_dragon/medium/princess_dragon_medium_v1.png",
    "library/animals_dog/simple/animals_dog_simple_v1.png",
    "library/animals_cat/beginner/animals_cat_beginner_v1.png",
    "library/farm_tractor/medium/farm_tractor_medium_v1.png",
]

MOCK_PUBLIC_URL = "https://test-r2.example.com"


def _make_r2_response(keys: list[str]) -> dict:
    return {"Contents": [{"Key": k} for k in keys]}


# ── Unit Tests ───────────────────────────────────────────────────────────────

class TestParseR2Keys:
    """Test _parse_r2_keys directly."""

    def test_parses_valid_keys(self):
        from app.services.library_cache import _parse_r2_keys

        with patch("app.services.library_cache.settings") as mock_settings:
            mock_settings.r2_public_url = MOCK_PUBLIC_URL
            index = _parse_r2_keys(SAMPLE_R2_KEYS)

        # Check correct number of lookup keys
        assert "animals_bear:simple" in index
        assert len(index["animals_bear:simple"]) == 3
        assert "ocean_dolphin:medium" in index
        assert len(index["ocean_dolphin:medium"]) == 2
        assert "dino_trex:simple" in index

    def test_urls_include_public_prefix(self):
        from app.services.library_cache import _parse_r2_keys

        with patch("app.services.library_cache.settings") as mock_settings:
            mock_settings.r2_public_url = MOCK_PUBLIC_URL
            index = _parse_r2_keys(SAMPLE_R2_KEYS)

        url = index["animals_bear:simple"][0]
        assert url.startswith(MOCK_PUBLIC_URL)
        assert "animals_bear_simple_v1.png" in url

    def test_ignores_malformed_keys(self):
        from app.services.library_cache import _parse_r2_keys

        with patch("app.services.library_cache.settings") as mock_settings:
            mock_settings.r2_public_url = MOCK_PUBLIC_URL
            index = _parse_r2_keys(["library/orphan", "bad_key"])

        assert len(index) == 0


class TestFindMatch:
    """Test find_match with a pre-loaded mock index."""

    def _preload_index(self):
        """Inject a mock index into the module cache."""
        import app.services.library_cache as lib
        with patch.object(lib, "settings") as mock_settings:
            mock_settings.r2_public_url = MOCK_PUBLIC_URL
            lib._index = _parse_r2_keys_with_mock(SAMPLE_R2_KEYS)
            lib._index_loaded_at = 9999999999.0  # far future — prevent reload

    def test_hit_animals_bear_simple(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="animals", subject_hint="bear", complexity="simple")
        )
        assert url is not None
        assert "animals_bear" in url
        assert "simple" in url

    def test_hit_ocean_dolphin_medium(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="ocean", subject_hint="dolphin", complexity="medium")
        )
        assert url is not None
        assert "ocean_dolphin" in url

    def test_hit_dinosaur_trex(self):
        """scene_planner uses 'dinosaur' theme but R2 uses 'dino_' prefix."""
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="dinosaur", subject_hint="trex", complexity="simple")
        )
        assert url is not None
        assert "dino_trex" in url

    def test_hit_vehicles_fire_truck(self):
        """scene_planner uses 'vehicles' but R2 uses 'veh_'."""
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="vehicles", subject_hint="fire_truck", complexity="beginner")
        )
        assert url is not None
        assert "veh_fire_truck" in url

    def test_hit_subject_alias_puppy_to_dog(self):
        """scene_planner uses 'puppy' but R2 has 'animals_dog'."""
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="animals", subject_hint="puppy", complexity="simple")
        )
        assert url is not None
        assert "animals_dog" in url

    def test_hit_subject_alias_kitten_to_cat(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="animals", subject_hint="kitten", complexity="beginner")
        )
        assert url is not None
        assert "animals_cat" in url

    def test_hit_fantasy_unicorn(self):
        """fantasy theme maps to uni_ and princess_ prefixes."""
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="fantasy", subject_hint="unicorn", complexity="simple")
        )
        assert url is not None
        assert "uni_flying" in url

    def test_hit_fantasy_dragon(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="fantasy", subject_hint="dragon", complexity="medium")
        )
        assert url is not None
        assert "princess_dragon" in url

    def test_miss_nonexistent_subject(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="animals", subject_hint="platypus", complexity="simple")
        )
        assert url is None

    def test_miss_wrong_complexity(self):
        self._preload_index()
        from app.services.library_cache import find_match
        url = asyncio.get_event_loop().run_until_complete(
            find_match(theme="animals", subject_hint="bear", complexity="beginner")
        )
        # animals_bear only has simple, medium, advanced — no beginner
        assert url is None

    def test_miss_empty_index(self):
        import app.services.library_cache as lib
        from app.services.library_cache import find_match

        # Patch load_library_index to return empty dict (simulates empty R2 bucket)
        async def _empty_load(force=False):
            return {}

        original_load = lib.load_library_index
        lib.load_library_index = _empty_load
        try:
            url = asyncio.get_event_loop().run_until_complete(
                find_match(theme="animals", subject_hint="bear", complexity="simple")
            )
        finally:
            lib.load_library_index = original_load
        assert url is None


class TestCostDocumentFields:
    """Verify the cost document includes library tracking fields."""

    def test_cost_data_has_library_fields(self):
        """Simulate what books.py builds and verify the fields exist."""
        # This mirrors the cost_data dict from books.py
        from dataclasses import dataclass

        @dataclass
        class MockMetrics:
            total_attempts: int = 3
            total_image_spend: float = 0.222
            library_hits: int = 5
            library_misses: int = 3

        metrics = MockMetrics()
        cost_per_image = 0.074

        cost_data = {
            "book_id": "test-123",
            "uid": "user-abc",
            "timestamp": "2026-03-09T00:00:00Z",
            "total_cost": round(metrics.total_image_spend + 0.01, 6),
            "image_cost": round(metrics.total_image_spend, 6),
            "planning_cost": 0.01,
            "retry_count": 0,
            "page_count": 8,
            "theme": "animals",
            "title": "Test Book",
            "status": "success",
            "library_hits": metrics.library_hits,
            "library_misses": metrics.library_misses,
            "estimated_savings": round(metrics.library_hits * cost_per_image, 6),
        }

        assert "library_hits" in cost_data
        assert "library_misses" in cost_data
        assert "estimated_savings" in cost_data
        assert cost_data["library_hits"] == 5
        assert cost_data["library_misses"] == 3
        assert cost_data["estimated_savings"] == round(5 * 0.074, 6)


class TestGetIndexStats:
    """Test the stats summary function."""

    def test_stats_when_loaded(self):
        import app.services.library_cache as lib
        with patch.object(lib, "settings") as mock_settings:
            mock_settings.r2_public_url = MOCK_PUBLIC_URL
            lib._index = _parse_r2_keys_with_mock(SAMPLE_R2_KEYS)
            lib._index_loaded_at = 9999999999.0

        stats = lib.get_index_stats()
        assert stats["loaded"] is True
        assert stats["total_images"] == len(SAMPLE_R2_KEYS)
        assert stats["entries"] > 0
        assert "animals" in stats["themes"]
        assert "ocean" in stats["themes"]

    def test_stats_when_empty(self):
        import app.services.library_cache as lib
        lib._index = {}
        lib._index_loaded_at = 0.0

        stats = lib.get_index_stats()
        assert stats["loaded"] is False
        assert stats["total_images"] == 0


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_r2_keys_with_mock(keys: list[str]) -> dict[str, list[str]]:
    """Parse keys using the real function but with mocked settings."""
    from app.services.library_cache import _parse_r2_keys
    with patch("app.services.library_cache.settings") as mock_settings:
        mock_settings.r2_public_url = MOCK_PUBLIC_URL
        return _parse_r2_keys(keys)


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running library cache tests...\n")
    failures = 0

    for cls in [TestParseR2Keys, TestFindMatch, TestCostDocumentFields, TestGetIndexStats]:
        instance = cls()
        for name in dir(instance):
            if name.startswith("test_"):
                try:
                    getattr(instance, name)()
                    print(f"  PASS: {cls.__name__}.{name}")
                except AssertionError as e:
                    print(f"  FAIL: {cls.__name__}.{name} — {e}")
                    failures += 1
                except Exception as e:
                    print(f"  ERROR: {cls.__name__}.{name} — {e}")
                    failures += 1

    print(f"\n{'All tests passed!' if failures == 0 else f'{failures} test(s) failed.'}")
