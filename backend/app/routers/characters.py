from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, Form
from datetime import datetime, timezone
import uuid
import structlog
from app.middleware.auth import get_current_user
from app.services import sketch_converter, storage, firebase

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/characters", tags=["characters"])

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

    try:
        input_bytes = await image.read()
    except Exception as e:
        logger.error("character_image_read_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to read the uploaded image")

    # Generate sketch from bytes
    try:
        sketch_bytes = sketch_converter.image_bytes_to_sketch_bytes(input_bytes)
    except Exception as e:
        logger.error("character_sketch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process sketch")

    # Upload both images to R2
    try:
        original_ext = image.filename.split(".")[-1] if "." in image.filename else "png"
        original_url = await storage.upload_character_asset(input_bytes, character_id, f"original.{original_ext}")
        sketch_url = await storage.upload_character_asset(sketch_bytes, character_id, "sketch.png")
    except Exception as e:
        logger.error("character_upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to upload assets")

    # Save to Firestore
    character_data = {
        "character_id": character_id,
        "uid": uid,
        "name": name,
        "relationship": relationship,
        "character_type": character_type,
        "original_url": original_url,
        "sketch_url": sketch_url,
        "created_at": datetime.now(timezone.utc),
    }
    
    try:
        await firebase.save_character(character_id, character_data)
    except Exception as e:
        logger.error("character_save_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to save character data")

    logger.info("character_creation_complete", uid=uid, character_id=character_id)
    return character_data

@router.get("/")
async def get_characters(user: dict = Depends(get_current_user)):
    try:
        characters = await firebase.get_user_characters(user["uid"])
        return characters
    except Exception as e:
        logger.error("character_fetch_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch characters")

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
