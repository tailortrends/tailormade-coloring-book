"""
Tests for the Stripe router — checkout sessions, portal sessions, and webhooks.
All Stripe SDK calls are mocked; no real API calls are made.
"""

import json
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient


# ── Patch Firebase and settings BEFORE importing app ─────────────────────────

mock_firebase = MagicMock()
mock_firebase._apps = {"default": True}

with patch.dict("sys.modules", {
    "firebase_admin": mock_firebase,
    "firebase_admin.auth": MagicMock(),
    "firebase_admin.credentials": MagicMock(),
    "firebase_admin.firestore": MagicMock(),
    "google.cloud.firestore_v1": MagicMock(),
    "sentry_sdk": MagicMock(),
}):
    import os
    os.environ.setdefault("FAL_KEY", "test")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test")
    os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
    os.environ.setdefault("R2_ACCOUNT_ID", "test")
    os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
    os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
    os.environ.setdefault("R2_BUCKET_NAME", "test")
    os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("STRIPE_MODE", "test")
    os.environ.setdefault("STRIPE_TEST_SECRET_KEY", "sk_test_fake")
    os.environ.setdefault("STRIPE_TEST_PUBLISHABLE_KEY", "pk_test_fake")
    os.environ.setdefault("STRIPE_LIVE_SECRET_KEY", "sk_live_fake")
    os.environ.setdefault("STRIPE_LIVE_PUBLISHABLE_KEY", "pk_live_fake")
    os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_testsecret")
    os.environ.setdefault("STRIPE_FAMILY_PRICE_ID", "price_family_123")
    os.environ.setdefault("STRIPE_TEACHER_PRICE_ID", "price_teacher_456")
    os.environ.setdefault("STRIPE_SINGLE_PRICE_ID", "price_single_789")

    from app.config import get_settings
    get_settings.cache_clear()

    from app.main import app
    import app.routers.stripe_router as stripe_mod


client = TestClient(app, raise_server_exceptions=False)
AUTH_HEADER = {"Authorization": "Bearer dev-test-token"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_webhook_event(event_type: str, data_object: dict) -> dict:
    return {
        "id": "evt_test_123",
        "type": event_type,
        "data": {"object": data_object},
    }


# ── Test 1: Checkout session creation returns URL ────────────────────────────

@patch("app.routers.stripe_router.get_user_stripe_info", new_callable=AsyncMock)
@patch("app.routers.stripe_router.update_user_stripe", new_callable=AsyncMock)
def test_create_checkout_session_returns_url(mock_update, mock_get_info):
    """Checkout session creation should return a checkout URL."""
    mock_get_info.return_value = {"stripe_customer_id": "cus_existing123"}

    mock_session = MagicMock()
    mock_session.id = "cs_test_abc"
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_abc"

    with patch("stripe.checkout.Session") as mock_checkout_session:
        mock_checkout_session.create.return_value = mock_session

        response = client.post(
            "/api/v1/stripe/create-checkout-session",
            json={
                "price_id": "price_family_123",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
            headers=AUTH_HEADER,
        )

    assert response.status_code == 200
    body = response.json()
    assert "checkout_url" in body
    assert body["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_abc"


# ── Test 2: Webhook rejects invalid signature ────────────────────────────────

def test_webhook_rejects_invalid_signature():
    """Webhook should reject requests with an invalid Stripe signature."""
    payload = json.dumps(_make_webhook_event("checkout.session.completed", {})).encode()

    response = client.post(
        "/api/v1/stripe/webhook",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "stripe-signature": "t=123,v1=invalidsig",
        },
    )

    assert response.status_code == 400


# ── Test 3: checkout.session.completed updates Firestore tier ────────────────

def test_checkout_completed_sets_tier():
    """checkout.session.completed should update subscription_tier in Firestore."""
    mock_sub = MagicMock()
    mock_sub.__getitem__ = lambda self, key: {
        "items": {"data": [{"price": {"id": "price_family_123"}}]}
    }[key]

    event = _make_webhook_event("checkout.session.completed", {
        "id": "cs_test_xyz",
        "metadata": {"firebase_uid": "user-abc"},
        "customer": "cus_test_123",
        "mode": "subscription",
        "subscription": "sub_test_456",
    })

    mock_update = AsyncMock()
    original_update = stripe_mod.update_user_stripe
    stripe_mod.update_user_stripe = mock_update

    try:
        with patch("stripe.Webhook.construct_event", return_value=event), \
             patch("stripe.Subscription.retrieve", return_value=mock_sub):

            payload = json.dumps(event).encode()
            response = client.post(
                "/api/v1/stripe/webhook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "stripe-signature": "t=123,v1=fakesig",
                },
            )

        assert response.status_code == 200
        mock_update.assert_called_once_with(
            "user-abc",
            stripe_customer_id="cus_test_123",
            stripe_subscription_id="sub_test_456",
            subscription_tier="family",
            subscription_active=True,
        )
    finally:
        stripe_mod.update_user_stripe = original_update


# ── Test 4: subscription.deleted resets to free ──────────────────────────────

def test_subscription_deleted_resets_to_free():
    """customer.subscription.deleted should reset tier to free."""
    event = _make_webhook_event("customer.subscription.deleted", {
        "id": "sub_test_456",
        "customer": "cus_test_123",
    })

    mock_update = AsyncMock()
    mock_get_uid = AsyncMock(return_value="user-abc")
    original_update = stripe_mod.update_user_stripe
    original_get_uid = stripe_mod._get_uid_from_customer
    stripe_mod.update_user_stripe = mock_update
    stripe_mod._get_uid_from_customer = mock_get_uid

    try:
        with patch("stripe.Webhook.construct_event", return_value=event):
            payload = json.dumps(event).encode()
            response = client.post(
                "/api/v1/stripe/webhook",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "stripe-signature": "t=123,v1=fakesig",
                },
            )

        assert response.status_code == 200
        mock_update.assert_called_once_with(
            "user-abc",
            subscription_tier="free",
            subscription_active=False,
        )
    finally:
        stripe_mod.update_user_stripe = original_update
        stripe_mod._get_uid_from_customer = original_get_uid
