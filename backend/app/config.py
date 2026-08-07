from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",       # ← this one line
    )

    # App
    app_env: str = "development"
    debug: bool = False

    # fal.ai
    fal_key: str  # NO default — must be in .env
    # Legacy fields — kept optional so existing .env files still load.
    # Image generation now uses fal-ai/flux-pro/kontext (no LoRA).
    custom_lora_url: str = ""
    lora_scale: float = 1.0

    # Anthropic
    anthropic_api_key: str  # NO default

    # Firebase
    firebase_service_account_json: str = ""
    firebase_service_account_path: str = "./app/tailormade-coloring-book-firebase-adminsdk-fbsvc-677adebcf5.json"
    firebase_project_id: str  # NO default

    # Cloudflare R2
    r2_account_id: str 
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_url: str 

    # Tier limits
    # Free tier — lifetime single book, not monthly
    free_lifetime_limit: int = 1       # 1 book total, ever
    free_max_pages: int = 6
    # Single one-time purchase
    single_max_pages: int = 15
    # Family subscription
    family_monthly_limit: int = 12
    family_max_pages: int = 15
    # Teacher subscription
    teacher_monthly_limit: int = 25
    teacher_max_pages: int = 12

    # Admin
    admin_uids: str = ""  # Comma-separated Firebase UIDs
    admin_secret_token: str = ""  # X-Admin-Token header value

    # Stripe — dual mode (admin toggleable)
    stripe_mode: str = "test"  # "test" or "live" — default from env, overridable via Firestore
    stripe_live_secret_key: str = ""
    stripe_live_publishable_key: str = ""
    stripe_test_secret_key: str = ""
    stripe_test_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    # Legacy, mode-agnostic price IDs. Kept as a fallback when the mode-specific
    # IDs below are unset, so existing deployments keep working.
    stripe_family_price_id: str = ""
    stripe_teacher_price_id: str = ""
    stripe_single_price_id: str = ""
    # Mode-specific price IDs (preferred). Selected by the active STRIPE_MODE the
    # same way secret keys are — a live-mode price is never accepted while in test
    # mode and vice versa.
    stripe_live_family_price_id: str = ""
    stripe_live_teacher_price_id: str = ""
    stripe_live_single_price_id: str = ""
    stripe_test_family_price_id: str = ""
    stripe_test_teacher_price_id: str = ""
    stripe_test_single_price_id: str = ""
    stripe_portal_return_url: str = ""

    # Sentry
    sentry_dsn: str = ""  # Backend Sentry DSN (from env)

    # Resend Email (optional — non-blocking transactional emails)
    resend_api_key: Optional[str] = None
    resend_from_email: str = "noreply@tailormadecoloringbook.app"
    resend_from_name: str = "TailorMade Coloring Book"

    # Generation limits
    max_pages: int = 15
    max_concurrent_fal_calls: int = 5
    # Hard per-user/day ceiling on paid generations (books + character sketches),
    # independent of tier quota. A cost circuit-breaker against a single account
    # running up unbounded fal.ai spend.
    daily_generation_ceiling: int = 50

    @property
    def admin_uid_list(self) -> list[str]:
        return [u.strip() for u in self.admin_uids.split(",") if u.strip()]

    # Cost tracking (per-unit rates for margin calculation)
    # fal.ai FLUX.1 Kontext [pro]: $0.04/image
    cost_flux_lora: float = 0.04
    # Anthropic Claude Haiku 4.5: $1.00/MTok input, $5.00/MTok output
    cost_haiku_input: float = 0.000001   # per token
    cost_haiku_output: float = 0.000005  # per token

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def validate_launch_environment(self) -> None:
        """Fail fast when required runtime integrations are not configured."""
        missing: list[str] = []

        required = [
            "fal_key",
            "anthropic_api_key",
            "firebase_project_id",
            "r2_account_id",
            "r2_access_key_id",
            "r2_secret_access_key",
            "r2_bucket_name",
            "r2_public_url",
            "stripe_webhook_secret",
            "stripe_family_price_id",
            "stripe_teacher_price_id",
            "stripe_single_price_id",
        ]
        for field_name in required:
            if not str(getattr(self, field_name, "")).strip():
                missing.append(field_name.upper())

        if self.stripe_mode not in {"test", "live"}:
            missing.append("STRIPE_MODE must be 'test' or 'live'")
        elif self.stripe_mode == "live":
            if not self.stripe_live_secret_key.strip():
                missing.append("STRIPE_LIVE_SECRET_KEY")
            if not self.stripe_live_publishable_key.strip():
                missing.append("STRIPE_LIVE_PUBLISHABLE_KEY")
        else:
            if not self.stripe_test_secret_key.strip():
                missing.append("STRIPE_TEST_SECRET_KEY")
            if not self.stripe_test_publishable_key.strip():
                missing.append("STRIPE_TEST_PUBLISHABLE_KEY")

        if self.is_production:
            has_inline_firebase = bool(self.firebase_service_account_json.strip())
            has_file_firebase = bool(
                self.firebase_service_account_path.strip()
                and os.path.exists(self.firebase_service_account_path)
            )
            if not (has_inline_firebase or has_file_firebase):
                missing.append("FIREBASE_SERVICE_ACCOUNT_JSON or valid FIREBASE_SERVICE_ACCOUNT_PATH")

        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(missing)
            )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
