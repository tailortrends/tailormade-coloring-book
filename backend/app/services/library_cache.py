"""
Library cache: In-memory index of pre-generated coloring book images stored in R2.

Checks the library BEFORE calling fal.ai to avoid redundant generation costs.
Index is built by listing R2 keys under library/ and cached with a 5-minute TTL.
"""

import asyncio
import random
import time
from typing import Optional
import structlog
from app.config import get_settings
from app.services.storage import _get_r2_client

logger = structlog.get_logger()
settings = get_settings()

# ── In-memory cache ──────────────────────────────────────────────────────────

_index: dict[str, list[str]] = {}  # "animals_bear:simple" → [url1, url2, url3]
_index_loaded_at: float = 0.0
_INDEX_TTL_SECONDS: float = 300.0  # 5 minutes

# ── Theme prefix mapping ─────────────────────────────────────────────────────
# scene_planner.THEME_SUBJECTS uses these theme keys, but R2 folders use different prefixes.

THEME_TO_R2_PREFIXES: dict[str, list[str]] = {
    "ocean": ["ocean"],
    "space": ["space"],
    "dinosaur": ["dino"],
    "fantasy": ["uni", "princess"],
    "animals": ["animals"],
    "vehicles": ["veh"],
    "nature": ["farm", "animals"],  # nature subjects overlap with farm and animals
    "farm": ["farm"],
    "unicorns": ["uni"],
    "princesses": ["princess"],
}

# Subject hint aliases: scene_planner subject_hint → R2 subject name
SUBJECT_ALIASES: dict[str, str] = {
    "puppy": "dog",
    "kitten": "cat",
    "sea_turtle": "turtle",
    "space_station": "station",
    "star_cluster": "stars",
    "treasure_chest": "treasure",
    "baby_dinosaur": "baby",
    "brontosaurus": "brachiosaurus",
    "coral_reef": "coral_reef",
    "pirate_ship": "pirate_ship",
    "hot_air_balloon": "hot_air_balloon",
    "fire_truck": "fire_truck",
    "race_car": "race_car",
    "school_bus": "school_bus",
    "monster_truck": "dump_truck",
    "mars_rover": "mars_rover",
    "sunflower": "sunflower_field",
    "unicorn": "flying",  # fantasy theme "unicorn" → uni_flying
    "dragon": "dragon",  # fantasy theme "dragon" → princess_dragon
    "castle": "castle",  # both uni_castle and princess_castle exist
    "princess": "adventure",
    "enchanted_forest": "forest",
    "magic_wand": "magic",
    "fairy": "friends",
}


def _parse_r2_keys(keys: list[str]) -> dict[str, list[str]]:
    """Parse R2 object keys into an index dict.

    Key format: library/{subject_folder}/{tier}/{filename}.png
    Example:    library/animals_bear/simple/animals_bear_simple_v1.png

    Returns dict keyed by "{subject_folder}:{tier}" → list of public URLs.
    """
    index: dict[str, list[str]] = {}
    for key in keys:
        parts = key.split("/")
        if len(parts) < 4:
            continue
        subject_folder = parts[1]  # e.g. "animals_bear"
        tier = parts[2]  # e.g. "simple"
        lookup_key = f"{subject_folder}:{tier}"
        url = f"{settings.r2_public_url}/{key}"
        index.setdefault(lookup_key, []).append(url)
    return index


async def load_library_index(force: bool = False) -> dict[str, list[str]]:
    """Load the library index from R2. Returns cached version if within TTL."""
    global _index, _index_loaded_at

    now = time.monotonic()
    if not force and _index and (now - _index_loaded_at) < _INDEX_TTL_SECONDS:
        return _index

    logger.info("library_index_loading")
    loop = asyncio.get_event_loop()

    def _list_keys() -> list[str]:
        client = _get_r2_client()
        paginator = client.get_paginator("list_objects_v2")
        keys: list[str] = []
        for page in paginator.paginate(Bucket=settings.r2_bucket_name, Prefix="library/"):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    try:
        keys = await loop.run_in_executor(None, _list_keys)
        _index = _parse_r2_keys(keys)
        _index_loaded_at = time.monotonic()
        total_images = sum(len(urls) for urls in _index.values())
        logger.info("library_index_loaded",
                     entries=len(_index),
                     total_images=total_images)
    except Exception as e:
        logger.error("library_index_load_failed", error=str(e))
        # Keep stale index if we had one
        if not _index:
            _index = {}

    return _index


def _resolve_lookup_keys(theme: str, subject_hint: str) -> list[str]:
    """Resolve a (theme, subject_hint) pair into candidate R2 subject folder names.

    Returns a list of possible folder names to try, e.g. ["animals_bear", "ocean_turtle"].
    """
    # Normalize
    theme_lower = theme.lower().strip()
    subject = subject_hint.lower().strip().replace(" ", "_")

    # Apply alias if available
    aliased_subject = SUBJECT_ALIASES.get(subject, subject)

    # Get R2 prefixes for this theme
    prefixes = THEME_TO_R2_PREFIXES.get(theme_lower, [])

    candidates: list[str] = []
    for prefix in prefixes:
        candidates.append(f"{prefix}_{aliased_subject}")
        # Also try the original subject if alias was applied
        if aliased_subject != subject:
            candidates.append(f"{prefix}_{subject}")

    # Fallback: try all known prefixes if theme doesn't match directly
    if not prefixes:
        for prefix_list in THEME_TO_R2_PREFIXES.values():
            for prefix in prefix_list:
                candidates.append(f"{prefix}_{aliased_subject}")

    return candidates


async def find_match(
    theme: str,
    subject_hint: str,
    complexity: str,
) -> Optional[str]:
    """Look up a matching pre-generated image from the library.

    Returns a random URL from all matches (so books don't look identical),
    or None on miss.
    """
    index = await load_library_index()
    if not index:
        logger.debug("library_miss_empty_index", theme=theme, subject=subject_hint)
        return None

    candidates = _resolve_lookup_keys(theme, subject_hint)

    for folder_name in candidates:
        lookup_key = f"{folder_name}:{complexity}"
        urls = index.get(lookup_key)
        if urls:
            chosen = random.choice(urls)
            logger.info("library_hit",
                         theme=theme,
                         subject=subject_hint,
                         complexity=complexity,
                         folder=folder_name,
                         url=chosen)
            return chosen

    logger.info("library_miss",
                 theme=theme,
                 subject=subject_hint,
                 complexity=complexity,
                 tried=candidates[:4])
    return None


def get_index_stats() -> dict:
    """Return summary stats about the current in-memory index."""
    if not _index:
        return {"loaded": False, "entries": 0, "total_images": 0, "themes": []}

    total_images = sum(len(urls) for urls in _index.values())

    # Extract unique theme prefixes
    themes: set[str] = set()
    for key in _index:
        folder = key.split(":")[0]
        # folder is like "animals_bear" → prefix is "animals"
        # But some have underscores in subject, so split on first _
        prefix = folder.split("_")[0]
        themes.add(prefix)

    return {
        "loaded": True,
        "entries": len(_index),
        "total_images": total_images,
        "themes": sorted(themes),
        "ttl_remaining": max(0, _INDEX_TTL_SECONDS - (time.monotonic() - _index_loaded_at)),
    }
