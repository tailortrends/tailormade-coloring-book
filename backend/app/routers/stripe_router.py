"""
Stripe integration: checkout sessions, customer portal, and webhooks.
Supports admin-togglable live/test mode via Firestore settings.
"""

import asyncio
import stripe
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.middleware.auth import get_current_user
from app.services.firebase import update_user_stripe, get_user_stripe_info

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/api/v1/stripe", tags=["stripe"])

# ── Helpers ──────────────────────────────────────────────────────────────────

PRICE_ID_TO_TIER = {
    price_id: tier
    for price_id, tier in (
        (settings.stripe_family_price_id, "family"),
        (settings.stripe_teacher_price_id, "teacher"),
        (settings.stripe_single_price_id, "single"),
    )
    if price_id
}
ALLOWED_PRICE_IDS = set(PRICE_ID_TO_TIER)


def _get_stripe_mode() -> str:
    """Read stripe mode from Firestore settings (cached per-request), fallback to env."""
    try:
        from firebase_admin import firestore as fs
        db = fs.client()
        doc = db.collection("settings").document("stripe").get()
        if doc.exists:
            mode = doc.to_dict().get("mode")
            if mode in ("test", "live"):
                return mode
    except Exception:
        pass
    return settings.stripe_mode


def _get_stripe_keys() -> tuple[str, str]:
    """Return (secret_key, publishable_key) based on current mode."""
    mode = _get_stripe_mode()
    if mode == "live":
        return settings.stripe_live_secret_key, settings.stripe_live_publishable_key
    return settings.stripe_test_secret_key, settings.stripe_test_publishable_key


def _get_stripe():
    """Configure and return the stripe module with the correct API key."""
    secret_key, _ = _get_stripe_keys()
    if not secret_key:
        mode = _get_stripe_mode()
        logger.error("stripe_no_api_key", mode=mode)
        raise HTTPException(
            status_code=503,
            detail=f"Stripe {mode} secret key is not configured",
        )
    stripe.api_key = secret_key
    return stripe


async def _find_or_create_customer(email: str, uid: str) -> str:
    """Look up existing Stripe customer by uid metadata, or create one."""
    s = _get_stripe()
    loop = asyncio.get_event_loop()

    info = await get_user_stripe_info(uid)
    if info and info.get("stripe_customer_id"):
        return info["stripe_customer_id"]

    customers = await loop.run_in_executor(
        None, lambda: s.Customer.list(email=email, limit=1)
    )
    if customers.data:
        customer_id = customers.data[0].id
    else:
        customer = await loop.run_in_executor(
            None,
            lambda: s.Customer.create(email=email, metadata={"firebase_uid": uid}),
        )
        customer_id = customer.id

    await update_user_stripe(uid, stripe_customer_id=customer_id)
    return customer_id


# ── Request / Response Models ────────────────────────────────────────────────

class CheckoutRequest(BaseModel):
    price_id: str
    success_url: str = "https://tailormadecoloringbook.app/success"
    cancel_url: str = "https://tailormadecoloringbook.app/pricing"


class CheckoutResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/config")
async def get_stripe_config():
    """Return publishable key and mode for the frontend (no auth needed)."""
    _, publishable_key = _get_stripe_keys()
    return {
        "publishable_key": publishable_key,
        "mode": _get_stripe_mode(),
    }


@router.post("/checkout", response_model=CheckoutResponse)
@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    user: dict = Depends(get_current_user),
):
    """Create a Stripe Checkout Session and return the URL."""
    if body.price_id not in ALLOWED_PRICE_IDS:
        raise HTTPException(status_code=400, detail="Invalid price selection")

    s = _get_stripe()
    loop = asyncio.get_event_loop()

    customer_id = await _find_or_create_customer(user["email"], user["uid"])
    selected_tier = PRICE_ID_TO_TIER[body.price_id]
    is_subscription = selected_tier in ("family", "teacher")

    session_params = {
        "customer": customer_id,
        "line_items": [{"price": body.price_id, "quantity": 1}],
        "mode": "subscription" if is_subscription else "payment",
        "success_url": body.success_url,
        "cancel_url": body.cancel_url,
        "metadata": {
            "firebase_uid": user["uid"],
            "price_id": body.price_id,
            "tier": selected_tier,
        },
    }

    try:
        session = await loop.run_in_executor(
            None, lambda: s.checkout.Session.create(**session_params)
        )
    except stripe.StripeError as e:
        logger.error("stripe_checkout_error", error=str(e), uid=user["uid"])
        raise HTTPException(status_code=502, detail="Failed to create checkout session")

    logger.info(
        "checkout_session_created",
        uid=user["uid"],
        session_id=session.id,
        mode=session_params["mode"],
    )
    return CheckoutResponse(checkout_url=session.url)


