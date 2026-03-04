import firebase_admin
from firebase_admin import auth as firebase_auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

logger = structlog.get_logger()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Verify Firebase ID token and return user info."""
    token = credentials.credentials
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
