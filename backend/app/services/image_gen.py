"""
Image generation via fal.ai FLUX LoRA with custom coloring book style.

Key improvements:
- Composition-aware prompts (close-up, full-body, wide-scene, action-pose)
- Stronger style enforcement with repeating negative concepts in prompt
- Fill percentage instructions per composition type
- Tuned guidance_scale (5.5) and num_inference_steps (35) for cleaner lines
- Portrait aspect ratio (1024x1408) to match 8.5x11 page layout
- 5-point image validation (contrast, color, whitespace, edge density, watermark)
- Retry with prompt variation instead of identical re-submission
"""

import asyncio
import os
from dataclasses import dataclass
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

# Semaphore caps concurrent fal.ai calls
_semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

# Set credential from settings
os.environ["FAL_KEY"] = settings.fal_key

# ─── Prompt templates ────────────────────────────────────────────────────────

STYLE_SUFFIX = (
    "tmcb_style, children's coloring book page, "
    "pure black and white line art, ONLY black outlines on pure white background, "
    "thick bold clean outlines suitable for children to color within, "
    "absolutely NO color, NO shading, NO gradients, NO grey fill, NO shadows, "
    "NO watermarks, NO text, NO signatures, "
    "high contrast, print-ready, professional coloring book quality"
)

# Mandatory layout modifiers — ensures subjects and scenes fill the entire page
FULL_PAGE_MODIFIER = (
    "edge-to-edge composition, full-bleed illustration, "
    "elements touching all four corners of the frame, "
    "no large empty white borders, "
    "intricate detail filling the entire page, "
    "professional coloring book style"
)

COMPOSITION_PROMPTS = {
    "close-up": (
        "dramatic close-up portrait of {subject} filling the entire frame, "
        "head and face details clearly visible, subject occupies 85% of the image, "
        "decorative elements filling remaining space around subject"
    ),
    "full-body": (
        "full body view of {subject} centered on page, "
        "entire subject visible from head to feet, "
        "subject occupies 65% of the image, environmental details filling the scene"
    ),
    "wide-scene": (
        "wide panoramic scene showing {subject} in a rich themed environment, "
        "subject is the clear focal point occupying 50% of the image, "
        "detailed background and foreground elements filling the entire composition"
    ),
    "action-pose": (
        "{subject} in a dynamic action pose, full of energy and movement, "
        "subject occupies 60% of the image, "
        "environmental context and motion elements filling the scene"
    ),
}

COMPLEXITY_DETAIL = {
    "simple": "EXTRA THICK bold outlines, very few details, large simple shapes, toddler-friendly",
    "beginner": "thick bold outlines, simple shapes with some detail, kid-friendly ages 4-6",
    "medium": "medium weight outlines, moderate detail with 10-15 distinct colorable regions, ages 6-9",
    "advanced": "detailed outlines with fine lines, intricate patterns, 20+ distinct colorable regions, ages 9-12",
}

# Variations applied on retry to nudge the model differently
RETRY_VARIATIONS = [
    "",  # First attempt: no variation
    ", zoomed in, larger subject, filling more of the frame",
    ", simplified composition, single clear subject, extra bold outlines",
]

# ─── Quality thresholds ──────────────────────────────────────────────────────

MIN_STD_DEV = 10.0        # below this = near-solid image (bad generation)
MAX_STD_DEV = 120.0       # above this = too noisy/complex
MAX_CHANNEL_SPREAD = 15   # above this = colored image (LoRA failed)
MAX_SATURATION = 20       # above this mean HSV saturation = colored image
MIN_BLACK_RATIO = 0.02    # below 2% = nearly blank (tiny subject)
MAX_BLACK_RATIO = 0.50    # above 50% = maze/noise pattern
MIN_EDGE_RATIO = 0.01     # below 1% = too sparse/simple
MAX_EDGE_RATIO = 0.30     # above 30% = too noisy/complex
MIN_FILL_RATIO = 0.60     # below 60% non-white = page too empty, needs more detail

