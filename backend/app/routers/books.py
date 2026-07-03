from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import uuid
import tempfile
import os
import io
import zipfile
import httpx
import structlog
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.middleware.rate_limit import (
    GenerationPermit,
    check_rate_limit,
    increment_usage,
    release_quota_reservation,
)
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


class BulkDownloadRequest(BaseModel):
    book_ids: list[str]


def _owner_uid(data: dict) -> str | None:
    return data.get("uid") or data.get("user_id")


def _book_pdf_key(data: dict) -> str | None:
    return data.get("pdf_key") or storage.object_key_from_url(data.get("pdf_url"))


def _book_page_keys(data: dict) -> list[str]:
    if data.get("page_keys"):
        return [str(k) for k in data.get("page_keys", []) if k]
    return [
        key
        for key in (storage.object_key_from_url(url) for url in data.get("page_urls", []))
        if key
    ]


def _safe_pdf_filename(title: str, fallback: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_", " ") else "_" for ch in title)
    safe = "_".join(safe.split()).strip("_")
    return f"{safe or fallback}.pdf"


def _book_response_from_data(data: dict) -> BookResponse:
    pdf_key = _book_pdf_key(data)
    page_keys = _book_page_keys(data)
    pdf_url = (
        storage.generate_presigned_url(pdf_key, expiry_seconds=storage.PDF_URL_EXPIRY_SECONDS)
        if pdf_key else None
    )
    # Free-tier books are watermarked in the PDF. Do NOT hand back clean,
    # unwatermarked interior page images — that would let a free user strip the
    # watermark by pulling the raw PNGs. Only the watermarked PDF is exposed.
    if data.get("watermarked"):
        page_urls = []
    else:
        page_urls = [
            storage.generate_presigned_url(key, expiry_seconds=storage.IMAGE_URL_EXPIRY_SECONDS)
            for key in page_keys
        ]
    return BookResponse(
        book_id=data["book_id"],
        title=data["title"],
        status=data.get("status", "complete"),
        pdf_url=pdf_url,
        page_urls=page_urls,
        page_count=data.get("page_count", len(page_urls)),
        created_at=data["created_at"],
        theme=data["theme"],
        age_range=data["age_range"],
    )


@router.post("/download-zip")
async def download_books_zip(
    body: BulkDownloadRequest,
    user: dict = Depends(get_current_user),
):
    uid = user["uid"]
    stripe_info = await firebase.get_user_stripe_info(uid) or {}
    user_tier = stripe_info.get("subscription_tier", user.get("tier", "free"))
    subscription_active = stripe_info.get("subscription_active", False)
    if user_tier == "free" or not subscription_active:
        raise HTTPException(
            status_code=403,
            detail="Bulk download requires a paid plan",
        )
    if not body.book_ids:
        raise HTTPException(status_code=400, detail="No books selected")
    if len(body.book_ids) > 50:
        raise HTTPException(status_code=400, detail="Too many books selected")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        used_names: set[str] = set()
        for book_id in body.book_ids:
            data = await firebase.get_book(book_id)
            if not data:
                raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")
            if _owner_uid(data) != uid:
                raise HTTPException(status_code=403, detail="Access denied")
            pdf_key = _book_pdf_key(data)
            if not pdf_key:
                raise HTTPException(status_code=404, detail=f"PDF not available: {book_id}")

            filename = _safe_pdf_filename(data.get("title", ""), book_id)
            if filename in used_names:
                stem = filename.removesuffix(".pdf")
                filename = f"{stem}_{book_id[:8]}.pdf"
            used_names.add(filename)
            archive.writestr(filename, await storage.get_object_bytes(pdf_key))

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="tailormade-books.zip"'},
    )


def _signed_character_reference(character: dict) -> str | None:
    for key_field, url_field in (("sketch_key", "sketch_url"), ("original_key", "original_url")):
        object_key = character.get(key_field) or storage.object_key_from_url(character.get(url_field))
        if object_key:
            return storage.generate_presigned_url(
                object_key,
                expiry_seconds=storage.IMAGE_URL_EXPIRY_SECONDS,
            )
    return None


