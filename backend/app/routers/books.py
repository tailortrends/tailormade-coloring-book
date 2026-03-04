from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import uuid
import httpx
import structlog

from app.middleware.auth import get_current_user
from app.middleware.rate_limit import check_rate_limit, increment_usage
from app.models.book import BookRequest, BookResponse
from app.services import (
    content_filter,
    scene_planner,
    image_gen,
    pdf_builder,
    storage,
    firebase,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.post("/generate", response_model=BookResponse)
async def generate_book(
    request: BookRequest,
    user: dict = Depends(get_current_user),
):
    uid = user["uid"]
    tier = user.get("tier", "free")
    book_id = str(uuid.uuid4())

    logger.info(
        "book_generation_started",
        uid=uid,
        book_id=book_id,
        theme=request.theme,
        page_count=request.page_count,
    )

    # FIX 2: Check rate limit BEFORE generation (read-only, transactional)
    await check_rate_limit(uid, tier)

    # Step 1: Content safety (FIX 4: checks ALL fields)
    is_safe, reason = await content_filter.check_content_safety(request)
    if not is_safe:
        raise HTTPException(status_code=422, detail=f"Content not allowed: {reason}")

    # Step 2: Scene planning
    try:
        scenes = await scene_planner.plan_scenes(request)
    except Exception as e:
        logger.error("scene_planning_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Scene planning failed")

    # Step 3: Image generation (FIX 1: concurrent, FIX 3: with retry)
    try:
        image_results = await image_gen.generate_images(scenes)
    except Exception as e:
        logger.error("image_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Image generation failed")

    # Step 4: Post-process images (grayscale -> B&W threshold)
    processed_bytes = []
    for result in sorted(image_results, key=lambda r: r.page_number):
        if not result.success:
            continue
        async with httpx.AsyncClient() as client:
            resp = await client.get(result.image_url)
        processed = await image_gen.post_process_image(resp.content)
        processed_bytes.append(processed)

    # Step 5: Upload page images to R2
    page_urls = []
    for i, img_bytes in enumerate(processed_bytes):
        url = await storage.upload_image(img_bytes, book_id, i + 1)
        page_urls.append(url)

    # Step 6: Build PDF (FIX 6: streams to temp disk, not memory)
    try:
        pdf_bytes = await pdf_builder.build_pdf(
            book_id=book_id,
            title=request.title,
            page_image_urls=page_urls,
            age_range=request.age_range,
        )
    except Exception as e:
        logger.error("pdf_build_failed", error=str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")

    # Step 7: Upload PDF to R2
    pdf_url = await storage.upload_pdf(pdf_bytes, book_id)

    # Step 8: Save to Firestore
    book_data = {
        "book_id": book_id,
        "uid": uid,
        "title": request.title,
        "theme": request.theme,
        "age_range": request.age_range,
        "page_count": len(page_urls),
        "page_urls": page_urls,
        "pdf_url": pdf_url,
        "status": "complete",
        "created_at": datetime.now(timezone.utc),
    }
    await firebase.save_book(book_id, book_data)

    # FIX 2: Increment usage ONLY after successful generation
    await increment_usage(uid)

    logger.info(
        "book_generation_complete", uid=uid, book_id=book_id, pdf_url=pdf_url
    )

    return BookResponse(
        book_id=book_id,
        title=request.title,
        status="complete",
        pdf_url=pdf_url,
        page_urls=page_urls,
        page_count=len(page_urls),
        created_at=datetime.now(timezone.utc),
        theme=request.theme,
        age_range=request.age_range,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, user: dict = Depends(get_current_user)):
    data = await firebase.get_book(book_id)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found")
    if data.get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your book")
    return BookResponse(**data)


@router.get("/", response_model=list[BookResponse])
async def list_books(user: dict = Depends(get_current_user)):
    books = await firebase.get_user_books(user["uid"])
    return [BookResponse(**b) for b in books]
