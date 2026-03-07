from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials
import structlog
import logging
import os
import json
import tempfile

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

logger = structlog.get_logger()


firebase_init_error = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global firebase_init_error
    # FIX 5: Validate all required env vars at startup
    from app.config import get_settings

    try:
        settings = get_settings()
        logger.info("config_loaded", env=settings.app_env)
    except Exception as e:
        print(f"\n❌ Missing required environment variables:\n{e}\n")
        print("Copy .env.example to .env and fill in your values.")
        raise SystemExit(1)

    # Firebase init
    try:
        if not firebase_admin._apps:
            cert_val = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
            if not cert_val:
                cert_val = settings.firebase_service_account_path
                
            try:
                cert_dict = json.loads(cert_val)
                cred = credentials.Certificate(cert_dict)
            except json.JSONDecodeError as je:
                firebase_init_error = f"JSONDecodeError: {je} | val length: {len(cert_val)}"
                cred = credentials.Certificate(cert_val)
                
            firebase_admin.initialize_app(cred)
        logger.info("firebase_initialized")
    except Exception as e:
        firebase_init_error = firebase_init_error or str(e)
        if settings.is_production:
            raise RuntimeError(f"Firebase credentials required in production: {e}")
        logger.warning(f"firebase_disabled_dev_mode: {e}")

    logger.info("tailormade_api_ready", env=settings.app_env)
    yield
    logger.info("tailormade_api_shutdown")


app = FastAPI(
    title="TailorMade API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://tailormade-coloring-book.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import auth, books, admin  # noqa: E402

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    """Deep health check — tests all dependencies."""
    import json
    from fastapi import Response

    checks = {}

    try:
        from firebase_admin import firestore

        db = firestore.client()
        db.collection("_health").limit(1).get()
        checks["firebase"] = "ok"
    except Exception as e:
        import app.main as main_mod
        if hasattr(main_mod, "firebase_init_error") and main_mod.firebase_init_error:
            checks["firebase"] = f"Init Failed: {main_mod.firebase_init_error}"
        else:
            checks["firebase"] = f"error: {str(e)[:100]}"

    try:
        from app.services.storage import _get_r2_client
        from app.config import get_settings

        s = get_settings()
        _get_r2_client().head_bucket(Bucket=s.r2_bucket_name)
        checks["r2"] = "ok"
    except Exception as e:
        checks["r2"] = f"error: {str(e)[:100]}"

    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return Response(
        content=json.dumps({"status": status, "checks": checks}),
        status_code=200 if status == "ok" else 503,
        media_type="application/json",
    )
