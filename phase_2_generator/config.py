from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    debug: bool = False

    # fal.ai
    fal_key: str  # NO default — must be in .env

    # Custom LoRA (needed for spot check and batch gen)
    custom_lora_url: str = "https://v3b.fal.media/files/b/0a90dad9/48k2C_DU6yGSBg6AayMRl_pytorch_lora_weights.safetensors" # Can be empty during seed generation

    # Firebase
    firebase_service_account_path: str = "../backend/app/tailormade-coloring-book-firebase-adminsdk-fbsvc-677adebcf5.json"
    firebase_project_id: str = "" # Optional for local scripts if passing default app

    # Cloudflare R2
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_url: str = ""

    # Generation limits
    max_concurrent_fal_calls: int = 5


@lru_cache()
def get_settings() -> Settings:
    return Settings()
