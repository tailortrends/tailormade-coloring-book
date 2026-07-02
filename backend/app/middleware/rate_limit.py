"""
Tiered generation gate with lifetime free limit, one-time credits,
and monthly subscription checks via Firestore transactions.

Tiers: free | single | family | teacher
Free = 1 book LIFETIME (not monthly).
"""

import asyncio
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
    reservation_kind: str = "free"


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
    db = firestore.client()
    user_ref = db.collection("users").document(uid)
    usage_ref = db.collection("usage").document(uid)

    @firestore.transactional
    def gate_transaction(transaction, user_document, usage_document):
        user_snapshot = user_document.get(transaction=transaction)
        usage_snapshot = usage_document.get(transaction=transaction)
        now = datetime.now(timezone.utc)
        month_key = now.strftime("%Y-%m")
        day_key = now.strftime("%Y-%m-%d")

        if user_snapshot.exists:
            data = user_snapshot.to_dict()
        else:
            # Brand-new user — initialise defaults
            data = {
                "subscription_tier": "free",
                "books_generated_total": 0,
                "books_generated_this_month": 0,
                "one_time_credits": 0,
                "subscription_active": False,
                "month_reset": month_key,
            }

        usage = usage_snapshot.to_dict() if usage_snapshot.exists else {}

        sub_tier = data.get("subscription_tier", "free")
        active = data.get("subscription_active", False)
        total = data.get("books_generated_total", 0)
        credits = data.get("one_time_credits", 0)

        # Monthly counter reset
        if data.get("month_reset") != month_key:
            user_monthly = 0
            transaction.set(user_document, {
                "books_generated_this_month": 0,
                "month_reset": month_key,
            }, merge=True)
        else:
            user_monthly = data.get("books_generated_this_month", 0)

        reserved_monthly = (
            usage.get("monthly_count", 0)
            if usage.get("month_key") == month_key
            else 0
        )
        monthly = max(user_monthly, reserved_monthly)
        daily_count = (
            usage.get("daily_count", 0)
            if usage.get("daily_date") == day_key
            else 0
        )
        free_count = max(usage.get("free_count", 0), total)
        single_reserved = usage.get("single_reserved", 0)

        if not user_snapshot.exists:
            transaction.set(user_document, data, merge=True)

        def reserve(kind: str, permit_tier: str, max_pages: int, used_credit: bool = False) -> GenerationPermit:
            update = {
                "daily_date": day_key,
                "daily_count": daily_count + 1,
                "month_key": month_key,
                "updated_at": now,
            }
            if kind in ("family", "teacher"):
                update["monthly_count"] = monthly + 1
            elif kind == "single":
                update["single_reserved"] = single_reserved + 1
            elif kind == "free":
                update["free_count"] = free_count + 1
            transaction.set(usage_document, update, merge=True)
            return GenerationPermit(
                max_pages=max_pages,
                tier=permit_tier,
                used_credit=used_credit,
                reservation_kind=kind,
            )

        # 1. TEACHER
        if sub_tier == "teacher" and active:
            if monthly < settings.teacher_monthly_limit:
                return reserve(
                    "teacher",
                    "teacher",
                    settings.teacher_max_pages,
                )

        # 2. FAMILY
        if sub_tier == "family" and active:
            if monthly < settings.family_monthly_limit:
                return reserve(
                    "family",
                    "family",
                    settings.family_max_pages,
                )

        # 3. SINGLE CREDIT (available regardless of sub_tier).
        # The paid credit is reserved here and consumed only after success.
        if credits - single_reserved > 0:
            return reserve(
                "single",
                "single",
                settings.single_max_pages,
                used_credit=True,
            )

        # 4. FREE TIER — LIFETIME CHECK
        if free_count < settings.free_lifetime_limit:
            return reserve(
                "free",
                "free",
                settings.free_max_pages,
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
            used_val = free_count
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
        None, gate_transaction, transaction, user_ref, usage_ref
    )
    logger.info("rate_limit_check_passed", uid=uid, tier=permit.tier,
                max_pages=permit.max_pages,
                used_credit=permit.used_credit)
    return permit


