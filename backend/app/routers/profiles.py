from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional
import uuid
import random
import bleach
import structlog

from app.middleware.auth import get_current_user
from app.services import firebase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

MAX_PROFILES_PER_USER = 5

AVATAR_COLORS = [
    "#6366f1",  # indigo
    "#ec4899",  # pink
    "#f59e0b",  # amber
    "#10b981",  # emerald
    "#3b82f6",  # blue
    "#8b5cf6",  # violet
    "#ef4444",  # red
    "#14b8a6",  # teal
    "#f97316",  # orange
    "#06b6d4",  # cyan
]

VALID_THEMES = [
    "animals", "dinosaur", "space", "fantasy", "ocean",
    "vehicles", "nature", "farm", "unicorns", "princesses",
]


# ── Request / Response models ─────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=2, le=12)
    favorite_themes: list[str] = Field(default=[], max_length=3)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return bleach.clean(str(v), tags=[], strip=True).strip()

    @field_validator("favorite_themes", mode="before")
    @classmethod
    def validate_themes(cls, v: list[str]) -> list[str]:
        if not v:
            return []
        cleaned = [bleach.clean(str(t), tags=[], strip=True).strip().lower() for t in v]
        invalid = [t for t in cleaned if t not in VALID_THEMES]
        if invalid:
            raise ValueError(f"Invalid themes: {invalid}")
        return cleaned[:3]


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    age: Optional[int] = Field(default=None, ge=2, le=12)
    favorite_themes: Optional[list[str]] = Field(default=None, max_length=3)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return bleach.clean(str(v), tags=[], strip=True).strip()

    @field_validator("favorite_themes", mode="before")
    @classmethod
    def validate_themes(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        cleaned = [bleach.clean(str(t), tags=[], strip=True).strip().lower() for t in v]
        invalid = [t for t in cleaned if t not in VALID_THEMES]
        if invalid:
            raise ValueError(f"Invalid themes: {invalid}")
        return cleaned[:3]


class ProfileResponse(BaseModel):
    profile_id: str
    uid: str
    name: str
    age: int
    favorite_themes: list[str]
    avatar_color: str
    created_at: datetime
    is_default: bool


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=ProfileResponse, status_code=201)
async def create_profile(
    body: ProfileCreate,
    user: dict = Depends(get_current_user),
):
    uid = user["uid"]

    existing = await firebase.get_user_profiles(uid)
    if len(existing) >= MAX_PROFILES_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_PROFILES_PER_USER} profiles allowed per account.",
        )

    profile_id = str(uuid.uuid4())
    is_first = len(existing) == 0

    data = {
        "uid": uid,
        "name": body.name,
        "age": body.age,
        "favorite_themes": body.favorite_themes,
        "avatar_color": random.choice(AVATAR_COLORS),
        "created_at": datetime.now(timezone.utc),
        "is_default": is_first,  # first profile auto-becomes default
    }
    await firebase.save_profile(profile_id, data)
    logger.info("profile_created", uid=uid, profile_id=profile_id, name=body.name)

    return ProfileResponse(profile_id=profile_id, **data)


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(user: dict = Depends(get_current_user)):
    profiles = await firebase.get_user_profiles(user["uid"])
    return [ProfileResponse(**p) for p in profiles]


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str, user: dict = Depends(get_current_user)):
    profile = await firebase.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your profile")
    return ProfileResponse(**profile)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    body: ProfileUpdate,
    user: dict = Depends(get_current_user),
):
    profile = await firebase.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your profile")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    await firebase.update_profile(profile_id, updates)
    profile.update(updates)
    return ProfileResponse(**profile)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: str, user: dict = Depends(get_current_user)):
    uid = user["uid"]
    profile = await firebase.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Not your profile")

    all_profiles = await firebase.get_user_profiles(uid)
    if len(all_profiles) <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your only profile. Create another one first.",
        )

    was_default = profile.get("is_default", False)
    await firebase.delete_profile(profile_id)

    # If deleted profile was default, promote the first remaining one
    if was_default:
        remaining = [p for p in all_profiles if p["profile_id"] != profile_id]
        if remaining:
            await firebase.update_profile(remaining[0]["profile_id"], {"is_default": True})


@router.put("/{profile_id}/set-default", response_model=ProfileResponse)
async def set_default_profile(
    profile_id: str,
    user: dict = Depends(get_current_user),
):
    uid = user["uid"]
    profile = await firebase.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Not your profile")

    await firebase.clear_default_profiles(uid)
    await firebase.update_profile(profile_id, {"is_default": True})
    profile["is_default"] = True
    return ProfileResponse(**profile)