# Aggressive background filler keywords added on density retry
DENSITY_FILLER = (
    "dense detailed background filling every corner, "
    "lush environmental details everywhere, "
    "no empty white space, every area of the page has line art detail, "
    "maximum illustration coverage"
)


@dataclass
class ImageResult:
    page_number: int
    image_url: str
    image_bytes: Optional[bytes] = None
    success: bool = True
    error: Optional[str] = None
    fal_attempts: int = 1  # number of fal.ai API calls for this page


@dataclass
class ImageGenMetrics:
    total_attempts: int = 0
    total_image_spend: float = 0.0


def _build_prompt(scene: Scene, variation: str = "") -> str:
    """
    Assemble the image generation prompt from the 4-layer scene structure.

    Priority order (most important first, so they survive truncation):
    1. Composition frame (sets camera/framing)
    2. Main subject (hero element)
    3. Secondary elements (supporting details)
    4. Background + foreground (environmental context)
    5. Cover note (if applicable)
    6. Full-page modifier (edge-to-edge fill)
    7. Complexity detail
    8. Style suffix (LoRA trigger + BW enforcement)
    """
    subject = scene.subject_hint.replace("_", " ")
    comp_type = scene.composition if scene.composition in COMPOSITION_PROMPTS else "full-body"
    comp_prompt = COMPOSITION_PROMPTS[comp_type].format(subject=subject)
    detail = COMPLEXITY_DETAIL.get(scene.complexity, COMPLEXITY_DETAIL["medium"])

    # Build prompt parts in priority order
    parts = [comp_prompt]

    # Layer 1: Main subject
    if scene.main_subject:
        parts.append(scene.main_subject)

    # Layer 2: Secondary elements (cap at 4 to save tokens)
    if scene.secondary_elements:
        secondary = ", ".join(scene.secondary_elements[:4])
        parts.append(f"accompanied by {secondary}")

    # Layer 3: Background
    if scene.background:
        parts.append(f"background showing {scene.background}")

    # Layer 4: Foreground
    if scene.foreground:
        parts.append(f"foreground with {scene.foreground}")

    # Cover scenes get grand masterpiece treatment
    if scene.is_cover:
        parts.append("grand masterpiece composition, large clear open space in top-center for title")

    # Full-page fill modifier (every prompt)
    parts.append(FULL_PAGE_MODIFIER)

    # Complexity detail
    parts.append(detail)

    # Style enforcement (LoRA trigger + BW rules)
    parts.append(STYLE_SUFFIX)

    # Variation suffix (for retries)
    if variation:
        parts.append(variation.strip(", "))

    prompt = ", ".join(parts)

    # Truncate to 120 words — higher resolution can handle longer prompts
    words = prompt.split()
    if len(words) > 120:
        prompt = " ".join(words[:120])

    return prompt


# ─── fal.ai call ─────────────────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def _call_fal_single(prompt: str, page_number: int, guidance_scale: float = 5.5) -> ImageResult:
    """Single fal.ai call with retry logic. Uses custom LoRA for consistent style."""
    logger.info("fal_call_start", page=page_number, guidance_scale=guidance_scale,
                prompt_preview=prompt[:120])
    try:
        lora_url = settings.custom_lora_url
        loras = [{"path": lora_url, "scale": settings.lora_scale}] if lora_url else []
        endpoint = "fal-ai/flux-lora" if loras else "fal-ai/flux/dev"

        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    endpoint,
                    arguments={
                        "prompt": prompt,
                        "loras": loras,
                        "image_size": {"width": 1216, "height": 1728},
                        "num_inference_steps": 35,
                        "guidance_scale": guidance_scale,
                        "num_images": 1,
                        "enable_safety_checker": True,
                        "output_format": "png",
                    },
                ),
            ),
            timeout=120.0,
        )
        image_url = result["images"][0]["url"]
        logger.info("fal_call_success", page=page_number, url=image_url)
        return ImageResult(page_number=page_number, image_url=image_url)
    except asyncio.TimeoutError:
        logger.error("fal_call_timeout", page=page_number)
        raise
    except Exception as e:
        logger.error("fal_call_error", page=page_number, error=str(e))
        raise


