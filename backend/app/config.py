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
    custom_lora_url: str = ""  # LoRA weights URL for coloring book style
    lora_scale: float = 1.0   # LoRA influence scale (0.0-1.0)

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

    # Generation limits
    max_pages: int = 15
    max_concurrent_fal_calls: int = 5

    # Cost tracking (per-unit rates for margin calculation)
    # fal.ai FLUX LoRA: $0.035/megapixel × 2.10 MP (1216×1728) = $0.074/image
    cost_flux_lora: float = 0.074
    # Anthropic Claude Haiku 4.5: $1.00/MTok input, $5.00/MTok output
    cost_haiku_input: float = 0.000001   # per token
    cost_haiku_output: float = 0.000005  # per token

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
