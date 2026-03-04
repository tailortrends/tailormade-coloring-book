"""
FIX 1: Concurrency — asyncio.gather() with Semaphore(5) for parallel fal.ai calls.
FIX 3: Retry — tenacity wraps every fal.ai call (3 attempts, exponential backoff).
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Optional
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

# FIX 1: Semaphore caps concurrent fal.ai calls
_semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

# FIX 5: Set credential from settings, never hardcoded
os.environ["FAL_KEY"] = settings.fal_key


@dataclass
class ImageResult:
    page_number: int
    image_url: str
    image_bytes: Optional[bytes] = None
    success: bool = True
    error: Optional[str] = None


# FIX 3: Retry decorator for individual fal.ai calls
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def _call_fal_single(prompt: str, page_number: int) -> ImageResult:
    """Single fal.ai call with retry logic."""
    logger.info("fal_call_start", page=page_number)
    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.run(
                    "fal-ai/flux/dev",
                    arguments={
                        "prompt": prompt,
                        "image_size": "square_hd",
                        "num_inference_steps": 28,
                        "guidance_scale": 3.5,
                        "num_images": 1,
                        "enable_safety_checker": True,
                        "output_format": "png",
                    },
                ),
            ),
            timeout=60.0,  # 60-second hard timeout per image
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


async def _generate_one(scene: Scene, semaphore: asyncio.Semaphore) -> ImageResult:
    """FIX 1: Acquire semaphore slot, then call fal.ai with retry."""
    prompt = _build_prompt(scene)
    async with semaphore:
        try:
            return await _call_fal_single(prompt, scene.page_number)
        except Exception as e:
            # After all retries exhausted, return a failed result (don't crash whole book)
            logger.error("fal_all_retries_failed", page=scene.page_number, error=str(e))
            return ImageResult(
                page_number=scene.page_number,
                image_url="",
                success=False,
                error=str(e),
            )


async def generate_images(scenes: list[Scene]) -> list[ImageResult]:
    """
    FIX 1: Fire ALL image generation calls concurrently using asyncio.gather().
    All scenes launch simultaneously, capped at max_concurrent_fal_calls via semaphore.
    10-page book: ~12 seconds instead of ~100 seconds.
    """
    logger.info("image_gen_start", page_count=len(scenes))

    # FIX 1: gather() fires everything at once
    results = await asyncio.gather(
        *[_generate_one(scene, _semaphore) for scene in scenes]
    )

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    logger.info(
        "image_gen_complete",
        total=len(scenes),
        successful=len(successful),
        failed=len(failed),
    )

    if len(failed) > len(scenes) // 2:
        raise RuntimeError(
            f"Too many image generation failures: {len(failed)}/{len(scenes)}"
        )

    return list(results)


def _build_prompt(scene: Scene) -> str:
    """Build the fal.ai prompt from a scene, using complexity-appropriate language."""
    complexity_map = {
        "simple": "EXTRA THICK bold black outlines, single subject, white background, NO background details, suitable for toddlers ages 2-4",
        "beginner": "thick bold black outlines, simple background, easy to color, suitable for ages 4-6",
        "medium": "medium weight black outlines, moderate detail, fun scene, suitable for ages 6-9",
        "advanced": "fine detailed black outlines, rich scene, foreground and background, suitable for ages 9-12",
    }
    style = complexity_map.get(scene.complexity, complexity_map["medium"])
    return (
        f"children's coloring book page, {style}, "
        f"{scene.description}, "
        f"pure black and white line art, no fill, no color, no grey, "
        f"clean outlines only, print-ready"
    )


async def post_process_image(image_bytes: bytes) -> bytes:
    """Convert to grayscale, threshold to pure B&W for coloring book."""
    from PIL import Image, ImageOps
    import io

    loop = asyncio.get_event_loop()

    def _process():
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img = ImageOps.autocontrast(img)
        threshold = 180
        img = img.point(lambda p: 255 if p > threshold else 0)
        output = io.BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    return await loop.run_in_executor(None, _process)
