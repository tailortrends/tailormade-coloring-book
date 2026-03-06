import asyncio
import os
import logging
import structlog
import fal_client
from pathlib import Path
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

os.environ["FAL_KEY"] = settings.fal_key

# ── MODEL ────────────────────────────────────────────────────────────────────
# Shakker-Labs Children Simple Sketch LoRA
# Trained specifically for children's line art on FLUX.1-dev
# Hosted on HuggingFace — no auth required
COLORING_BOOK_LORA = "https://v3b.fal.media/files/b/0a90d9ee/dqZ721n9Zseuu3MCbZBl-_children_sketch.safetensors"

# ── SEEDS V2 — CLEAN 25 ───────────────────────────────────────────────────
# One subject per entry. Prompts are intentionally short — the LoRA handles style,
# the prompt just needs to name the subject clearly.
# Covers all 8 taxonomy themes + all 4 complexity tiers represented across the set.
SEED_PROMPTS = [
    ("animal_lion", "a friendly lion, children's coloring book page"),
]

# Style suffix — kept minimal so the LoRA does the heavy lifting
PROMPT_SUFFIX = "children's coloring book page, bold black ink outlines, pure white background, no color fill, no shading, flat line art, ready to color, simple cartoon style"

# ── OUTPUT ───────────────────────────────────────────────────────────────────
# Fresh folder — does not touch your existing seeds/ keeper images
OUTPUT_DIR = Path("seeds_v2")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def generate_single_seed(
    subject_id: str, base_prompt: str, semaphore: asyncio.Semaphore
):
    """Generate one seed. Skips if file already exists in seeds_v2/."""
    image_path = OUTPUT_DIR / f"{subject_id}.png"
    text_path  = OUTPUT_DIR / f"{subject_id}.txt"

    if image_path.exists():
        logger.info("seed_skipped_exists", subject=subject_id)
        return True

    full_prompt = f"{base_prompt}, {PROMPT_SUFFIX}"
    logger.info("generating_seed", subject=subject_id)

    async with semaphore:
        try:
            # DELETE the COLORING_BOOK_LORA variable entirely

            # Change the fal_client.run call to:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: fal_client.run(
                        "fal-ai/flux-pro/v1.1",
                        arguments={
                            "prompt": full_prompt,
                            "image_size": "square_hd",
                            "num_inference_steps": 28,
                            "guidance_scale": 3.5,
                            "num_images": 1,
                            "output_format": "png",
                            "safety_tolerance": "2",
                        },
                    ),
                ),
                timeout=120.0,
            )

            image_url = result["images"][0]["url"]

            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                image_bytes = resp.content

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # TXT caption pairs with PNG for LoRA training
            # trigger word tmcb_style gets embedded during training
            with open(text_path, "w") as f:
                f.write(f"tmcb_style, {base_prompt}")

            logger.info("seed_saved", subject=subject_id, path=str(image_path))
            return True

        except Exception as e:
            logger.error("seed_failed", subject=subject_id, error=str(e))
            return False


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    existing    = [p.stem for p in OUTPUT_DIR.glob("*.png")]
    to_generate = [s for s in SEED_PROMPTS if s[0] not in existing]

    print(f"\n{'─' * 50}")
    print(f"  TailorMade Seed Generator v2")
    print(f"  Model: Shakker-Labs Children Sketch LoRA")
    print(f"  Output: ./{OUTPUT_DIR}/")
    print(f"{'─' * 50}")
    print(f"  Total subjects : {len(SEED_PROMPTS)}")
    print(f"  Already exist  : {len(existing)}")
    print(f"  Generating now : {len(to_generate)}")
    print(f"  Est. cost      : ~${len(to_generate) * 0.025:.2f}")
    print(f"{'─' * 50}\n")

    if not to_generate:
        print("✅ All seeds already exist. Nothing to generate.")
        print(f"   Review ./{OUTPUT_DIR}/ then zip for fal.ai LoRA training.")
        return

    semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

    tasks = [
        generate_single_seed(subject_id, prompt, semaphore)
        for subject_id, prompt in SEED_PROMPTS
    ]

    results      = await asyncio.gather(*tasks)
    success      = sum(1 for r in results if r)
    failed       = len(SEED_PROMPTS) - success
    total_in_dir = len(list(OUTPUT_DIR.glob("*.png")))

    print(f"\n{'─' * 50}")
    if failed == 0:
        print(f"  ✅ {success} seeds generated successfully")
        print(f"  Total in {OUTPUT_DIR}/: {total_in_dir} images")
        if total_in_dir >= 25:
            print(f"  🎯 25 reached — review images then zip {OUTPUT_DIR}/ for training")
        else:
            print(f"  Need {25 - total_in_dir} more — re-run to retry any failures")
    else:
        print(f"  ⚠️  {failed} failed | {success} succeeded")
        print(f"  Total saved: {total_in_dir}")
        print(f"  Re-run to retry failures — existing files are skipped")
    print(f"{'─' * 50}\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("FAL_KEY"):
        print("❌ FAL_KEY not found in .env")
        exit(1)

    asyncio.run(main())