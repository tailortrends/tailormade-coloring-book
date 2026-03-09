"""
Tiered generation gate with lifetime free limit, one-time credits,
and monthly subscription checks via Firestore transactions.

Tiers: free | single | family | teacher
Free = 1 book LIFETIME (not monthly).
"""

from firebase_admin import firestore
from fastapi import HTTPException
from datetime import datetime, timezone
from dataclasses import dataclass
from app.config import get_settings
import structlog

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class GenerationPermit:
    """Returned by check_rate_limit on success."""
    max_pages: int
    tier: str
    used_credit: bool = False  # True if a one-time credit was consumed


async def check_rate_limit(uid: str, tier: str) -> GenerationPermit:
    """
    Check whether the user may generate a book.
    Returns a GenerationPermit with the max_pages allowed.
    Raises 429 if blocked.

    Tier precedence:
      1. teacher (subscription)
      2. family  (subscription)
      3. single  (one-time credit)
      4. free    (lifetime limit)
    """
    import asyncio

    db = firestore.client()
    user_ref = db.collection("users").document(uid)

    @firestore.transactional
    def gate_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        now = datetime.now(timezone.utc)

        if snapshot.exists:
            data = snapshot.to_dict()
        else:
            # Brand-new user — initialise defaults
            data = {
                "subscription_tier": "free",
                "books_generated_total": 0,
                "books_generated_this_month": 0,
                "one_time_credits": 0,
                "subscription_active": False,
                "month_reset": now.strftime("%Y-%m"),
            }
            transaction.set(ref, data)

        sub_tier = data.get("subscription_tier", "free")
        active = data.get("subscription_active", False)
        total = data.get("books_generated_total", 0)
        monthly = data.get("books_generated_this_month", 0)
        credits = data.get("one_time_credits", 0)

        # Monthly counter reset
        month_key = now.strftime("%Y-%m")
        if data.get("month_reset") != month_key:
            monthly = 0
            transaction.update(ref, {
                "books_generated_this_month": 0,
                "month_reset": month_key,
            })

        # 1. TEACHER
        if sub_tier == "teacher" and active:
            if monthly < settings.teacher_monthly_limit:
                return GenerationPermit(
                    max_pages=settings.teacher_max_pages, tier="teacher"
                )

        # 2. FAMILY
        if sub_tier == "family" and active:
            if monthly < settings.family_monthly_limit:
                return GenerationPermit(
                    max_pages=settings.family_max_pages, tier="family"
                )

        # 3. SINGLE CREDIT (available regardless of sub_tier)
        if credits > 0:
            transaction.update(ref, {
                "one_time_credits": credits - 1,
            })
            return GenerationPermit(
                max_pages=settings.single_max_pages,
                tier="single",
                used_credit=True,
            )

        # 4. FREE TIER — LIFETIME CHECK
        if total < settings.free_lifetime_limit:
            return GenerationPermit(
                max_pages=settings.free_max_pages, tier="free"
            )

        # 5. BLOCKED — build quota info for the frontend
        if sub_tier in ("teacher", "family") and active:
            # Subscription user who exhausted monthly allowance
            limit_val = (
                settings.teacher_monthly_limit if sub_tier == "teacher"
                else settings.family_monthly_limit
            )
            used_val = monthly
            # Reset is first of next month
            if now.month == 12:
                reset = now.replace(year=now.year + 1, month=1, day=1,
                                    hour=0, minute=0, second=0, microsecond=0)
            else:
                reset = now.replace(month=now.month + 1, day=1,
                                    hour=0, minute=0, second=0, microsecond=0)
        else:
            # Free tier — lifetime limit
            limit_val = settings.free_lifetime_limit
            used_val = total
            reset = None

        raise HTTPException(
            status_code=429,
            detail={
                "message": (
                    "You've used your free book! Upgrade to create more "
                    "personalized books for your little artist."
                ),
                "quota": {
                    "used": used_val,
                    "limit": limit_val,
                    "remaining": max(0, limit_val - used_val),
                    "reset_date": reset.isoformat() if reset else None,
                    "tier": sub_tier,
                    "is_subscription_active": active,
                },
            },
        )

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    permit = await loop.run_in_executor(
        None, gate_transaction, transaction, user_ref
    )
    logger.info("rate_limit_check_passed", uid=uid, tier=permit.tier,
                max_pages=permit.max_pages,
                used_credit=permit.used_credit)
    return permit


async def increment_usage(uid: str) -> None:
    """
    Called ONLY after successful book generation.
    Increments both lifetime total and monthly counter atomically.
    """
    import asyncio

    db = firestore.client()
    user_ref = db.collection("users").document(uid)

    @firestore.transactional
    def increment_in_transaction(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if snapshot.exists:
            data = snapshot.to_dict()
            transaction.update(ref, {
                "books_generated_total": data.get("books_generated_total", 0) + 1,
                "books_generated_this_month": data.get("books_generated_this_month", 0) + 1,
            })
        else:
            transaction.set(ref, {
                "subscription_tier": "free",
                "books_generated_total": 1,
                "books_generated_this_month": 1,
                "one_time_credits": 0,
                "subscription_active": False,
                "month_reset": datetime.now(timezone.utc).strftime("%Y-%m"),
            })

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, increment_in_transaction, transaction, user_ref)
    logger.info("usage_incremented", uid=uid)
