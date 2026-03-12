from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

    # Sentry init (silently skip if no DSN configured)
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                traces_sample_rate=0.2,
                environment=settings.app_env,
            )
            logger.info("sentry_initialized")
        except Exception as e:
            logger.warning("sentry_init_failed", error=str(e))

    # Firebase init
    try:
        if not firebase_admin._apps:
            cert_val = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
            if not cert_val:
                cert_val = settings.firebase_service_account_path
                
            try:
                import ast
                try:
                    cert_dict = json.loads(cert_val)
                except json.JSONDecodeError:
                    cert_dict = ast.literal_eval(cert_val)
                cred = credentials.Certificate(cert_dict)
            except Exception as je:
                firebase_init_error = f"ParseError: {je} | val length: {len(cert_val)}"
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

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://tailormade-coloring-book.vercel.app",
    "https://tailormadecoloringbook.vercel.app",
    "https://tailormadecoloringbook.app",
    "https://www.tailormadecoloringbook.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return JSON with CORS headers.
    Without this, 500s bypass CORSMiddleware and the browser blocks the response."""
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    logger.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )


from app.routers import auth, books, admin, library, characters, profiles, stripe_router  # noqa: E402

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)
app.include_router(library.router)
app.include_router(characters.router)
app.include_router(profiles.router)
app.include_router(stripe_router.router)


@app.get("/health")
async def health():
    """Liveness probe — always returns 200 if the server is running.
    Dependency status is reported in the response body for observability."""
    import json

    checks = {}

    try:
        from firebase_admin import firestore
        db = firestore.client()
        db.collection("_health").limit(1).get()
        checks["firebase"] = "ok"
    except Exception as e:
        checks["firebase"] = globals().get("firebase_init_error") or f"error: {str(e)[:100]}"

    checks["version"] = 3

    try:
        from app.services.storage import _get_r2_client
        from app.config import get_settings
        s = get_settings()
        _get_r2_client().head_bucket(Bucket=s.r2_bucket_name)
        checks["r2"] = "ok"
    except Exception as e:
        checks["r2"] = f"error: {str(e)[:100]}"

    status = "ok" if checks.get("firebase") == "ok" and checks.get("r2") == "ok" else "degraded"
    # Always return 200 so Railway healthcheck passes.
    # Monitoring tools can check the "status" field for degradation.
    return {"status": status, "checks": checks}
