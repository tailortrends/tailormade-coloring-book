import asyncio
from firebase_admin import firestore
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger()


async def save_book(book_id: str, data: dict) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("books").document(book_id).set(data)
    )
    logger.info("book_saved", book_id=book_id)


async def get_book(book_id: str) -> dict | None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None, lambda: db.collection("books").document(book_id).get()
    )
    return doc.to_dict() if doc.exists else None


async def get_user_books(uid: str, limit: int = 20) -> list[dict]:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(
        None,
        lambda: list(
            db.collection("books")
            .where("uid", "==", uid)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ),
    )
    return [doc.to_dict() for doc in docs]


async def delete_book(book_id: str) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("books").document(book_id).delete()
    )
    logger.info("book_deleted", book_id=book_id)


async def record_generation_cost(cost_data: dict) -> None:
    """Write a cost record to the 'costs' collection for margin tracking."""
    db = firestore.client()
    loop = asyncio.get_event_loop()
    doc_id = cost_data.get("book_id", "unknown")
    await loop.run_in_executor(
        None, lambda: db.collection("costs").document(doc_id).set(cost_data)
    )
    logger.info("cost_recorded", book_id=doc_id, total_cost=cost_data.get("total_cost"))


async def get_library_images(
    theme: str | None = None,
    age_range: str | None = None,
    complexity: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Fetch public library images with optional filtering."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _query():
        ref = db.collection("library_images")
        if theme:
            ref = ref.where("theme", "==", theme)
        if age_range:
            ref = ref.where("age_range", "==", age_range)
        if complexity:
            ref = ref.where("complexity", "==", complexity)
        ref = ref.order_by("clip_score", direction=firestore.Query.DESCENDING)
        ref = ref.offset(offset).limit(limit)
        return [doc.to_dict() | {"image_id": doc.id} for doc in ref.stream()]

    return await loop.run_in_executor(None, _query)


async def get_library_themes() -> list[str]:
    """Return distinct themes present in the library_images collection."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _query():
        docs = db.collection("library_images").select(["theme"]).stream()
        return sorted({doc.to_dict().get("theme", "") for doc in docs} - {""})

    return await loop.run_in_executor(None, _query)


async def get_all_costs(limit: int = 500) -> list[dict]:
    """Retrieve cost records for admin dashboard."""
    db = firestore.client()
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(
        None,
        lambda: list(
            db.collection("costs")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ),
    )
    return [doc.to_dict() for doc in docs]

async def save_character(character_id: str, data: dict) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("characters").document(character_id).set(data)
    )
    logger.info("character_saved", character_id=character_id)

async def get_user_characters(uid: str, limit: int = 50) -> list[dict]:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(
        None,
        lambda: list(
            db.collection("characters")
            .where("uid", "==", uid)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ),
    )
    return [doc.to_dict() for doc in docs]

async def delete_character(character_id: str) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("characters").document(character_id).delete()
    )
    logger.info("character_deleted", character_id=character_id)


# ── Profiles ──────────────────────────────────────────────────────────────────

async def save_profile(profile_id: str, data: dict) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("profiles").document(profile_id).set(data)
    )
    logger.info("profile_saved", profile_id=profile_id)


async def get_profile(profile_id: str) -> dict | None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None, lambda: db.collection("profiles").document(profile_id).get()
    )
    if not doc.exists:
        return None
    return doc.to_dict() | {"profile_id": doc.id}


async def get_user_profiles(uid: str) -> list[dict]:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(
        None,
        lambda: list(
            db.collection("profiles")
            .where("uid", "==", uid)
            .order_by("created_at", direction=firestore.Query.ASCENDING)
            .stream()
        ),
    )
    return [doc.to_dict() | {"profile_id": doc.id} for doc in docs]


async def update_profile(profile_id: str, data: dict) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("profiles").document(profile_id).update(data)
    )
    logger.info("profile_updated", profile_id=profile_id)


async def delete_profile(profile_id: str) -> None:
    db = firestore.client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, lambda: db.collection("profiles").document(profile_id).delete()
    )
    logger.info("profile_deleted", profile_id=profile_id)


async def clear_default_profiles(uid: str) -> None:
    """Set is_default=False on all profiles for a user."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _clear():
        batch = db.batch()
        docs = (
            db.collection("profiles")
            .where("uid", "==", uid)
            .where("is_default", "==", True)
            .stream()
        )
        for doc in docs:
            batch.update(doc.reference, {"is_default": False})
        batch.commit()

    await loop.run_in_executor(None, _clear)


# ── Analytics ────────────────────────────────────────────────────────────────

async def record_daily_analytics(data: dict) -> None:
    """
    Increment daily analytics counters in analytics/daily/{YYYY-MM-DD}.
    Uses merge + Increment to safely handle concurrent writes.
    """
    from google.cloud.firestore_v1 import Increment

    db = firestore.client()
    loop = asyncio.get_event_loop()
    date_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _write():
        ref = db.collection("analytics").document("daily").collection("days").document(date_key)
        update = {}
        for field in ("books_generated", "pages_generated", "library_hits",
                      "library_misses", "total_cost", "failures"):
            if field in data:
                update[field] = Increment(data[field])
        # Nested maps: themes and tiers
        for map_field in ("themes", "tiers"):
            if map_field in data and isinstance(data[map_field], dict):
                for k, v in data[map_field].items():
                    update[f"{map_field}.{k}"] = Increment(v)
        if update:
            ref.set(update, merge=True)

    await loop.run_in_executor(None, _write)
    logger.info("daily_analytics_recorded", date=date_key)


async def get_daily_analytics(days: int = 30) -> list[dict]:
    """Return the last N days of analytics docs."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _query():
        ref = (
            db.collection("analytics").document("daily").collection("days")
            .order_by("__name__", direction=firestore.Query.DESCENDING)
            .limit(days)
        )
        results = []
        for doc in ref.stream():
            d = doc.to_dict()
            d["date"] = doc.id
            results.append(d)
        return results

    return await loop.run_in_executor(None, _query)


async def get_failed_books(limit: int = 20) -> list[dict]:
    """Return the most recent failed book generation records."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _query():
        return [
            doc.to_dict() | {"book_id": doc.id}
            for doc in db.collection("books")
            .where("status", "==", "failed")
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ]

    return await loop.run_in_executor(None, _query)


async def get_books_by_cost(limit: int = 50) -> list[dict]:
    """Return most expensive books by total_cost descending."""
    db = firestore.client()
    loop = asyncio.get_event_loop()

    def _query():
        return [
            doc.to_dict()
            for doc in db.collection("costs")
            .order_by("total_cost", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        ]

    return await loop.run_in_executor(None, _query)