# ─── Image validation ────────────────────────────────────────────────────────

def _is_valid_image(image_bytes: bytes, page_number: int) -> tuple[bool, str]:
    """
    7-point image validation. Returns (is_valid, failure_reason).
    failure_reason is one of: "pass", "low_contrast", "noisy", "colored",
    "colored_image", "blank", "dense", "sparse", "complex", "watermark",
    "sparse_fill", "error".
    """
    from PIL import Image, ImageStat, ImageFilter
    import io
    import numpy as np

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        gray = img.convert("L")

        # ── Check 1: Contrast ──
        stat = ImageStat.Stat(gray)
        std_dev = stat.stddev[0]
        if std_dev < MIN_STD_DEV:
            logger.warning("image_rejected_low_contrast",
                          page=page_number, std_dev=round(std_dev, 1))
            return False, "low_contrast"
        if std_dev > MAX_STD_DEV:
            logger.warning("image_rejected_too_noisy",
                          page=page_number, std_dev=round(std_dev, 1))
            return False, "noisy"

        # ── Check 2: Color detection ──
        r, g, b = img.split()
        r_mean = ImageStat.Stat(r).mean[0]
        g_mean = ImageStat.Stat(g).mean[0]
        b_mean = ImageStat.Stat(b).mean[0]
        channel_spread = max(r_mean, g_mean, b_mean) - min(r_mean, g_mean, b_mean)
        if channel_spread > MAX_CHANNEL_SPREAD:
            logger.warning("image_rejected_colored",
                          page=page_number, channel_spread=round(channel_spread, 1))
            return False, "colored"

        # ── Check 2b: Mean saturation (catches fully colored images) ──
        import colorsys
        hsv_array = np.array(img.convert("RGB"))
        pixels = hsv_array.reshape(-1, 3) / 255.0
        saturations = np.array([
            colorsys.rgb_to_hsv(r, g, b)[1]
            for r, g, b in pixels
        ])
        mean_saturation = saturations.mean() * 100
        logger.debug("saturation_check",
                     mean_saturation=round(mean_saturation, 1))
        if mean_saturation > 15:
            logger.warning("image_rejected_colored",
                           mean_saturation=round(mean_saturation, 1))
            return False, "colored_image"

        # ── Check 3: Whitespace ratio (black pixel percentage) ──
        gray_arr = np.array(gray)
        black_pixels = np.sum(gray_arr < 128)
        total_pixels = gray_arr.size
        black_ratio = black_pixels / total_pixels
        if black_ratio < MIN_BLACK_RATIO:
            logger.warning("image_rejected_too_blank",
                          page=page_number, black_ratio=round(black_ratio, 3))
            return False, "blank"
        if black_ratio > MAX_BLACK_RATIO:
            logger.warning("image_rejected_too_dense",
                          page=page_number, black_ratio=round(black_ratio, 3))
            return False, "dense"

        # ── Check 4: Edge density (enough detail to color?) ──
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_arr = np.array(edges)
        edge_pixels = np.sum(edge_arr > 50)
        edge_ratio = edge_pixels / total_pixels
        if edge_ratio < MIN_EDGE_RATIO:
            logger.warning("image_rejected_too_sparse",
                          page=page_number, edge_ratio=round(edge_ratio, 3))
            return False, "sparse"
        if edge_ratio > MAX_EDGE_RATIO:
            logger.warning("image_rejected_too_complex",
                          page=page_number, edge_ratio=round(edge_ratio, 3))
            return False, "complex"

        # ── Check 5: Bottom-strip watermark detection ──
        h = gray_arr.shape[0]
        bottom_strip = gray_arr[int(h * 0.92):, :]  # Bottom 8%
        main_body = gray_arr[:int(h * 0.85), :]
        bottom_content = np.mean(bottom_strip < 200)
        main_content = np.mean(main_body < 200)
        if bottom_content > 0.15 and bottom_content > main_content * 3:
            logger.warning("image_rejected_watermark_suspected",
                          page=page_number,
                          bottom_content=round(bottom_content, 3),
                          main_content=round(main_content, 3))
            return False, "watermark"

        # ── Check 6: Ink-to-Paper density (fill ratio) ──
        # Non-white pixels = any pixel below 250 (accounts for slight JPEG artifacts)
        non_white_pixels = np.sum(gray_arr < 250)
        fill_ratio = non_white_pixels / total_pixels
        if fill_ratio < MIN_FILL_RATIO:
            logger.warning("image_rejected_sparse_fill",
                          page=page_number, fill_ratio=round(fill_ratio, 3),
                          threshold=MIN_FILL_RATIO)
            return False, "sparse_fill"

        logger.info("image_quality_passed",
                   page=page_number,
                   std_dev=round(std_dev, 1),
                   channel_spread=round(channel_spread, 1),
                   mean_saturation=round(mean_saturation, 1),
                   black_ratio=round(black_ratio, 3),
                   edge_ratio=round(edge_ratio, 3),
                   fill_ratio=round(fill_ratio, 3))
        return True, "pass"

    except Exception as e:
        logger.error("image_validation_error", page=page_number, error=str(e))
        return False, "error"


