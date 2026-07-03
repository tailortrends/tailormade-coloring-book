import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import Depends, HTTPException, Security
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
    # Allows testing without a real Firebase token in local/dev contexts.
    # Structurally inert outside an explicit debug context: it requires BOTH
    # settings.debug AND a non-production APP_ENV. A single env var can no longer
    # flip production into an open door — both gates must be wrong at once.
    if token == "dev-test-token":
        if settings.is_production:
            # This path must never be honored in production. If we reach it,
            # something is badly misconfigured — alert loudly and fall through
            # to real token verification (which will reject this token).
            logger.error("auth_bypass_attempted_in_production", uid="test-user-123")
            try:
                import sentry_sdk
                sentry_sdk.capture_message(
                    "dev-test-token auth bypass attempted while APP_ENV=production",
                    level="error",
                )
            except Exception:
                pass
        elif settings.debug and settings.app_env != "production":
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


async def get_admin_user(
    user: dict = Depends(get_current_user),
) -> dict:
    """Verify the authenticated user is an admin."""
    if user["uid"] not in settings.admin_uid_list:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