async def _record_failed_book(book_id: str, uid: str, request: BookRequest, error: str) -> None:
    """Save a failed book record to Firestore. Never raises."""
    try:
        await firebase.save_book(book_id, {
            "book_id": book_id,
            "uid": uid,
            "user_id": uid,
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
    user_email = user.get("email")
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

    try:
        return await _generate_book_after_reservation(
            request,
            uid,
            user_email,
            tier,
            book_id,
            permit,
        )
    except HTTPException as e:
        await release_quota_reservation(uid, permit)
        if e.status_code >= 500:
            raise HTTPException(
                status_code=500,
                detail="Generation failed. Your credit has been returned.",
            ) from e
        raise
    except Exception as e:
        await release_quota_reservation(uid, permit)
        logger.error("generation_pipeline_unhandled", uid=uid, book_id=book_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Generation failed. Your credit has been returned.",
        ) from e


async def _generate_book_after_reservation(
    request: BookRequest,
    uid: str,
    user_email: str | None,
    tier: str,
    book_id: str,
    permit: GenerationPermit,
) -> BookResponse:
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

    # Step 2b: Fetch the user's most recent character for visual reference.
    # Failure here must not block generation — books work fine without a reference.
    character_image_url: str | None = None
    try:
        characters = await firebase.get_user_characters(uid, limit=1)
        if characters:
            char = characters[0]
            character_image_url = _signed_character_reference(char)
            logger.info("character_reference_attached",
                        uid=uid, book_id=book_id,
                        character_id=char.get("character_id"),
                        has_url=bool(character_image_url))
    except Exception as e:
        logger.warning("character_fetch_failed_for_book",
                       uid=uid, book_id=book_id, error=str(e))
        character_image_url = None

    # Step 3: Image generation (all scenes including cover hero)
    try:
        image_results, image_metrics = await image_gen.generate_images(
            scenes,
            character_image_url=character_image_url,
            age_range=request.age_range,
            user_tier=permit.tier,
        )
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
        cover_hero_key = await storage.upload_image(cover_hero_bytes, book_id, 0)
        logger.info("cover_hero_uploaded", book_id=book_id, key=cover_hero_key)
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
    page_keys = []
    for i, img_bytes in enumerate(processed_bytes):
        key = await storage.upload_image(img_bytes, book_id, i + 1)
        page_keys.append(key)

    page_signed_urls = [
        storage.generate_presigned_url(key, expiry_seconds=storage.IMAGE_URL_EXPIRY_SECONDS)
        for key in page_keys
    ]

    # Step 7: Build PDF (cover hero + clean image-only coloring pages)
    logger.info("pdf_build_cover_debug",
               cover_hero_local_path=cover_hero_local_path,
               cover_hero_file_exists=os.path.exists(cover_hero_local_path) if cover_hero_local_path else False)
    try:
        pdf_bytes = await pdf_builder.build_pdf(
            book_id=book_id,
            title=request.title,
            page_image_urls=page_signed_urls,
            age_range=request.age_range,
            theme=request.theme,
            cover_hero_path=cover_hero_local_path,
            user_tier=permit.tier,
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
    pdf_key = await storage.upload_pdf(pdf_bytes, book_id)
    pdf_url = storage.generate_presigned_url(
        pdf_key,
        expiry_seconds=storage.PDF_URL_EXPIRY_SECONDS,
    )

    # Step 8: Save to Firestore
    book_data = {
        "book_id": book_id,
        "uid": uid,
        "user_id": uid,
        "title": request.title,
        "theme": request.theme,
        "age_range": request.age_range,
        "page_count": len(page_keys),
        "page_keys": page_keys,
        "pdf_key": pdf_key,
        "status": "complete",
        "watermarked": permit.tier == "free",
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
    await increment_usage(uid, permit)

    # Non-fatal: email failure never blocks book delivery
    try:
        from app.services.email import send_book_ready

        child_name = next(
            (name.strip() for name in request.character_names or [] if name and name.strip()),
            "your child",
        )
        send_book_ready(
            to_email=user_email or "",
            child_name=child_name,
            download_url=f"https://tailormadecoloringbook.app/books/{book_id}",
        )
    except Exception as e:
        logger.warning("book_ready_email_failed_non_fatal", book_id=book_id, error=str(e))

    logger.info(
        "book_generation_complete", uid=uid, book_id=book_id, pdf_key=pdf_key,
        total_cost=round(total_cost, 6),
    )

    # Free-tier books only expose the watermarked PDF, never the clean page PNGs.
    response_page_urls = [] if permit.tier == "free" else page_signed_urls

    return BookResponse(
        book_id=book_id,
        title=request.title,
        status="complete",
        pdf_url=pdf_url,
        page_urls=response_page_urls,
        page_count=len(page_keys),
        created_at=datetime.now(timezone.utc),
        theme=request.theme,
        age_range=request.age_range,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, user: dict = Depends(get_current_user)):
    data = await firebase.get_book(book_id)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found")
    if _owner_uid(data) != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your book")
    return _book_response_from_data(data)


@router.get("/{book_id}/download")
async def get_book_download_url(book_id: str, user: dict = Depends(get_current_user)):
    data = await firebase.get_book(book_id)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found")
    if _owner_uid(data) != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")
    pdf_key = _book_pdf_key(data)
    if not pdf_key:
        raise HTTPException(status_code=404, detail="PDF not available")
    signed_url = storage.generate_presigned_url(
        pdf_key,
        expiry_seconds=storage.PDF_URL_EXPIRY_SECONDS,
    )
    return {"download_url": signed_url, "expires_in": storage.PDF_URL_EXPIRY_SECONDS}


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, user: dict = Depends(get_current_user)):
    data = await firebase.get_book(book_id)
    if not data:
        raise HTTPException(status_code=404, detail="Book not found")
    if _owner_uid(data) != user["uid"]:
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
    return [_book_response_from_data(b) for b in books]
