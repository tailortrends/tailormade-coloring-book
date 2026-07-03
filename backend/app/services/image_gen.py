"""
Image generation via fal.ai FLUX.1 Kontext [pro].

Kontext produces high-quality coloring book line art from natural-language
prompts and an optional character reference image — no LoRA required.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import httpx
import fal_client
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import structlog
import logging
from app.config import get_settings
from app.models.book import Scene

logger = structlog.get_logger()
settings = get_settings()

_semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

os.environ["FAL_KEY"] = settings.fal_key

KONTEXT_MODEL = "fal-ai/flux-pro/kontext"
KONTEXT_TEXT_MODEL = "fal-ai/flux-pro/kontext/text-to-image"

# By default fal keeps its own copy of generated media on its public CDN
# (unguessable URL) for ~7 days. We download every image into our own R2 storage
# within the same request, so fal's copy is redundant almost immediately. Ask fal
# to expire its copy quickly to minimize how long generated children's content
# lives on a third-party public URL. The fal SDK forwards this per-request
# `headers` dict onto the outgoing run request (see fal_client.SyncClient.run).
FAL_OUTPUT_LIFECYCLE_HEADER = "X-Fal-Object-Lifecycle-Preference"
FAL_REQUEST_HEADERS: dict[str, str] = {
    FAL_OUTPUT_LIFECYCLE_HEADER: json.dumps({"expiration_duration_seconds": 3600}),
}

# ─── Prompt templates ────────────────────────────────────────────────────────

# Maps age_range (BookRequest pattern) → complexity modifier text
AGE_RANGE_MODIFIERS: dict[str, str] = {
    "2-4": "very simple bold shapes, large coloring areas, minimal detail, thick lines",
    "4-6": "simple friendly detail, clear regions, medium line weight",
    "6-9": "moderate detail, varied line weight, more complex composition",
    "9-12": "intricate detail, fine linework, complex adult coloring book style",
}

# Maps Scene.complexity → complexity modifier text (fallback when age_range not provided)
COMPLEXITY_MODIFIERS: dict[str, str] = {
    "simple": "very simple bold shapes, large coloring areas, minimal detail, thick lines",
    "beginner": "simple friendly detail, clear regions, medium line weight",
    "medium": "moderate detail, varied line weight, more complex composition",
    "advanced": "intricate detail, fine linework, complex adult coloring book style",
}

NEGATIVE_PROMPT = (
    "color, colorful, shading, gradients, watercolor, painting, photograph, "
    "realistic, 3d render, filled areas, gray fill, dark background, "
    "blur, noise, text, watermark, signature, border, frame"
)


@dataclass
class ImageResult:
    page_number: int
    image_url: str
    image_bytes: Optional[bytes] = None
    success: bool = True
    error: Optional[str] = None
    fal_attempts: int = 1
    from_library: bool = False


@dataclass
class ImageGenMetrics:
    total_attempts: int = 0
    total_image_spend: float = 0.0
    library_hits: int = 0
    library_misses: int = 0


def _scene_description(scene: Scene) -> str:
    """Compose a natural-language scene description from the 4-layer Scene model."""
    subject = (scene.main_subject or scene.subject_hint).replace("_", " ")
    parts = [subject]

    if scene.composition == "close-up":
        parts.append("close-up portrait view")
    elif scene.composition == "wide-scene":
        parts.append("wide panoramic view")
    elif scene.composition == "action-pose":
        parts.append("dynamic action pose")
    else:
        parts.append("full body view")

    if scene.secondary_elements:
        secondary = ", ".join(scene.secondary_elements[:4])
        parts.append(f"with {secondary}")

    if scene.background:
        parts.append(f"in {scene.background}")
    if scene.foreground:
        parts.append(f"with {scene.foreground} in the foreground")

    if scene.is_cover:
        parts.append("with open space in the top center for a title")

    return ", ".join(parts)


def _resolve_age_modifier(age_range: Optional[str], complexity: Optional[str]) -> str:
    if age_range and age_range in AGE_RANGE_MODIFIERS:
        return AGE_RANGE_MODIFIERS[age_range]
    if complexity and complexity in COMPLEXITY_MODIFIERS:
        return COMPLEXITY_MODIFIERS[complexity]
    return COMPLEXITY_MODIFIERS["medium"]


def _build_prompt(scene: Scene, age_range: Optional[str] = None) -> str:
    scene_desc = _scene_description(scene)
    age_mod = _resolve_age_modifier(age_range, scene.complexity)

    return (
        "Black and white coloring book page, clean thick outlines only, "
        "pure white background, no shading no gray no color fill, "
        f"{scene_desc}, {age_mod}, "
        "children's illustration style, printable line art"
    )


# ─── fal.ai call ─────────────────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def _call_kontext(
    prompt: str,
    page_number: int,
    character_image_url: Optional[str] = None,
    aspect_ratio: str = "3:4",
) -> tuple[str, dict]:
    """Single Kontext call. Returns (image_url, raw_result)."""
    has_ref = bool(character_image_url)
    endpoint = KONTEXT_MODEL if has_ref else KONTEXT_TEXT_MODEL

    arguments: dict = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "guidance_scale": 3.5,
        "num_inference_steps": 28,
        "num_images": 1,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
    }
    if has_ref:
        arguments["image_url"] = character_image_url

    logger.info("kontext_call_start", page=page_number, endpoint=endpoint,
                has_ref=has_ref, prompt_preview=prompt[:120],
                negative_prompt=NEGATIVE_PROMPT)
    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(endpoint, arguments=arguments, headers=FAL_REQUEST_HEADERS),
            ),
            timeout=120.0,
        )
        image_url = result["images"][0]["url"]
        logger.info("kontext_call_success", page=page_number)
        return image_url, result
    except asyncio.TimeoutError:
        logger.error("kontext_call_timeout", page=page_number)
        raise
    except Exception as e:
        logger.error("kontext_call_error", page=page_number, error=str(e))
        raise


# ─── Image validation ────────────────────────────────────────────────────────

# Hard-retry only on completely solid images (Kontext is reliable enough that
# softer quality issues are not worth the extra cost of retries).
HARD_FAIL_BLANK_THRESHOLD = 0.005   # < 0.5% black pixels = effectively all white
HARD_FAIL_DENSE_THRESHOLD = 0.85    # > 85% black pixels = effectively all black
MAX_MID_GRAY_RATIO = 0.30           # > 30% mid-gray suggests color/shading survived


def validate_is_line_art(image_path: str) -> bool:
    """
    Returns True if image looks like line art (mostly white with dark lines).
    Rejects if more than 30% of pixels are mid-gray.
    """
    from PIL import Image
    import numpy as np

    img = Image.open(image_path).convert("L")
    arr = np.array(img)
    mid_gray = np.sum((arr > 50) & (arr < 220))
    total = arr.size
    gray_ratio = mid_gray / total
    return bool(gray_ratio < MAX_MID_GRAY_RATIO)


def _is_valid_image(image_bytes: bytes, page_number: int, raw_result: Optional[dict] = None) -> tuple[bool, str]:
    """Lightweight validation. Returns (is_valid, fail_reason).

    Hard-retry only on: completely black, completely white, or NSFW flag.
    """
    from PIL import Image
    import io
    import numpy as np

    if raw_result and raw_result.get("has_nsfw_concepts"):
        flags = raw_result.get("has_nsfw_concepts", [])
        if any(flags):
            logger.warning("image_rejected_nsfw", page=page_number)
            return False, "nsfw"

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        gray = np.array(img)
        black_ratio = np.sum(gray < 50) / gray.size
        mid_gray_ratio = np.sum((gray > 50) & (gray < 220)) / gray.size

        if black_ratio < HARD_FAIL_BLANK_THRESHOLD:
            logger.warning("image_rejected_blank",
                           page=page_number, black_ratio=round(black_ratio, 4))
            return False, "blank"
        if black_ratio > HARD_FAIL_DENSE_THRESHOLD:
            logger.warning("image_rejected_all_black",
                           page=page_number, black_ratio=round(black_ratio, 4))
            return False, "all_black"
        if mid_gray_ratio > MAX_MID_GRAY_RATIO:
            logger.warning("image_rejected_mid_gray",
                           page=page_number,
                           mid_gray_ratio=round(mid_gray_ratio, 4))
            return False, "mid_gray"

        logger.info("image_quality_passed",
                    page=page_number,
                    black_ratio=round(black_ratio, 3),
                    mid_gray_ratio=round(mid_gray_ratio, 3))
        return True, "pass"

    except Exception as e:
        logger.error("image_validation_error", page=page_number, error=str(e))
        return False, "error"


# ─── Generation orchestration ────────────────────────────────────────────────

async def _generate_one(
    scene: Scene,
    semaphore: asyncio.Semaphore,
    use_library: bool = True,
    character_image_url: Optional[str] = None,
    age_range: Optional[str] = None,
    user_tier: str = "free",
) -> ImageResult:
    """Generate one page image. Library cache is checked first."""
    if use_library and not scene.is_cover:
        from app.services.library_cache import find_match
        library_url = await find_match(
            theme=scene.theme,
            subject_hint=scene.subject_hint,
            complexity=scene.complexity,
        )
        if library_url:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(library_url)
                    resp.raise_for_status()
                    img_bytes = resp.content
                logger.info("library_image_used",
                            page=scene.page_number,
                            subject=scene.subject_hint)
                return ImageResult(
                    page_number=scene.page_number,
                    image_url=library_url,
                    image_bytes=img_bytes,
                    success=True,
                    fal_attempts=0,
                    from_library=True,
                )
            except Exception as e:
                logger.warning("library_image_download_failed",
                               page=scene.page_number,
                               error=str(e))

    async with semaphore:
        last_result = None
        fal_calls = 0
        prompt = _build_prompt(scene, age_range=age_range)

        for attempt in range(2):
            try:
                fal_calls += 1
                if user_tier == "free":
                    logger.info("free_tier_generation_deprioritized",
                                page=scene.page_number,
                                hour=datetime.now().hour)
                    await asyncio.sleep(2)
                image_url, raw_result = await _call_kontext(
                    prompt,
                    scene.page_number,
                    character_image_url=character_image_url,
                )

                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(image_url)
                    img_bytes = resp.content

                is_valid, fail_reason = _is_valid_image(img_bytes, scene.page_number, raw_result)
                if is_valid:
                    return ImageResult(
                        page_number=scene.page_number,
                        image_url=image_url,
                        image_bytes=img_bytes,
                        success=True,
                        fal_attempts=fal_calls,
                    )

                logger.warning("image_quality_failed",
                               page=scene.page_number, attempt=attempt + 1,
                               reason=fail_reason)
                last_result = ImageResult(
                    page_number=scene.page_number,
                    image_url=image_url,
                    image_bytes=img_bytes,
                    success=scene.is_cover,
                    fal_attempts=fal_calls,
                    error=fail_reason,
                )

            except Exception as e:
                logger.error("kontext_exception",
                             page=scene.page_number, attempt=attempt + 1, error=str(e))

        logger.warning("image_quality_all_attempts_failed", page=scene.page_number)
        if last_result:
            last_result.fal_attempts = fal_calls
            return last_result
        return ImageResult(
            page_number=scene.page_number,
            image_url="",
            success=False,
            error="All generation attempts failed",
            fal_attempts=fal_calls,
        )


async def generate_page_image(
    scene: Scene,
    age_range: Optional[str] = None,
    character_image_url: Optional[str] = None,
    user_tier: str = "free",
) -> str:
    """Generate a single coloring book page and return its image URL.

    Convenience wrapper around _generate_one for callers that just need a URL.
    """
    result = await _generate_one(
        scene,
        _semaphore,
        use_library=False,
        character_image_url=character_image_url,
        age_range=age_range,
        user_tier=user_tier,
    )
    if not result.success or not result.image_url:
        raise RuntimeError(f"Image generation failed: {result.error}")
    return result.image_url


async def generate_images(
    scenes: list[Scene],
    character_image_url: Optional[str] = None,
    age_range: Optional[str] = None,
    user_tier: str = "free",
) -> tuple[list[ImageResult], ImageGenMetrics]:
    """Fire all image generation calls concurrently."""
    logger.info("image_gen_start", page_count=len(scenes),
                has_character=bool(character_image_url),
                user_tier=user_tier)

    from app.services.library_cache import load_library_index
    await load_library_index()

    results = await asyncio.gather(
        *[
            _generate_one(
                scene,
                _semaphore,
                character_image_url=character_image_url,
                age_range=age_range,
                user_tier=user_tier,
            )
            for scene in scenes
        ]
    )

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    library_hits = sum(1 for r in results if r.from_library)
    library_misses = sum(1 for r in results if not r.from_library)
    total_attempts = sum(r.fal_attempts for r in results)
    total_image_spend = total_attempts * settings.cost_flux_lora
    metrics = ImageGenMetrics(
        total_attempts=total_attempts,
        total_image_spend=total_image_spend,
        library_hits=library_hits,
        library_misses=library_misses,
    )

    logger.info(
        "image_gen_complete",
        total=len(scenes),
        successful=len(successful),
        failed=len(failed),
        library_hits=library_hits,
        library_misses=library_misses,
        fal_attempts=total_attempts,
        image_spend=round(total_image_spend, 4),
    )

    if len(failed) > len(scenes) // 2:
        raise RuntimeError(
            f"Too many image generation failures: {len(failed)}/{len(scenes)}"
        )

    return list(results), metrics


async def post_process_image(image_bytes: bytes) -> bytes:
    """No-op — Kontext produces correct B&W line art. Kept for API compatibility."""
    return image_bytes


# ─── Cover background image generation ───────────────────────────────────────

COVER_SUBJECTS = {
    "ocean": ["starfish", "seashell", "small fish", "coral", "sea bubble", "anchor"],
    "space": ["star", "small planet", "rocket", "moon crescent", "comet", "asteroid"],
    "dinosaur": ["dinosaur egg", "small footprint", "leaf", "bone", "fern", "small dino"],
    "fantasy": ["small star", "magic wand", "fairy wing", "flower", "butterfly", "gem"],
    "animals": ["paw print", "butterfly", "small bird", "flower", "leaf", "acorn"],
    "vehicles": ["small car", "wheel", "road sign", "cloud", "traffic cone", "bolt"],
    "nature": ["flower", "leaf", "acorn", "mushroom", "raindrop", "sun ray"],
}


async def generate_cover_bg_image(subject: str, theme: str) -> str:
    """Generate a small decorative image for cover background.

    Returns the local temp file path of the saved PNG.
    """
    prompt = (
        "Black and white coloring book page, clean thick outlines only, "
        "pure white background, no shading no gray no color fill, "
        f"a single {subject}, centered, simple cute illustration, "
        "very simple bold shapes, minimal detail, thick lines, "
        "children's illustration style, printable line art"
    )

    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    KONTEXT_TEXT_MODEL,
                    arguments={
                        "prompt": prompt,
                        "negative_prompt": NEGATIVE_PROMPT,
                        "guidance_scale": 3.5,
                        "num_inference_steps": 28,
                        "num_images": 1,
                        "aspect_ratio": "1:1",
                        "output_format": "png",
                    },
                    headers=FAL_REQUEST_HEADERS,
                ),
            ),
            timeout=90.0,
        )

        image_url = result["images"][0]["url"]

        import tempfile
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()

        tmp = tempfile.NamedTemporaryFile(
            prefix=f"cover_bg_{subject.replace(' ', '_')}_",
            suffix=".png",
            delete=False,
        )
        tmp.write(resp.content)
        tmp.close()

        logger.info("cover_bg_generated", subject=subject, path=tmp.name,
                    negative_prompt=NEGATIVE_PROMPT)
        return tmp.name

    except Exception as e:
        logger.error("cover_bg_generation_failed", subject=subject, error=str(e))
        raise


async def generate_character_sketch(photo_url: str) -> str:
    """Convert a user-uploaded photo into a coloring-book character sketch via Kontext.

    Returns the fal.media image URL of the generated sketch.
    """
    prompt = (
        "Convert this photo into a black and white coloring book character "
        "illustration. Clean thick outlines only, pure white background, "
        "no shading, no gray, no color. Friendly children's coloring book "
        "style. Preserve the character's key features and likeness."
    )
    logger.info("character_sketch_start", has_photo=bool(photo_url))
    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    KONTEXT_MODEL,
                    arguments={
                        "prompt": prompt,
                        "image_url": photo_url,
                        "negative_prompt": NEGATIVE_PROMPT,
                        "guidance_scale": 3.5,
                        "num_inference_steps": 28,
                        "num_images": 1,
                        "output_format": "png",
                    },
                    headers=FAL_REQUEST_HEADERS,
                ),
            ),
            timeout=120.0,
        )
        image_url = result["images"][0]["url"]
        logger.info("character_sketch_success")
        return image_url
    except Exception as e:
        logger.error("character_sketch_failed", error=str(e))
        raise


# ─── Self-test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import io
    from PIL import Image as PILImage
    import PIL.ImageDraw as ImageDraw

    def _make_png(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    blank = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
    result, reason = _is_valid_image(_make_png(blank), page_number=901)
    assert result is False and reason == "blank", f"blank should fail, got {reason}"
    print(f"Test 1 PASS: blank rejected ({reason})")

    line = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(line)
    for i in range(0, 200, 12):
        draw.line([(i, 0), (i, 200)], fill=(0, 0, 0), width=2)
        draw.line([(0, i), (200, i)], fill=(0, 0, 0), width=2)
    result, reason = _is_valid_image(_make_png(line), page_number=902)
    assert result is True, f"line art should pass, got {reason}"
    print("Test 2 PASS: line art accepted")

    print("All tests passed")
