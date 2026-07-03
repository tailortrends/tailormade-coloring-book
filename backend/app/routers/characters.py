from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form
from datetime import datetime, timezone
import uuid
import httpx
import structlog
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import (
    reserve_daily_generation,
    release_daily_generation,
)
from app.services import image_gen, storage, firebase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/characters", tags=["characters"])

# Per-user cap on stored characters, mirroring the child-profile cap.
MAX_CHARACTERS_PER_USER = 5

VALID_RELATIONSHIPS = [
    "mother", "father", "son", "daughter",
    "grandpa1", "grandpa2", "grandma1", "grandma2",
    "uncle", "aunt", "brother", "sister",
    "cousin", "pet", "friend", "other",
]

VALID_CHARACTER_TYPES = ["person", "animal"]


@router.post("/")
async def create_character(
    name: str = Form(...),
    relationship: str = Form(...),
    character_type: str = Form("person"),
    image: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    if relationship not in VALID_RELATIONSHIPS:
        raise HTTPException(status_code=422, detail=f"Invalid relationship. Must be one of: {VALID_RELATIONSHIPS}")
    if character_type not in VALID_CHARACTER_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid character_type. Must be one of: {VALID_CHARACTER_TYPES}")

    uid = user["uid"]
    character_id = str(uuid.uuid4())
    logger.info("character_creation_started", uid=uid, character_id=character_id, name=name, relationship=relationship)

    # Per-user cap on stored characters (mirrors the child-profile cap).
    existing = await firebase.get_user_characters(uid)
    if len(existing) >= MAX_CHARACTERS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_CHARACTERS_PER_USER} characters allowed per account.",
        )

    try:
        input_bytes = await image.read()
    except Exception as e:
        logger.error("character_image_read_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to read the uploaded image")

    # Reserve a daily-generation slot BEFORE the paid Kontext sketch call. This
    # is the same hard per-user/day ceiling that book generation consumes — it
    # caps fal.ai spend even for an authenticated user hammering this endpoint.
    # Released on any failure so a failed sketch doesn't burn the day's ceiling.
    await reserve_daily_generation(uid)
    reservation_active = True
    try:
        return await _create_character_after_reservation(
            uid, character_id, name, relationship, character_type,
            image, input_bytes,
        )
    except Exception:
        if reservation_active:
            await release_daily_generation(uid)
        raise


async def _create_character_after_reservation(
    uid: str,
    character_id: str,
    name: str,
    relationship: str,
    character_type: str,
    image: UploadFile,
    input_bytes: bytes,
):
    # Upload the original photo to R2 first — Kontext needs a reachable URL.
    try:
        original_ext = image.filename.split(".")[-1] if "." in image.filename else "png"
        original_ext = original_ext.lower()
        original_key = await storage.upload_character_asset(
            input_bytes, character_id, f"original.{original_ext}"
        )
        original_url = storage.generate_presigned_url(
            original_key,
            expiry_seconds=storage.IMAGE_URL_EXPIRY_SECONDS,
        )
    except Exception as e:
        logger.error("character_upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload original photo")

    # Convert the photo into a coloring-book character sketch via Kontext.
    try:
        kontext_sketch_url = await image_gen.generate_character_sketch(original_url)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(kontext_sketch_url)
            resp.raise_for_status()
            sketch_bytes = resp.content
        sketch_key = await storage.upload_character_asset(
            sketch_bytes, character_id, "sketch.png"
        )
        sketch_url = storage.generate_presigned_url(
            sketch_key,
            expiry_seconds=storage.IMAGE_URL_EXPIRY_SECONDS,
        )
    except Exception as e:
        logger.error("character_sketch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate character sketch")

    # Save to Firestore
    character_data = {
        "character_id": character_id,
        "uid": uid,
        "name": name,
        "relationship": relationship,
        "character_type": character_type,
        "original_key": original_key,
        "sketch_key": sketch_key,
        "created_at": datetime.now(timezone.utc),
    }
    
    try:
        await firebase.save_character(character_id, character_data)
    except Exception as e:
        logger.error("character_save_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to save character data")

    logger.info("character_creation_complete", uid=uid, character_id=character_id)
    return character_data | {
        "original_url": original_url,
        "sketch_url": sketch_url,
    }

@router.get("/")
async def get_characters(user: dict = Depends(get_current_user)):
    try:
        characters = await firebase.get_user_characters(user["uid"])
        signed = []
        for char in characters:
            original_key = char.get("original_key") or storage.object_key_from_url(char.get("original_url"))
            sketch_key = char.get("sketch_key") or storage.object_key_from_url(char.get("sketch_url"))
            signed.append(char | {
                "original_url": storage.signed_url_for_key_or_url(original_key),
                "sketch_url": storage.signed_url_for_key_or_url(sketch_key),
            })
        return signed
    except Exception as e:
        logger.error("character_fetch_failed", uid=user["uid"], error=str(e), error_type=type(e).__name__)
        # Return empty list so dashboard still loads (likely missing Firestore composite index)
        return []

@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: str, user: dict = Depends(get_current_user)):
    # Simple check if character exists (and verify owner if get_user_characters handles it)
    characters = await firebase.get_user_characters(user["uid"])
    char = next((c for c in characters if c["character_id"] == character_id), None)
    if not char:
        raise HTTPException(status_code=404, detail="Character not found or not owned by user")

    try:
        await storage.delete_character_assets(character_id)
    except Exception as e:
        logger.warning("r2_character_cleanup_failed", character_id=character_id, error=str(e))

    try:
        await firebase.delete_character(character_id)
    except Exception as e:
        logger.error("character_delete_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete character")
    
    return Response(status_code=204)
