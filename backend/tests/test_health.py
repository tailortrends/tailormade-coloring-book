"""
/health must validate real dependencies (Firebase, R2, fal model URL, Anthropic),
report each in the body, and still return 200 for Railway liveness. Dependency
probes are stubbed — no real network calls.
"""

import os
from unittest.mock import patch, AsyncMock, MagicMock

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
    os.environ.setdefault("FAL_KEY", "test")
    os.environ.setdefault("ANTHROPIC_API_KEY", "test")
    os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
    os.environ.setdefault("R2_ACCOUNT_ID", "test")
    os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
    os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
    os.environ.setdefault("R2_BUCKET_NAME", "test")
    os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")

    from fastapi.testclient import TestClient
    import app.main as main_mod

client = TestClient(main_mod.app)


def test_health_all_ok():
    with patch.object(main_mod, "_check_firebase", AsyncMock(return_value="ok")), \
         patch.object(main_mod, "_check_r2", AsyncMock(return_value="ok")), \
         patch.object(main_mod, "_check_fal", AsyncMock(return_value="ok")), \
         patch.object(main_mod, "_check_anthropic", AsyncMock(return_value="ok")):
        resp = client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    # All four dependencies are reported, including the fal model URL.
    assert set(["firebase", "r2", "fal", "anthropic"]).issubset(body["checks"].keys())


def test_health_degraded_on_dead_fal_model_but_still_200():
    with patch.object(main_mod, "_check_firebase", AsyncMock(return_value="ok")), \
         patch.object(main_mod, "_check_r2", AsyncMock(return_value="ok")), \
         patch.object(main_mod, "_check_fal", AsyncMock(return_value="error: model url not found")), \
         patch.object(main_mod, "_check_anthropic", AsyncMock(return_value="ok")):
        resp = client.get("/health")

    assert resp.status_code == 200  # liveness still passes
    body = resp.json()
    assert body["status"] == "degraded"
    assert body["checks"]["fal"] == "error: model url not found"