async def reserve_daily_generation(uid: str) -> None:
    """Atomically reserve one slot against the per-user/day generation ceiling.

    Shared cost circuit-breaker for any paid fal.ai generation (book pages and
    character sketches), independent of tier quota. Raises 429 when the ceiling
    is reached. Pair every successful reservation-consuming path with a call to
    release_daily_generation on failure so a failed generation doesn't burn the
    day's ceiling.
    """
    db = firestore.client()
    usage_ref = db.collection("usage").document(uid)

    @firestore.transactional
    def _reserve(transaction, usage_document):
        snapshot = usage_document.get(transaction=transaction)
        usage = snapshot.to_dict() if snapshot.exists else {}
        now = datetime.now(timezone.utc)
        day_key = now.strftime("%Y-%m-%d")
        daily = usage.get("daily_count", 0) if usage.get("daily_date") == day_key else 0

        if daily >= settings.daily_generation_ceiling:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": (
                        "You've hit today's generation limit. "
                        "Please try again tomorrow."
                    ),
                    "quota": {
                        "used": daily,
                        "limit": settings.daily_generation_ceiling,
                        "remaining": 0,
                    },
                },
            )

        transaction.set(usage_document, {
            "daily_date": day_key,
            "daily_count": daily + 1,
            "updated_at": now,
        }, merge=True)

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, _reserve, transaction, usage_ref)


async def release_daily_generation(uid: str) -> None:
    """Return a daily-ceiling slot after a failed generation."""
    db = firestore.client()
    usage_ref = db.collection("usage").document(uid)

    @firestore.transactional
    def _rollback(transaction, usage_document):
        snapshot = usage_document.get(transaction=transaction)
        if not snapshot.exists:
            return
        usage = snapshot.to_dict()
        transaction.set(usage_document, {
            "daily_count": max(0, usage.get("daily_count", 0) - 1),
            "updated_at": datetime.now(timezone.utc),
        }, merge=True)

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, _rollback, transaction, usage_ref)


async def increment_usage(uid: str, permit: GenerationPermit | None = None) -> None:
    """
    Called ONLY after successful book generation.
    Finalizes reserved quota and increments user-facing counters atomically.
    """
    db = firestore.client()
    user_ref = db.collection("users").document(uid)
    usage_ref = db.collection("usage").document(uid)

    @firestore.transactional
    def increment_in_transaction(transaction, user_document, usage_document):
        user_snapshot = user_document.get(transaction=transaction)
        usage_snapshot = usage_document.get(transaction=transaction)
        usage = usage_snapshot.to_dict() if usage_snapshot.exists else {}
        now = datetime.now(timezone.utc)

        if user_snapshot.exists:
            data = user_snapshot.to_dict()
            update = {
                "books_generated_total": data.get("books_generated_total", 0) + 1,
                "books_generated_this_month": data.get("books_generated_this_month", 0) + 1,
                "month_reset": now.strftime("%Y-%m"),
                "last_generation_at": now,
            }
            if permit and permit.used_credit:
                update["one_time_credits"] = max(0, data.get("one_time_credits", 0) - 1)
            transaction.update(user_document, update)
        else:
            transaction.set(user_document, {
                "subscription_tier": "free",
                "books_generated_total": 1,
                "books_generated_this_month": 1,
                "one_time_credits": 0,
                "subscription_active": False,
                "month_reset": now.strftime("%Y-%m"),
                "last_generation_at": now,
            })

        usage_update = {
            "successful_count": usage.get("successful_count", 0) + 1,
            "last_success_at": now,
        }
        if permit and permit.used_credit:
            usage_update["single_reserved"] = max(0, usage.get("single_reserved", 0) - 1)
        transaction.set(usage_document, usage_update, merge=True)

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(
        None, increment_in_transaction, transaction, user_ref, usage_ref
    )
    logger.info(
        "usage_incremented",
        uid=uid,
        tier=permit.tier if permit else None,
        reservation_kind=permit.reservation_kind if permit else None,
    )


async def release_quota_reservation(uid: str, permit: GenerationPermit) -> None:
    """Return a reserved generation slot after a failed generation."""
    db = firestore.client()
    usage_ref = db.collection("usage").document(uid)

    @firestore.transactional
    def rollback_in_transaction(transaction, usage_document):
        snapshot = usage_document.get(transaction=transaction)
        if not snapshot.exists:
            return

        usage = snapshot.to_dict()
        update = {
            "daily_count": max(0, usage.get("daily_count", 0) - 1),
            "updated_at": datetime.now(timezone.utc),
        }

        if permit.reservation_kind in ("family", "teacher"):
            update["monthly_count"] = max(0, usage.get("monthly_count", 0) - 1)
        elif permit.reservation_kind == "single":
            update["single_reserved"] = max(0, usage.get("single_reserved", 0) - 1)
        elif permit.reservation_kind == "free":
            update["free_count"] = max(0, usage.get("free_count", 0) - 1)

        transaction.set(usage_document, update, merge=True)

    loop = asyncio.get_event_loop()
    transaction = db.transaction()
    await loop.run_in_executor(None, rollback_in_transaction, transaction, usage_ref)
    logger.info(
        "quota_reservation_released",
        uid=uid,
        tier=permit.tier,
        reservation_kind=permit.reservation_kind,
    )
