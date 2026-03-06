import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
from app.config import get_settings

logger = structlog.get_logger()
security = HTTPBearer()
settings = get_settings()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Verify Firebase ID token and return user info."""
    token = credentials.credentials

    # ── DEV BYPASS ───────────────────────────────────────────────────────────
    # Allows testing without a real Firebase token in development.
    # NEVER remove this env check — it must always be gated on APP_ENV.
    if settings.app_env == "development" and token == "dev-test-token":
        logger.warning("auth_bypass_used", uid="test-user-123")
        return {
            "uid": "test-user-123",
            "email": "test@tailormade.dev",
            "tier": "free",
        }
    # ─────────────────────────────────────────────────────────────────────────

    try:
        decoded = firebase_auth.verify_id_token(token)
        return {
            "uid": decoded["uid"],
            "email": decoded.get("email"),
            "tier": decoded.get("tier", "free"),
        }
    except firebase_admin.exceptions.FirebaseError as e:
        logger.warning("auth_failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception as e:
        logger.warning("auth_failed_unexpected", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")