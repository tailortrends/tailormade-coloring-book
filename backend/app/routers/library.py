from fastapi import APIRouter, Query
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/library", tags=["library"])


@router.get("/index")
async def get_library_index(
    theme: str | None = Query(default=None),
    age_range: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Public gallery stub — full library coming after LoRA batch generation."""
    return {
        "themes": [
            "ocean", "space", "dinosaur",
            "fantasy", "animals",
            "vehicles", "nature",
        ],
        "images": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "message": "Library coming soon",
    }
