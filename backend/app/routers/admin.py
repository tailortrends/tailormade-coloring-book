from fastapi import APIRouter, Header, HTTPException
import structlog

from app.config import get_settings
from app.services import firebase

logger = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(x_admin_token: str = Header(None)):
    """
    Admin dashboard: aggregated cost metrics from the 'costs' collection.
    Returns average cost per book, total spend, and most expensive prompt.
    Protected by X-Admin-Token header.
    """
    if not x_admin_token or x_admin_token != settings.admin_secret_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    costs = await firebase.get_all_costs(limit=500)

    if not costs:
        return {
            "total_books": 0,
            "avg_cost_per_book": 0.0,
            "total_spend": 0.0,
            "total_image_spend": 0.0,
            "total_planning_spend": 0.0,
            "total_retries": 0,
            "most_expensive_book": None,
        }

    total_spend = sum(c.get("total_cost", 0) for c in costs)
    total_image_spend = sum(c.get("image_cost", 0) for c in costs)
    total_planning_spend = sum(c.get("planning_cost", 0) for c in costs)
    total_retries = sum(c.get("retry_count", 0) for c in costs)
    avg_cost = total_spend / len(costs)

    # Most expensive book (most retries = most wasted spend)
    most_expensive = max(costs, key=lambda c: c.get("total_cost", 0))

    return {
        "total_books": len(costs),
        "avg_cost_per_book": round(avg_cost, 4),
        "total_spend": round(total_spend, 4),
        "total_image_spend": round(total_image_spend, 4),
        "total_planning_spend": round(total_planning_spend, 4),
        "total_retries": total_retries,
        "most_expensive_book": {
            "book_id": most_expensive.get("book_id"),
            "title": most_expensive.get("title"),
            "total_cost": most_expensive.get("total_cost"),
            "retry_count": most_expensive.get("retry_count"),
            "theme": most_expensive.get("theme"),
            "uid": most_expensive.get("uid"),
        },
    }
