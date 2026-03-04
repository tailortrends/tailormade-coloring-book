"""
FIX 2: Race-condition-safe rate limiting via Firestore transactions.

The read-check-increment is a single Firestore transaction.
- check_rate_limit(): transactional read-only check at request start
- increment_usage(): transactional increment ONLY after successful generation
"""

from firebase_admin import firestore
from fastapi import HTTPException
from datetime import datetime, timezone
from app.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()

TIER_LIMITS = {
    "free": settings.free_tier_monthly_limit,
    "pro": settings.pro_tier_monthly_limit,
    "family": settings.family_tier_monthly_limit,
}


def _get_limit_for_tier(tier: str) -> int:
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])


async def check_rate_limit(uid: str, tier: str) -> None:
    """
    FIX 2: Check rate limit using a Firestore transaction.
    This ONLY checks — does NOT increment.
    Increment happens in increment_usage() after successful generation.
    """
    import asyncio

    db = firestore.client()
    usage_ref = db.collection("users").document(uid).collection("usage").document("current")

    @firestore.transactional
    def check_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        now = datetime.now(timezone.utc)

        if snapshot.exists:
            data = snapshot.to_dict()
            last_reset = data.get("last_reset")
            count = data.get("books_generated", 0)

            # Reset monthly counter if it's a new month
            if last_reset and last_reset.month != now.month:
                transaction.set(ref, {
                    "books_generated": 0,
                    "last_reset": now,
                })
                count = 0
        else:
            count = 0
            transaction.set(ref, {
                "books_generated": 0,
                "last_reset": now,
            })

        limit = _get_limit_for_tier(tier)
        if count >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Monthly limit of {limit} book(s) reached. Upgrade to generate more.",
            )

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, check_in_transaction, transaction, usage_ref)
    logger.info("rate_limit_check_passed", uid=uid, tier=tier)


async def increment_usage(uid: str) -> None:
    """
    FIX 2: Called ONLY after successful book generation.
    Uses a transaction to safely increment the counter.
    """
    import asyncio

    db = firestore.client()
    usage_ref = db.collection("users").document(uid).collection("usage").document("current")

    @firestore.transactional
    def increment_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        current = snapshot.to_dict().get("books_generated", 0) if snapshot.exists else 0
        transaction.update(ref, {"books_generated": current + 1})

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, increment_in_transaction, transaction, usage_ref)
    logger.info("usage_incremented", uid=uid)
