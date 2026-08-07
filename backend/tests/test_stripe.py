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
    os.environ.setdefault("DEBUG", "true")  # required to honor the dev-test-token bypass
    os.environ.setdefault("STRIPE_MODE", "test")
    os.environ.setdefault("STRIPE_TEST_SECRET_KEY", "test_secret_fake")
    os.environ.setdefault("STRIPE_TEST_PUBLISHABLE_KEY", "pk_test_fake")
    os.environ.setdefault("STRIPE_LIVE_SECRET_KEY", "live_secret_fake")
    os.environ.setdefault("STRIPE_LIVE_PUBLISHABLE_KEY", "pk_live_fake")
    os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "webhook_secret_fake")
    os.environ.setdefault("STRIPE_FAMILY_PRICE_ID", "price_family_123")
    os.environ.setdefault("STRIPE_TEACHER_PRICE_ID", "price_teacher_456")
    os.environ.setdefault("STRIPE_SINGLE_PRICE_ID", "price_single_789")

    from app.config import get_settings
    get_settings.cache_clear()

    from app.main import app
    import app.routers.stripe_router as stripe_mod


client = TestClient(app, raise_server_exceptions=False)
AUTH_HEADER = {"Authorization": "Bearer dev-test-token"}


@pytest.fixture(autouse=True)
def _stub_event_dedup():
    """The webhook now claims each event id in Firestore for idempotency. There
    is no Firestore in these tests, so default the claim to 'first time seen'.
    Tests that exercise idempotency re-patch _claim_event with their own state."""
    with patch.object(stripe_mod, "_claim_event", AsyncMock(return_value=True)), \
         patch.object(stripe_mod, "_release_event", AsyncMock(return_value=None)):
        yield


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


def test_checkout_rejects_unknown_price_id():
    """Client-provided price IDs must be allowlisted before Stripe is called."""
    response = client.post(
        "/api/v1/stripe/checkout",
        json={"price_id": "price_FAKE123MALICIOUS"},
        headers=AUTH_HEADER,
    )

    assert response.status_code == 400


# ── Mode-aware price IDs ──────────────────────────────────────────────────────

def test_allowed_price_ids_follow_active_mode(monkeypatch):
    """The allow-list must reflect the currently active mode: a live-mode price is
    not accepted while in test mode, and vice versa."""
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_family_price_id", "price_test_fam")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_teacher_price_id", "price_test_teach")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_single_price_id", "price_test_single")
    monkeypatch.setattr(stripe_mod.settings, "stripe_live_family_price_id", "price_live_fam")
    monkeypatch.setattr(stripe_mod.settings, "stripe_live_teacher_price_id", "price_live_teach")
    monkeypatch.setattr(stripe_mod.settings, "stripe_live_single_price_id", "price_live_single")

    monkeypatch.setattr(stripe_mod, "_get_stripe_mode", lambda: "test")
    allowed_test = stripe_mod._allowed_price_ids()
    assert "price_test_fam" in allowed_test
    assert "price_live_fam" not in allowed_test
    assert stripe_mod._price_id_to_tier()["price_test_single"] == "single"

    monkeypatch.setattr(stripe_mod, "_get_stripe_mode", lambda: "live")
    allowed_live = stripe_mod._allowed_price_ids()
    assert "price_live_fam" in allowed_live
    assert "price_test_fam" not in allowed_live


def test_checkout_rejects_inactive_mode_price(monkeypatch):
    """Submitting a price ID that belongs to the INACTIVE mode is a 400."""
    monkeypatch.setattr(stripe_mod, "_get_stripe_mode", lambda: "test")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_family_price_id", "price_test_fam")
    monkeypatch.setattr(stripe_mod.settings, "stripe_live_family_price_id", "price_live_fam")

    response = client.post(
        "/api/v1/stripe/checkout",
        json={"price_id": "price_live_fam"},  # live price while mode is test
        headers=AUTH_HEADER,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid price selection"


def test_config_returns_active_mode_price_ids(monkeypatch):
    """GET /config exposes the active mode's price IDs for the frontend."""
    monkeypatch.setattr(stripe_mod, "_get_stripe_mode", lambda: "test")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_family_price_id", "price_test_fam")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_teacher_price_id", "price_test_teach")
    monkeypatch.setattr(stripe_mod.settings, "stripe_test_single_price_id", "price_test_single")

    response = client.get("/api/v1/stripe/config")
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "test"
    assert body["price_ids"] == {
        "family": "price_test_fam",
        "teacher": "price_test_teach",
        "single": "price_test_single",
    }


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


