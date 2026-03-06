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

# ── SPOT CHECK MATRIX ────────────────────────────────────────────────────────
# 5 fresh subjects x 4 complexity tiers = 20 images
# None of these subjects were used in the seed training set
# Purpose: verify the LoRA generalizes to NEW subjects it hasn't seen before
SPOT_CHECK_MATRIX = [

    # Subject 1: Penguin (Animals theme — not in seeds)
    ("penguin_simple",
     "tmcb_style, single large penguin standing, children's coloring book page, "
     "EXTRA THICK black outlines, white background, ages 2-4"),
    ("penguin_beginner",
     "tmcb_style, penguin sliding on ice, children's coloring book page, "
     "thick black outlines, simple background, ages 4-6"),
    ("penguin_medium",
     "tmcb_style, penguin family on iceberg with fish jumping, children's coloring book page, "
     "medium black outlines, ages 6-9"),
    ("penguin_advanced",
     "tmcb_style, penguin colony on Antarctic ice with detailed icebergs and aurora in sky, "
     "children's coloring book page, fine detailed black outlines, ages 9-12"),

    # Subject 2: Submarine (Vehicles theme — not in seeds)
    ("submarine_simple",
     "tmcb_style, single large cartoon submarine, children's coloring book page, "
     "EXTRA THICK black outlines, white background, ages 2-4"),
    ("submarine_beginner",
     "tmcb_style, submarine underwater with bubbles and a fish, children's coloring book page, "
     "thick black outlines, simple background, ages 4-6"),
    ("submarine_medium",
     "tmcb_style, submarine exploring ocean floor with coral and treasure chest, "
     "children's coloring book page, medium black outlines, ages 6-9"),
    ("submarine_advanced",
     "tmcb_style, detailed submarine with periscope navigating deep ocean scene with "
     "anglerfish, shipwreck and sea creatures, children's coloring book page, "
     "fine detailed black outlines, ages 9-12"),

    # Subject 3: Fox (Animals theme — not in seeds)
    ("fox_simple",
     "tmcb_style, single large cartoon fox sitting, children's coloring book page, "
     "EXTRA THICK black outlines, white background, ages 2-4"),
    ("fox_beginner",
     "tmcb_style, fox running through autumn leaves, children's coloring book page, "
     "thick black outlines, simple background, ages 4-6"),
    ("fox_medium",
     "tmcb_style, fox family outside their den in a forest, children's coloring book page, "
     "medium black outlines, ages 6-9"),
    ("fox_advanced",
     "tmcb_style, fox kit playing in detailed autumn forest scene with mushrooms, "
     "fallen leaves and stream, children's coloring book page, "
     "fine detailed black outlines, ages 9-12"),

    # Subject 4: Mermaid (Ocean theme — not in seeds)
    ("mermaid_simple",
     "tmcb_style, single large friendly mermaid, children's coloring book page, "
     "EXTRA THICK black outlines, white background, ages 2-4"),
    ("mermaid_beginner",
     "tmcb_style, mermaid swimming with a dolphin, children's coloring book page, "
     "thick black outlines, simple background, ages 4-6"),
    ("mermaid_medium",
     "tmcb_style, mermaid sitting on a rock with starfish and seashells around her, "
     "children's coloring book page, medium black outlines, ages 6-9"),
    ("mermaid_advanced",
     "tmcb_style, mermaid in detailed underwater kingdom with coral towers, "
     "tropical fish and treasure, children's coloring book page, "
     "fine detailed black outlines, ages 9-12"),

    # Subject 5: Hot Air Balloon (Vehicles theme — not in seeds)
    ("balloon_simple",
     "tmcb_style, single large cartoon hot air balloon, children's coloring book page, "
     "EXTRA THICK black outlines, white background, ages 2-4"),
    ("balloon_beginner",
     "tmcb_style, hot air balloon floating over hills with clouds, "
     "children's coloring book page, thick black outlines, simple background, ages 4-6"),
    ("balloon_medium",
     "tmcb_style, three hot air balloons floating over a village and river, "
     "children's coloring book page, medium black outlines, ages 6-9"),
    ("balloon_advanced",
     "tmcb_style, detailed hot air balloon festival over mountain landscape with "
     "forest, lake and tiny village below, children's coloring book page, "
     "fine detailed black outlines, ages 9-12"),
]

