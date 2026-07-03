"""
Account deletion: a real cascading delete that removes ALL of the caller's data
before the Firebase Auth record is removed.

Ordering is deliberate and gated: Stripe subscription is canceled first (so a
deleted account never keeps billing), then every book/character/profile and its
R2 assets, then the users/{uid} document, and ONLY if all of that succeeds is the
Auth record deleted. Any failure before that final step leaves the login intact
so the user can retry rather than being locked out with orphaned data behind them.
The cascade is idempotent, so a retry after a partial failure is safe.
"""

import asyncio
import stripe
import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user
from app.services import firebase, storage

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/account", tags=["account"])


async def _cancel_active_subscription(uid: str) -> None:
    """Cancel the user's Stripe subscription, if one exists, before deletion.

    An 'already canceled / not found' Stripe error is treated as success; any
    other Stripe/transport error propagates so the caller aborts the deletion
    (we must never delete an account that keeps getting billed).
    """
    info = await firebase.get_user_stripe_info(uid) or {}
    subscription_id = info.get("stripe_subscription_id")
    if not subscription_id:
        return

    from app.routers.stripe_router import _get_stripe
    s = _get_stripe()
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: s.Subscription.cancel(subscription_id))
        logger.info("account_deletion_subscription_canceled", uid=uid)
    except stripe.InvalidRequestError:
        # Subscription already canceled or no longer exists — safe to proceed.
        logger.info("account_deletion_subscription_absent", uid=uid)


@router.delete("", status_code=200)
@router.delete("/", status_code=200)
async def delete_account(user: dict = Depends(get_current_user)):
    """Permanently delete the authenticated user's account and all their data."""
    uid = user["uid"]
    logger.info("account_deletion_started", uid=uid)

    try:
        # 0. Stop billing first.
        await _cancel_active_subscription(uid)

        # 1. Books + their R2-stored images/PDFs. R2 failures are fatal here
        #    (unlike the per-book endpoint) so we never delete the account while
        #    generated files still linger.
        books = await firebase.get_user_books(uid, limit=1000)
        for book in books:
            book_id = book.get("book_id")
            if not book_id:
                continue
            await storage.delete_book_assets(book_id)
            await firebase.delete_book(book_id)

        # 2. Characters + their R2 assets.
        characters = await firebase.get_user_characters(uid, limit=1000)
        for char in characters:
            character_id = char.get("character_id")
            if not character_id:
                continue
            await storage.delete_character_assets(character_id)
            await firebase.delete_character(character_id)

        # 3. Child profiles.
        profiles = await firebase.get_user_profiles(uid)
        for profile in profiles:
            profile_id = profile.get("profile_id")
            if profile_id:
                await firebase.delete_profile(profile_id)

        # 4. The users/{uid} document itself (Admin SDK bypasses client rules).
        await firebase.delete_user_document(uid)

    except Exception as e:
        # ANY failure above means data may still exist. Do NOT delete the Auth
        # record — keep the user's access so they (or support) can retry, rather
        # than locking them out with orphaned data they can no longer reach.
        logger.error("account_deletion_failed_before_auth", uid=uid, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=(
                "Account deletion could not be completed and your login is "
                "unchanged. Please try again."
            ),
        )

    # 5. All data is confirmed removed — now, and only now, delete the Auth record.
    try:
        await firebase.delete_auth_user(uid)
    except Exception as e:
        logger.error("account_deletion_auth_delete_failed", uid=uid, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=(
                "Your data was removed but finalizing account closure failed. "
                "Please contact support."
            ),
        )

    logger.info("account_deletion_complete", uid=uid)
    return {"status": "deleted"}
