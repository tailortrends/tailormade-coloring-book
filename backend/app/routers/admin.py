from fastapi import APIRouter, Depends, Query
from collections import Counter
import structlog

from app.config import get_settings
from app.middleware.auth import get_admin_user
from app.services import firebase

logger = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(user: dict = Depends(get_admin_user)):
    """
    Admin dashboard: aggregated cost metrics from the 'costs' collection.
    Expanded with monthly stats, library hit rate, top themes, and tier breakdown.
    """
    costs = await firebase.get_all_costs(limit=2000)

    if not costs:
        return {
            "total_books": 0,
            "books_this_month": 0,
            "avg_cost_per_book": 0.0,
            "total_spend": 0.0,
            "total_image_spend": 0.0,
            "total_planning_spend": 0.0,
            "total_retries": 0,
            "library_hit_rate": 0.0,
            "top_themes": [],
            "books_by_tier": {},
            "most_expensive_book": None,
        }

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    month_prefix = now.strftime("%Y-%m")

    total_spend = sum(c.get("total_cost", 0) for c in costs)
    total_image_spend = sum(c.get("image_cost", 0) for c in costs)
    total_planning_spend = sum(c.get("planning_cost", 0) for c in costs)
    total_retries = sum(c.get("retry_count", 0) for c in costs)
    avg_cost = total_spend / len(costs)

    # Books this month
    books_this_month = sum(
        1 for c in costs
        if str(c.get("timestamp", "")).startswith(month_prefix)
    )

    # Library hit rate
    total_hits = sum(c.get("library_hits", 0) for c in costs)
    total_misses = sum(c.get("library_misses", 0) for c in costs)
    total_pages = total_hits + total_misses
    library_hit_rate = round((total_hits / total_pages * 100) if total_pages > 0 else 0, 1)

    # Top 5 themes
    theme_counter: Counter = Counter()
    for c in costs:
        theme = c.get("theme")
        if theme:
            theme_counter[theme] += 1
    top_themes = [{"theme": t, "count": n} for t, n in theme_counter.most_common(5)]

    # Books by tier
    tier_counter: Counter = Counter()
    for c in costs:
        # Costs collection doesn't always have tier, fall back to "unknown"
        t = c.get("tier", "unknown")
        tier_counter[t] += 1
    books_by_tier = dict(tier_counter)

    # Most expensive book
    most_expensive = max(costs, key=lambda c: c.get("total_cost", 0))

    return {
        "total_books": len(costs),
        "books_this_month": books_this_month,
        "avg_cost_per_book": round(avg_cost, 4),
        "total_spend": round(total_spend, 4),
        "total_image_spend": round(total_image_spend, 4),
        "total_planning_spend": round(total_planning_spend, 4),
        "total_retries": total_retries,
        "library_hit_rate": library_hit_rate,
        "top_themes": top_themes,
        "books_by_tier": books_by_tier,
        "most_expensive_book": {
            "book_id": most_expensive.get("book_id"),
            "title": most_expensive.get("title"),
            "total_cost": most_expensive.get("total_cost"),
            "retry_count": most_expensive.get("retry_count"),
            "theme": most_expensive.get("theme"),
            "uid": most_expensive.get("uid"),
        },
    }


@router.get("/daily")
async def get_daily(
    days: int = Query(default=30, ge=1, le=90),
    user: dict = Depends(get_admin_user),
):
    """Return the last N days of daily analytics for charting."""
    return await firebase.get_daily_analytics(days)


@router.get("/failures")
async def get_failures(
    limit: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_admin_user),
):
    """Return the most recent failed book generations."""
    return await firebase.get_failed_books(limit)


@router.get("/costs")
async def get_costs(
    limit: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(get_admin_user),
):
    """Return most expensive books sorted by total_cost descending."""
    return await firebase.get_books_by_cost(limit)
