import asyncio
import os
import logging
import structlog
import fal_client
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

os.environ["FAL_KEY"] = settings.fal_key

# ── ONLY THE 8 MISSING SUBJECTS ─────────────────────────────────────────────
# Your 17 keepers are safe — the skip check at the top of generate_single_seed
# will skip any subject_id that already has a .png in seeds/
SEED_PROMPTS = [
    ("animal_cat",
     "a cartoon cat, children's coloring book illustration, bold black outlines, white background"),

    ("animal_dog",
     "a cartoon dog sitting, children's coloring book illustration, bold black outlines, white background"),

    ("animal_elephant",
     "a cartoon elephant, children's coloring book illustration, bold black outlines, white background"),

    ("dino_pterodactyl",
     "a cartoon pterodactyl flying, children's coloring book illustration, bold black outlines, white background"),

    ("farm_horse",
     "a cartoon horse standing, children's coloring book illustration, bold black outlines, white background"),

    ("ocean_shark",
     "a cartoon shark swimming, children's coloring book illustration, bold black outlines, white background"),

    ("ocean_whale",
     "a cartoon whale, children's coloring book illustration, bold black outlines, white background"),

    ("space_astronaut",
     "a cartoon astronaut in spacesuit, children's coloring book illustration, bold black outlines, white background"),

    ("space_rocket",
     "a cartoon rocket ship, children's coloring book illustration, bold black outlines, white background"),

    ("unicorn_flying",
     "a cartoon unicorn with wings flying, children's coloring book illustration, bold black outlines, white background"),

    ("vehicle_airplane",
     "a cartoon airplane, children's coloring book illustration, bold black outlines, white background"),
]

# Suffix kept short — FLUX Dev responds better to simple style instructions
# High guidance + heavy negative prompting = blank pages (learned the hard way)
PROMPT_SUFFIX = "black and white line art, uncolored, outline drawing, printable coloring page"

OUTPUT_DIR = Path("seeds")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def generate_single_seed(subject_id: str, base_prompt: str, semaphore: asyncio.Semaphore):
    """Generate a single seed image. Skips if file already exists."""
    image_path = OUTPUT_DIR / f"{subject_id}.png"
    text_path  = OUTPUT_DIR / f"{subject_id}.txt"

    # ── SKIP: protects existing keepers ─────────────────────────────────────
    if image_path.exists():
        logger.info("seed_skipped_exists", subject=subject_id)
        return True

    full_prompt = f"{base_prompt}, {PROMPT_SUFFIX}"
    logger.info("generating_seed", subject=subject_id, prompt=full_prompt)

    async with semaphore:
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: fal_client.run(
                        "fal-ai/flux/dev",
                        arguments={
                            "prompt": full_prompt,
                            "image_size": "square_hd",
                            "num_inference_steps": 28,  # back to 28 — sweet spot for flux/dev
                            "guidance_scale": 3.5,      # back to 3.5 — 7.0 caused blank pages
                            "num_images": 1,
                            "enable_safety_checker": True,
                            "output_format": "png",
                        },
                    ),
                ),
                timeout=90.0,
            )

            image_url = result["images"][0]["url"]

            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # TXT file pairs with PNG for LoRA training — trigger word is tmcb_style
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

    logger.info(
        "starting_seed_generation",
        total=len(SEED_PROMPTS),
        already_have=len(existing),
        generating=len(to_generate),
    )

    if not to_generate:
        print("\n✅ All seeds already exist — nothing to generate.")
        print(f"   {len(existing)} images in ./{OUTPUT_DIR}/ ready for LoRA training.")
        return

    semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

    tasks = [
        generate_single_seed(subject_id, prompt, semaphore)
        for subject_id, prompt in SEED_PROMPTS
    ]

    results       = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    failed_count  = len(SEED_PROMPTS) - success_count

    logger.info("seed_generation_complete", successful=success_count, failed=failed_count)

    total_in_folder = len(list(OUTPUT_DIR.glob("*.png")))

    if failed_count == 0:
        print(f"\n✅ All {len(to_generate)} new seeds generated successfully.")
        print(f"   Total in seeds/: {total_in_folder} images")
        if total_in_folder >= 25:
            print("   🎯 25+ reached — ready to zip and upload to fal.ai for LoRA training!")
        else:
            print(f"   ⚠️  Still need {25 - total_in_folder} more to hit 25.")
    else:
        print(f"\n⚠️  {failed_count} seeds failed to generate.")
        print(f"   Total in seeds/: {total_in_folder} images")
        print("   Check logs above for which subject_ids failed, then re-run.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("FAL_KEY"):
        print("❌ FAL_KEY not found in .env")
        exit(1)

    asyncio.run(main())