@router.post("/create-portal-session", response_model=PortalResponse)
async def create_portal_session(user: dict = Depends(get_current_user)):
    """Create a Stripe Customer Portal session for subscription management."""
    s = _get_stripe()
    loop = asyncio.get_event_loop()

    info = await get_user_stripe_info(user["uid"])
    if not info or not info.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No Stripe customer found")

    return_url = settings.stripe_portal_return_url or "https://tailormadecoloringbook.app/billing"

    try:
        session = await loop.run_in_executor(
            None,
            lambda: s.billing_portal.Session.create(
                customer=info["stripe_customer_id"],
                return_url=return_url,
            ),
        )
    except stripe.StripeError as e:
        logger.error("stripe_portal_error", error=str(e), uid=user["uid"])
        raise HTTPException(status_code=502, detail="Failed to create portal session")

    return PortalResponse(portal_url=session.url)


# ── Webhook (NO auth middleware) ─────────────────────────────────────────────

async def _claim_event(event_id: str) -> bool:
    """Atomically claim a Stripe event id for processing.

    Returns True if this is the first time we've seen the event (caller should
    process it), or False if it was already claimed (duplicate → no-op). Backed
    by a create-if-absent write to stripe_events/{event_id}, which the Firestore
    server rejects with AlreadyExists on a second attempt.
    """
    from firebase_admin import firestore as fs
    from google.api_core.exceptions import AlreadyExists

    db = fs.client()
    loop = asyncio.get_event_loop()

    def _create() -> bool:
        from datetime import datetime, timezone
        try:
            db.collection("stripe_events").document(event_id).create(
                {"processed_at": datetime.now(timezone.utc)}
            )
            return True
        except AlreadyExists:
            return False

    return await loop.run_in_executor(None, _create)


async def _release_event(event_id: str) -> None:
    """Release an event claim so Stripe's retry can reprocess after a failure."""
    from firebase_admin import firestore as fs
    db = fs.client()
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(
            None,
            lambda: db.collection("stripe_events").document(event_id).delete(),
        )
    except Exception as e:
        logger.warning("stripe_event_release_failed", event_id=event_id, error=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events. No Firebase auth — uses Stripe signature."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        logger.warning("stripe_webhook_invalid_payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        logger.warning("stripe_webhook_invalid_signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_id = event["id"]
    event_type = event["type"]
    data_object = event["data"]["object"]
    logger.info("stripe_webhook_received", event_type=event_type, event_id=event_id)

    # Idempotency: claim the event before doing any state change. Stripe retries
    # any non-2xx (and on its own schedule), so without this a redelivered
    # checkout would grant credits twice.
    newly_claimed = await _claim_event(event_id)
    if not newly_claimed:
        logger.info("stripe_webhook_duplicate_ignored", event_id=event_id, event_type=event_type)
        return {"status": "ok", "duplicate": True}

    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(data_object)
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data_object)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data_object)
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(data_object)
        else:
            logger.info("stripe_webhook_unhandled", event_type=event_type)
    except Exception:
        # Processing failed — release the claim so Stripe's retry reprocesses
        # this event rather than hitting the duplicate no-op path forever.
        await _release_event(event_id)
        raise

    return {"status": "ok"}


# ── Webhook Handlers ─────────────────────────────────────────────────────────

async def _get_uid_from_customer(customer_id: str) -> str | None:
    """Look up Firebase UID from Stripe customer metadata or Firestore."""
    s = _get_stripe()
    loop = asyncio.get_event_loop()

    customer = await loop.run_in_executor(
        None, lambda: s.Customer.retrieve(customer_id)
    )
    uid = customer.get("metadata", {}).get("firebase_uid")
    if uid:
        return uid

    from firebase_admin import firestore as fs
    db = fs.client()
    docs = await loop.run_in_executor(
        None,
        lambda: list(
            db.collection("users")
            .where("stripe_customer_id", "==", customer_id)
            .limit(1)
            .stream()
        ),
    )
    return docs[0].id if docs else None


