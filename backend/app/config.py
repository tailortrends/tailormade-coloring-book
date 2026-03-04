from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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

    # Anthropic
    anthropic_api_key: str  # NO default

    # Firebase
    firebase_service_account_path: str = "./app/tailormade-coloring-book-firebase-adminsdk-fbsvc-677adebcf5.json"
    firebase_project_id: str  # NO default

    # Cloudflare R2
    r2_account_id: str 
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_public_url: str 

    # Rate limiting
    free_tier_monthly_limit: int = 1
    pro_tier_monthly_limit: int = 5
    family_tier_monthly_limit: int = 15

    # Generation limits
    max_pages: int = 15
    max_concurrent_fal_calls: int = 5

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