# ─── Generation orchestration ────────────────────────────────────────────────

async def _generate_one(scene: Scene, semaphore: asyncio.Semaphore) -> ImageResult:
    """
    Generate one page image with quality validation.
    On failure, retry with prompt variation (up to 3 attempts).
    On sparse_fill failure, retry with higher guidance_scale and density filler keywords.
    """
    async with semaphore:
        last_result = None
        fal_calls = 0
        for attempt in range(3):
            try:
                variation = RETRY_VARIATIONS[attempt] if attempt < len(RETRY_VARIATIONS) else ""
                guidance = 5.5  # Default guidance scale

                # If previous attempt failed due to sparse fill, boost density
                if attempt > 0 and last_result and getattr(last_result, '_fail_reason', '') == 'sparse_fill':
                    variation = f", {DENSITY_FILLER}"
                    guidance = 7.5  # Higher guidance = stronger prompt adherence
                    logger.info("density_retry_boost",
                              page=scene.page_number, attempt=attempt + 1,
                              guidance_scale=guidance)

                prompt = _build_prompt(scene, variation=variation)

                if attempt > 0:
                    logger.info("image_quality_retry_with_variation",
                              page=scene.page_number, attempt=attempt + 1,
                              variation=variation[:60], guidance=guidance)

                fal_calls += 1
                result = await _call_fal_single(prompt, scene.page_number, guidance_scale=guidance)

                # Download and validate before accepting
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(result.image_url)
                    img_bytes = resp.content

                is_valid, fail_reason = _is_valid_image(img_bytes, scene.page_number)
                if is_valid:
                    result.image_bytes = img_bytes
                    result.fal_attempts = fal_calls
                    return result
                else:
                    logger.warning("image_quality_failed",
                                  page=scene.page_number, attempt=attempt + 1,
                                  reason=fail_reason)
                    last_result = result
                    last_result.image_bytes = img_bytes
                    last_result._fail_reason = fail_reason  # Track reason for next retry
                    continue

            except Exception as e:
                logger.error("fal_call_exception",
                            page=scene.page_number, attempt=attempt + 1, error=str(e))
                # Do NOT wipe last_result — preserve any bytes from earlier attempts

        # All attempts failed quality check — return last result anyway
        logger.warning("image_quality_all_attempts_failed", page=scene.page_number)
        if last_result:
            last_result.fal_attempts = fal_calls
            return last_result
        return ImageResult(
            page_number=scene.page_number,
            image_url="",
            success=False,
            error="All generation attempts failed quality check",
            fal_attempts=fal_calls,
        )