def test_webhook_handler_exception_returns_500():
    """Webhook handler failures must surface as 500s so Stripe retries."""
    event = _make_webhook_event("checkout.session.completed", {
        "id": "cs_test_error",
        "metadata": {"firebase_uid": "user-abc"},
        "customer": "cus_test_123",
        "mode": "subscription",
        "subscription": "sub_test_456",
    })

    original_handler = stripe_mod._handle_checkout_completed

    async def _raise(_session):
        raise RuntimeError("forced handler failure")

    stripe_mod._handle_checkout_completed = _raise
    try:
        with patch("stripe.Webhook.construct_event", return_value=event):
            response = client.post(
                "/api/v1/stripe/webhook",
                content=json.dumps(event).encode(),
                headers={
                    "Content-Type": "application/json",
                    "stripe-signature": "t=123,v1=fakesig",
                },
            )

        assert response.status_code == 500
    finally:
        stripe_mod._handle_checkout_completed = original_handler


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


# ── Test 5: webhook idempotency — replayed event processed exactly once ───────

def _post_event(event: dict):
    return client.post(
        "/api/v1/stripe/webhook",
        content=json.dumps(event).encode(),
        headers={
            "Content-Type": "application/json",
            "stripe-signature": "t=123,v1=fakesig",
        },
    )


def test_webhook_idempotent_on_replay():
    """Delivering the same event id twice must process the handler only once."""
    event = _make_webhook_event("checkout.session.completed", {
        "id": "cs_replay",
        "metadata": {"firebase_uid": "user-abc", "price_id": "price_single_789"},
        "customer": "cus_test_123",
        "mode": "payment",
    })

    seen: set[str] = set()

    async def fake_claim(event_id: str) -> bool:
        if event_id in seen:
            return False
        seen.add(event_id)
        return True

    async def fake_release(event_id: str) -> None:
        seen.discard(event_id)

    handler_calls = []

    async def fake_handler(obj):
        handler_calls.append(obj)

    with patch.object(stripe_mod, "_claim_event", fake_claim), \
         patch.object(stripe_mod, "_release_event", fake_release), \
         patch.object(stripe_mod, "_handle_checkout_completed", fake_handler), \
         patch("stripe.Webhook.construct_event", return_value=event):
        r1 = _post_event(event)
        r2 = _post_event(event)  # same event id — a Stripe redelivery

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json().get("duplicate") is True
    assert len(handler_calls) == 1  # processed exactly once


def test_one_time_payment_adds_single_credit():
    """A one-time (mode=payment) checkout increments one_time_credits once."""
    event = _make_webhook_event("checkout.session.completed", {
        "id": "cs_single",
        "metadata": {"firebase_uid": "user-xyz", "price_id": "price_single_789"},
        "customer": "cus_single_1",
        "mode": "payment",
    })

    captured = {}

    class _FakeDoc:
        def set(self, data, merge=False):
            captured["data"] = data
            captured["merge"] = merge

    class _FakeCollection:
        def document(self, _uid):
            return _FakeDoc()

    class _FakeDB:
        def collection(self, _name):
            return _FakeCollection()

    with patch("stripe.Webhook.construct_event", return_value=event), \
         patch("firebase_admin.firestore.client", return_value=_FakeDB()), \
         patch("google.cloud.firestore_v1.Increment", lambda n: f"INC({n})"):
        response = _post_event(event)

    assert response.status_code == 200
    assert captured["data"]["one_time_credits"] == "INC(1)"