PROMPT_SUFFIX = "pure black and white line art, no fill, no color, no grey, clean outlines only, print-ready"

OUTPUT_DIR = Path("spot_checks")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def generate_spot_check(
    variation_id: str,
    base_prompt: str,
    semaphore: asyncio.Semaphore,
    custom_lora_url: str,
):
    """Generate a single spot check image using the trained custom LoRA."""
    image_path = OUTPUT_DIR / f"{variation_id}.png"

    if image_path.exists():
        logger.info("spot_check_skipped_exists", variation=variation_id)
        return True

    full_prompt = f"{base_prompt}, {PROMPT_SUFFIX}"
    logger.info("generating_spot_check", variation=variation_id)

    async with semaphore:
        try:
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: fal_client.run(
                        "fal-ai/flux-lora",
                        arguments={
                            "prompt": full_prompt,
                            "loras": [{"path": custom_lora_url, "scale": 1.0}],
                            "image_size": "square_hd",
                            "num_inference_steps": 28,
                            "guidance_scale": 3.5,
                            "num_images": 1,
                            "enable_safety_checker": True,
                            "output_format": "png",
                        },
                    ),
                ),
                timeout=120.0,
            )

            image_url = result["images"][0]["url"]

            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            logger.info("spot_check_saved", variation=variation_id, path=str(image_path))
            return True

        except Exception as e:
            logger.error("spot_check_failed", variation=variation_id, error=str(e))
            return False


async def main():
    if not getattr(settings, "custom_lora_url", None):
        print("❌ CUSTOM_LORA_URL missing from .env")
        print("   Add: CUSTOM_LORA_URL=https://v3b.fal.media/files/...")
        exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    existing    = [p.stem for p in OUTPUT_DIR.glob("*.png")]
    to_generate = [s for s in SPOT_CHECK_MATRIX if s[0] not in existing]

    print(f"\n{'─' * 52}")
    print(f"  TailorMade Spot Check")
    print(f"  LoRA: ...{settings.custom_lora_url[-40:]}")
    print(f"{'─' * 52}")
    print(f"  Total checks   : {len(SPOT_CHECK_MATRIX)}")
    print(f"  Already exist  : {len(existing)}")
    print(f"  Generating now : {len(to_generate)}")
    print(f"  Est. cost      : ~${len(to_generate) * 0.025:.2f}")
    print(f"{'─' * 52}\n")

    if not to_generate:
        print("✅ All spot checks already exist.")
        print(f"   Review ./{OUTPUT_DIR}/ and decide: GO or NO-GO for full batch.")
        return

    semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)

    tasks = [
        generate_spot_check(variation_id, prompt, semaphore, settings.custom_lora_url)
        for variation_id, prompt in SPOT_CHECK_MATRIX
    ]

    results       = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    failed_count  = len(SPOT_CHECK_MATRIX) - success_count
    total_in_dir  = len(list(OUTPUT_DIR.glob("*.png")))

    print(f"\n{'─' * 52}")
    if failed_count == 0:
        print(f"  ✅ All {len(to_generate)} spot checks generated.")
        print(f"  Total in spot_checks/: {total_in_dir}")
        print(f"\n  REVIEW CHECKLIST:")
        print(f"  □ Are outlines black (not gray)?")
        print(f"  □ Is background pure white?")
        print(f"  □ Does 'simple' look simpler than 'advanced'?")
        print(f"  □ Are all 4 complexity tiers visually distinct?")
        print(f"  □ Would a child recognize each subject?")
        print(f"\n  If YES to all → run 03_batch_generate.py")
        print(f"  If NO to any  → report back for LoRA adjustments")
    else:
        print(f"  ⚠️  {failed_count} failed | {success_count} succeeded")
        print(f"  Re-run to retry — existing files are skipped")
    print(f"{'─' * 52}\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("FAL_KEY"):
        print("❌ FAL_KEY not found in .env")
        exit(1)

    asyncio.run(main())