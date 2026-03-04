from pydantic import BaseModel, Field, field_validator
import bleach
from typing import Optional
from datetime import datetime


class Scene(BaseModel):
    page_number: int
    description: str
    subject_hint: str  # e.g. "dog", "dinosaur_trex"
    theme: str
    complexity: str  # simple | beginner | medium | advanced


class BookRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=80)
    theme: str = Field(..., min_length=2, max_length=100)
    age_range: str = Field(..., pattern=r"^(2-4|4-6|6-9|9-12)$")
    page_count: int = Field(default=8, ge=4, le=15)
    story_prompt: Optional[str] = Field(default="", max_length=300)
    character_names: Optional[list[str]] = Field(default=[])

    @field_validator("title", "theme", "story_prompt", mode="before")
    @classmethod
    def sanitize_text(cls, v):
        if v is None:
            return v
        return bleach.clean(str(v), tags=[], strip=True).strip()

    @field_validator("character_names", mode="before")
    @classmethod
    def sanitize_names(cls, v):
        if not v:
            return []
        return [bleach.clean(str(name), tags=[], strip=True).strip() for name in v]


class BookResponse(BaseModel):
    book_id: str
    title: str
    status: str  # generating | complete | failed
    pdf_url: Optional[str] = None
    page_urls: list[str] = []
    page_count: int
    created_at: datetime
    theme: str
    age_range: str


class GenerationStatus(BaseModel):
    book_id: str
    status: str
    progress: int  # 0-100
    message: str