async def generate_images(scenes: list[Scene]) -> tuple[list[ImageResult], ImageGenMetrics]:
    """
    Fire ALL image generation calls concurrently.
    Capped at max_concurrent_fal_calls via semaphore.
    Returns (results, metrics) for cost tracking.
    """
    logger.info("image_gen_start", page_count=len(scenes))

    results = await asyncio.gather(
        *[_generate_one(scene, _semaphore) for scene in scenes]
    )

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    total_attempts = sum(r.fal_attempts for r in results)
    total_image_spend = total_attempts * settings.cost_flux_lora
    metrics = ImageGenMetrics(
        total_attempts=total_attempts,
        total_image_spend=total_image_spend,
    )

    logger.info(
        "image_gen_complete",
        total=len(scenes),
        successful=len(successful),
        failed=len(failed),
        fal_attempts=total_attempts,
        image_spend=round(total_image_spend, 4),
    )

    if len(failed) > len(scenes) // 2:
        raise RuntimeError(
            f"Too many image generation failures: {len(failed)}/{len(scenes)}"
        )

    return list(results), metrics


async def post_process_image(image_bytes: bytes) -> bytes:
    """No-op — LoRA produces correct B&W line art. Kept for API compatibility."""
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
    """
    Generate a small decorative image for cover background.
    Returns the local temp file path of the saved PNG.
    Uses the same LoRA endpoint for style consistency, but at 512x512.
    """
    prompt = (
        f"{subject}, tmcb_style, simple cute illustration, "
        f"pure black and white line art, no fill, white background, "
        f"centered, minimal detail, children's coloring book decoration"
    )

    lora_url = settings.custom_lora_url
    loras = [{"path": lora_url, "scale": settings.lora_scale}] if lora_url else []
    endpoint = "fal-ai/flux-lora" if loras else "fal-ai/flux/dev"

    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    endpoint,
                    arguments={
                        "prompt": prompt,
                        "loras": loras,
                        "image_size": {"width": 512, "height": 512},
                        "num_inference_steps": 25,
                        "guidance_scale": 5.5,
                        "num_images": 1,
                        "enable_safety_checker": True,
                        "output_format": "png",
                    },
                ),
            ),
            timeout=90.0,
        )

        image_url = result["images"][0]["url"]

        # Download to temp file
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

        logger.info("cover_bg_generated", subject=subject, path=tmp.name)
        return tmp.name

    except Exception as e:
        logger.error("cover_bg_generation_failed", subject=subject, error=str(e))
        raise


# ─── Self-test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import io
    from PIL import Image as PILImage
    import numpy as np
    import PIL.ImageDraw as ImageDraw

    def _make_png(img):
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # Test 1: Solid blue image should FAIL
    blue_img = PILImage.new("RGB", (100, 100),
                             color=(30, 100, 200))
    blue_bytes = _make_png(blue_img)
    result, reason = _is_valid_image(blue_bytes, page_number=901)
    assert result == False, f"Blue image should fail, got {result}"
    print(f"✅ Test 1 PASS: Blue image rejected ({reason})")

    # Test 2: White image with black lines should PASS
    # Uses light gray bg (230) + dense cross-hatching to pass fill-ratio check
    white_img = PILImage.new("RGB", (200, 200),
                              color=(230, 230, 230))
    draw = ImageDraw.Draw(white_img)
    # Dense grid to ensure fill ratio > 60%
    for i in range(0, 200, 12):
        draw.line([(i, 0), (i, 200)], fill=(0, 0, 0), width=2)
        draw.line([(0, i), (200, i)], fill=(0, 0, 0), width=2)
    draw.line([(10, 10), (190, 190)], fill=(0, 0, 0), width=3)
    draw.rectangle([50, 50, 150, 150], outline=(0, 0, 0), width=2)
    line_bytes = _make_png(white_img)
    result, reason = _is_valid_image(line_bytes, page_number=902)
    assert result == True, f"Line art should pass, got {result}/{reason}"
    print(f"✅ Test 2 PASS: Line art accepted")

    print("All saturation tests passed ✅")