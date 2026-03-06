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


async def record_generation_cost(cost_data: dict) -> None:
    """Write a cost record to the 'costs' collection for margin tracking."""
    db = firestore.client()
    loop = asyncio.get_event_loop()
    doc_id = cost_data.get("book_id", "unknown")
    await loop.run_in_executor(
        None, lambda: db.collection("costs").document(doc_id).set(cost_data)
    )
    logger.info("cost_recorded", book_id=doc_id, total_cost=cost_data.get("total_cost"))


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
