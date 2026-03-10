from fastapi import APIRouter, Depends, HTTPException, Response
from datetime import datetime, timezone
import uuid
import tempfile
import os
import httpx
import structlog

from app.middleware.auth import get_current_user
from app.middleware.rate_limit import check_rate_limit, increment_usage, GenerationPermit
from app.models.book import BookRequest, BookResponse
from app.config import get_settings
from app.services import (
    content_filter,
    scene_planner,
    image_gen,
    pdf_builder,
    storage,
    firebase,
)

logger = structlog.get_logger()
settings = get_settings()
router = APIRouter(prefix="/api/v1/books", tags=["books"])


async def _record_failed_book(book_id: str, uid: str, request: BookRequest, error: str) -> None:
    """Save a failed book record to Firestore. Never raises."""
    try:
        await firebase.save_book(book_id, {
            "book_id": book_id,
            "uid": uid,
            "title": request.title,
            "theme": request.theme,
            "age_range": request.age_range,
            "page_count": request.page_count,
            "status": "failed",
            "error": error[:500],
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.warning("failed_book_record_error", error=str(e))


async def _record_analytics(request: BookRequest, tier: str, image_metrics, total_cost: float, failed: bool = False) -> None:
    """Non-blocking daily analytics write. Never raises."""
    try:
        data: dict = {
            "books_generated": 0 if failed else 1,
            "pages_generated": 0 if failed else request.page_count,
            "library_hits": image_metrics.library_hits if image_metrics else 0,
            "library_misses": image_metrics.library_misses if image_metrics else 0,
            "total_cost": total_cost,
            "failures": 1 if failed else 0,
            "themes": {request.theme: 1},
            "tiers": {tier: 1},
        }
        await firebase.record_daily_analytics(data)
    except Exception as e:
        logger.warning("analytics_write_failed", error=str(e))


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

    # Check rate limit BEFORE generation — returns permit with max_pages
    permit = await check_rate_limit(uid, tier)

    # Silently cap page count to tier's max (no error, just cap)
    if request.page_count > permit.max_pages:
        logger.info("page_count_capped", requested=request.page_count,
                     capped_to=permit.max_pages, tier=permit.tier)
        request.page_count = permit.max_pages

    # Step 1: Content safety
    is_safe, reason = await content_filter.check_content_safety(request)
    if not is_safe:
        raise HTTPException(status_code=422, detail=f"Content not allowed: {reason}")

    # Step 2: Scene planning (now returns taxonomy-aligned subjects + composition + captions)
    planning_cost = 0.0
    try:
        scenes, planning_cost = await scene_planner.plan_scenes(request)
    except Exception as e:
        logger.error("scene_planning_failed", error=str(e))
        await _record_failed_book(book_id, uid, request, str(e))
        await _record_analytics(request, tier, None, 0.0, failed=True)
        raise HTTPException(status_code=500, detail="Scene planning failed")

    # Step 3: Image generation (all scenes including cover hero)
    try:
        image_results, image_metrics = await image_gen.generate_images(scenes)
    except Exception as e:
        logger.error("image_generation_failed", error=str(e))
        await _record_failed_book(book_id, uid, request, str(e))
        await _record_analytics(request, tier, None, planning_cost, failed=True)
        raise HTTPException(status_code=500, detail="Image generation failed")

    # Step 4: Separate cover hero from interior pages
    # Find which scene is the cover
    cover_scene = next((s for s in scenes if s.is_cover), None)
    cover_page_number = cover_scene.page_number if cover_scene else None

    # Debug: log cover detection
    cover_count = sum(1 for s in scenes if s.is_cover)
    logger.info("cover_pipeline_debug",
               cover_scenes_count=cover_count,
               cover_page_number=cover_page_number,
               all_page_numbers=[s.page_number for s in scenes])

    processed_bytes = []
    cover_hero_bytes = None
    sorted_results = sorted(image_results, key=lambda r: r.page_number)

    for result in sorted_results:
        is_cover_result = result.page_number == cover_page_number

        # Skip failed interior pages, but NEVER skip the cover result —
        # cover is a hero background image, not a coloring page, so
        # quality-validation failures should not discard it.
        if not result.success and not is_cover_result:
            continue

        img_bytes = result.image_bytes
        if not img_bytes and result.image_url:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(result.image_url)
                img_bytes = resp.content
            except Exception as e:
                logger.warning("image_redownload_failed",
                               page=result.page_number, error=str(e))
                if not is_cover_result:
                    continue

        if is_cover_result and img_bytes:
            cover_hero_bytes = img_bytes
        elif not is_cover_result and img_bytes:
            processed_bytes.append(img_bytes)

    # Debug: log cover hero status
    logger.info("cover_hero_debug",
               cover_hero_bytes_present=cover_hero_bytes is not None,
               cover_hero_size=len(cover_hero_bytes) if cover_hero_bytes else 0,
               interior_page_count=len(processed_bytes))

    # Diagnostic: log cover separation results
    logger.info("cover_separation",
                cover_scene_found=cover_scene is not None,
                cover_hero_bytes_size=len(cover_hero_bytes) if cover_hero_bytes else None,
                interior_page_count=len(processed_bytes))

    # Step 5: Write cover hero to temp file for PDF builder (needs local path)
    cover_hero_local_path = None
    if cover_hero_bytes:
        cover_hero_url = await storage.upload_image(cover_hero_bytes, book_id, 0)
        logger.info("cover_hero_uploaded", book_id=book_id, url=cover_hero_url)
        # Also write to temp file for PDF builder
        tmp_cover = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="cover_hero_")
        tmp_cover.write(cover_hero_bytes)
        tmp_cover.close()
        cover_hero_local_path = tmp_cover.name
        logger.info("cover_hero_temp_file", path=cover_hero_local_path)

    logger.info("cover_separation_path",
                cover_hero_path=cover_hero_local_path,
                path_exists=os.path.exists(cover_hero_local_path) if cover_hero_local_path else False)

    # Step 6: Upload interior page images to R2
    page_urls = []
    for i, img_bytes in enumerate(processed_bytes):
        url = await storage.upload_image(img_bytes, book_id, i + 1)
        page_urls.append(url)

    # Step 7: Build PDF (cover hero + clean image-only coloring pages)
    logger.info("pdf_build_cover_debug",
               cover_hero_local_path=cover_hero_local_path,
               cover_hero_file_exists=os.path.exists(cover_hero_local_path) if cover_hero_local_path else False)
    try:
        pdf_bytes = await pdf_builder.build_pdf(
            book_id=book_id,
            title=request.title,
            page_image_urls=page_urls,
            age_range=request.age_range,
            theme=request.theme,
            cover_hero_path=cover_hero_local_path,
        )
    except Exception as e:
        logger.error("pdf_build_failed", error=str(e))
        await _record_failed_book(book_id, uid, request, str(e))
        await _record_analytics(request, tier, image_metrics, planning_cost + image_metrics.total_image_spend, failed=True)
        raise HTTPException(status_code=500, detail="PDF generation failed")
    finally:
        # Clean up temp cover file
        if cover_hero_local_path:
            try:
                os.unlink(cover_hero_local_path)
            except Exception:
                pass

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

    # Step 9: Record generation cost (with library hit/miss tracking)
    image_cost = image_metrics.total_image_spend
    total_cost = image_cost + planning_cost
    retry_count = image_metrics.total_attempts - request.page_count
    library_hits = image_metrics.library_hits
    library_misses = image_metrics.library_misses
    estimated_savings = round(library_hits * settings.cost_flux_lora, 6)
    cost_data = {
        "book_id": book_id,
        "uid": uid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cost": round(total_cost, 6),
        "image_cost": round(image_cost, 6),
        "planning_cost": round(planning_cost, 6),
        "retry_count": max(0, retry_count),
        "page_count": request.page_count,
        "theme": request.theme,
        "title": request.title,
        "status": "success",
        "library_hits": library_hits,
        "library_misses": library_misses,
        "estimated_savings": estimated_savings,
    }
    try:
        await firebase.record_generation_cost(cost_data)
    except Exception as e:
        logger.warning("cost_recording_failed", error=str(e), book_id=book_id)

    # Step 10: Record daily analytics (non-blocking)
    await _record_analytics(request, permit.tier, image_metrics, total_cost)

    # Increment usage ONLY after successful generation
    await increment_usage(uid)

    logger.info(
        "book_generation_complete", uid=uid, book_id=book_id, pdf_url=pdf_url,
        total_cost=round(total_cost, 6),
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


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, user: dict = Depends(get_current_user)):
    data = await firebase.get_book(book_id)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found")
    if data.get("uid") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your book")

    # Delete R2 assets (best-effort — don't fail the request if cleanup errors)
    try:
        await storage.delete_book_assets(book_id)
    except Exception as e:
        logger.warning("r2_cleanup_failed", book_id=book_id, error=str(e))

    await firebase.delete_book(book_id)
    return Response(status_code=204)


@router.get("/", response_model=list[BookResponse])
async def list_books(user: dict = Depends(get_current_user)):
    books = await firebase.get_user_books(user["uid"])
    return [BookResponse(**b) for b in books]
