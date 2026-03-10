from fastapi import APIRouter, Query
import structlog

from app.services.library_cache import load_library_index, get_index_stats
from app.services import firebase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/library", tags=["library"])


@router.get("/index")
async def get_library_index(
    theme: str | None = Query(default=None),
    age_range: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Return library index grouped by theme → subject → tier → image count."""
    index = await load_library_index()

    # Build structured summary: theme → { subject → { tier → count } }
    structured: dict[str, dict[str, dict[str, int]]] = {}
    for key, urls in index.items():
        folder, tier = key.split(":", 1)
        # folder is like "animals_bear" — split prefix from subject
        parts = folder.split("_", 1)
        if len(parts) < 2:
            continue
        prefix = parts[0]
        subject = parts[1]
        structured.setdefault(prefix, {}).setdefault(subject, {})[tier] = len(urls)

    # Filter by theme if provided
    if theme:
        theme_lower = theme.lower().strip()
        # Map scene_planner theme names to R2 prefixes
        prefix_map = {
            "ocean": ["ocean"], "space": ["space"], "dinosaur": ["dino"],
            "fantasy": ["uni", "princess"], "animals": ["animals"],
            "vehicles": ["veh"], "nature": ["farm", "animals"],
            "farm": ["farm"], "unicorns": ["uni"], "princesses": ["princess"],
        }
        allowed = set(prefix_map.get(theme_lower, [theme_lower]))
        structured = {k: v for k, v in structured.items() if k in allowed}

    total_images = sum(
        count
        for subjects in structured.values()
        for tiers in subjects.values()
        for count in tiers.values()
    )

    return {
        "themes": sorted(structured.keys()),
        "index": structured,
        "total_images": total_images,
        "total_subjects": sum(len(subjects) for subjects in structured.values()),
    }


@router.get("/stats")
async def get_library_stats():
    """Return library stats including cache status and aggregate hit rate from costs."""
    cache_stats = get_index_stats()

    # Read aggregate hit rate from recent cost documents
    total_hits = 0
    total_misses = 0
    books_with_library = 0
    try:
        costs = await firebase.get_all_costs(limit=200)
        for cost in costs:
            hits = cost.get("library_hits", 0)
            misses = cost.get("library_misses", 0)
            if hits > 0 or misses > 0:
                books_with_library += 1
                total_hits += hits
                total_misses += misses
    except Exception as e:
        logger.warning("library_stats_cost_fetch_failed", error=str(e))

    total_lookups = total_hits + total_misses
    hit_rate = round(total_hits / total_lookups * 100, 1) if total_lookups > 0 else 0.0

    return {
        "cache": cache_stats,
        "aggregate": {
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate_percent": hit_rate,
            "books_with_library_data": books_with_library,
            "estimated_total_savings": round(total_hits * 0.074, 2),
        },
    }
