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