async def _handle_checkout_completed(session: dict) -> None:
    """checkout.session.completed — set tier and subscription info."""
    uid = session.get("metadata", {}).get("firebase_uid")
    customer_id = session.get("customer")
    customer_email = (
        (session.get("customer_details") or {}).get("email")
        or session.get("customer_email")
    )

    if not uid and customer_id:
        uid = await _get_uid_from_customer(customer_id)

    if not uid:
        logger.error("stripe_checkout_no_uid", session_id=session.get("id"))
        raise RuntimeError("Stripe checkout session did not include a Firebase UID")

    mode = session.get("mode")
    subscription_id = session.get("subscription")

    if mode == "subscription":
        if not subscription_id:
            raise RuntimeError("Subscription checkout completed without subscription ID")
        s = _get_stripe()
        loop = asyncio.get_event_loop()
        sub = await loop.run_in_executor(
            None, lambda: s.Subscription.retrieve(subscription_id)
        )
        price_id = sub["items"]["data"][0]["price"]["id"] if sub["items"]["data"] else None
        if price_id not in PRICE_ID_TO_TIER:
            raise RuntimeError(f"Unrecognized subscription price ID: {price_id}")
        tier = PRICE_ID_TO_TIER[price_id]

        await update_user_stripe(
            uid,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            subscription_tier=tier,
            subscription_active=True,
        )
        logger.info("subscription_activated", uid=uid, tier=tier)

        # Non-fatal: email failure never blocks checkout flow
        try:
            from app.services.email import send_purchase_confirmed

            send_purchase_confirmed(
                to_email=customer_email or "",
                plan_name=tier,
            )
        except Exception as e:
            logger.warning("purchase_email_failed_non_fatal", uid=uid, error=str(e))

    elif mode == "payment":
        price_id = session.get("metadata", {}).get("price_id")
        if price_id != settings.stripe_single_price_id:
            raise RuntimeError(f"One-time payment used invalid price ID: {price_id}")

        from firebase_admin import firestore as fs
        from google.cloud.firestore_v1 import Increment

        db = fs.client()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: db.collection("users").document(uid).set(
                {
                    "one_time_credits": Increment(1),
                    "stripe_customer_id": customer_id,
                },
                merge=True,
            ),
        )
        logger.info("one_time_credit_added", uid=uid)

        # Non-fatal: email failure never blocks checkout flow
        try:
            from app.services.email import send_purchase_confirmed

            send_purchase_confirmed(
                to_email=customer_email or "",
                plan_name="single",
            )
        except Exception as e:
            logger.warning("purchase_email_failed_non_fatal", uid=uid, error=str(e))
    else:
        raise RuntimeError(f"Unsupported checkout mode: {mode}")


async def _handle_subscription_updated(subscription: dict) -> None:
    """customer.subscription.updated — update tier if plan changed."""
    customer_id = subscription.get("customer")
    uid = await _get_uid_from_customer(customer_id)
    if not uid:
        logger.error("stripe_sub_updated_no_uid", customer_id=customer_id)
        raise RuntimeError(f"Could not resolve Firebase UID for customer {customer_id}")

    price_id = (
        subscription["items"]["data"][0]["price"]["id"]
        if subscription.get("items", {}).get("data")
        else None
    )
    if price_id not in PRICE_ID_TO_TIER:
        raise RuntimeError(f"Unrecognized subscription price ID: {price_id}")
    tier = PRICE_ID_TO_TIER[price_id]
    status = subscription.get("status")
    active = status in ("active", "trialing")

    await update_user_stripe(
        uid,
        stripe_subscription_id=subscription.get("id"),
        subscription_tier=tier,
        subscription_active=active,
    )
    logger.info("subscription_updated", uid=uid, tier=tier, status=status)


async def _handle_subscription_deleted(subscription: dict) -> None:
    """customer.subscription.deleted — reset to free tier."""
    customer_id = subscription.get("customer")
    uid = await _get_uid_from_customer(customer_id)
    if not uid:
        logger.error("stripe_sub_deleted_no_uid", customer_id=customer_id)
        raise RuntimeError(f"Could not resolve Firebase UID for customer {customer_id}")

    await update_user_stripe(
        uid,
        subscription_tier="free",
        subscription_active=False,
    )
    logger.info("subscription_deleted", uid=uid)


async def _handle_payment_failed(invoice: dict) -> None:
    """invoice.payment_failed — mark subscription inactive, log to Sentry."""
    customer_id = invoice.get("customer")
    uid = await _get_uid_from_customer(customer_id)
    if not uid:
        logger.error("stripe_payment_failed_no_uid", customer_id=customer_id)
        raise RuntimeError(f"Could not resolve Firebase UID for customer {customer_id}")

    await update_user_stripe(uid, subscription_active=False)
    logger.warning("payment_failed", uid=uid, invoice_id=invoice.get("id"))

    try:
        import sentry_sdk
        sentry_sdk.capture_message(
            f"Stripe payment failed for user {uid}",
            level="warning",
        )
    except ImportError:
        pass
