import asyncio
import os
import json
import logging
import sqlite3
import threading
import structlog
import uuid
from pathlib import Path
from datetime import datetime, timezone

import fal_client
import boto3
import firebase_admin
from firebase_admin import credentials, firestore
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

os.environ["FAL_KEY"] = settings.fal_key

PROMPT_SUFFIX = "tmcb_style, pure black and white line art, no fill, no color, no grey, clean outlines only, print-ready"

# ── PATHS ─────────────────────────────────────────────────────────────────────
# Use __file__ so paths are correct regardless of where you run the script from
BASE_DIR     = Path(__file__).parent
TAXONOMY_DIR = BASE_DIR.parent / "taxonomy"
OUTPUT_DIR   = BASE_DIR / "batch_local_cache"
DB_FILE      = BASE_DIR / "batch_state.db"

# ── THREAD-SAFE SQLITE ────────────────────────────────────────────────────────
# SQLite connections cannot be shared across threads/async tasks.
# We use a threading.Lock + one connection per write to keep it safe.
_db_lock = threading.Lock()


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_log (
            id                TEXT PRIMARY KEY,
            subject_id        TEXT NOT NULL,
            tier              TEXT NOT NULL,
            variation_index   INTEGER NOT NULL,
            prompt            TEXT,
            status            TEXT DEFAULT 'pending',
            local_path        TEXT,
            r2_url            TEXT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sig
        ON generation_log(subject_id, tier, variation_index)
    """)
    conn.commit()
    return conn


def db_update(conn: sqlite3.Connection, sql: str, params: tuple):
    """Thread-safe SQLite write."""
    with _db_lock:
        conn.execute(sql, params)
        conn.commit()


# ── R2 UPLOAD ─────────────────────────────────────────────────────────────────
def upload_to_r2(local_path: str, blob_name: str) -> str:
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )
    s3.upload_file(
        Filename=local_path,
        Bucket=settings.r2_bucket_name,
        Key=blob_name,
        ExtraArgs={"ContentType": "image/png"},
    )
    return f"{settings.r2_public_url}/{blob_name}"


# ── FIREBASE ──────────────────────────────────────────────────────────────────
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.firebase_service_account_path)
        firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
    return firestore.client()


# ── PROGRESS COUNTER ──────────────────────────────────────────────────────────
class Progress:
    def __init__(self, total: int):
        self.total    = total
        self.success  = 0
        self.failed   = 0
        self._lock    = threading.Lock()
        self.start_time = datetime.now()

    def record(self, success: bool):
        with self._lock:
            if success:
                self.success += 1
            else:
                self.failed += 1
            done     = self.success + self.failed
            elapsed  = (datetime.now() - self.start_time).total_seconds()
            rate     = done / elapsed if elapsed > 0 else 0
            remaining = (self.total - done) / rate if rate > 0 else 0
            eta_min  = int(remaining // 60)
            eta_sec  = int(remaining % 60)
            print(
                f"\r  [{done}/{self.total}] "
                f"✅ {self.success}  ❌ {self.failed}  "
                f"ETA {eta_min}m {eta_sec}s   ",
                end="", flush=True
            )


# ── CORE GENERATION TASK ──────────────────────────────────────────────────────
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=2, min=5, max=30),
    retry=retry_if_exception_type((Exception,)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def generate_and_store(
    record_id: str,
    subject_id: str,
    tier: str,
    variation_index: int,
    base_prompt: str,
    semaphore: asyncio.Semaphore,
    db_conn: sqlite3.Connection,
    db_client,
    progress: Progress,
):
    full_prompt = f"{base_prompt}, {PROMPT_SUFFIX}"
    local_path  = OUTPUT_DIR / f"{subject_id}_{tier}_v{variation_index}.png"
    blob_name   = f"library/{subject_id}/{tier}/{subject_id}_{tier}_v{variation_index}.png"

    async with semaphore:
        try:
            # 1. Generate
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: fal_client.run(
                        "fal-ai/flux-lora",
                        arguments={
                            "prompt": full_prompt,
                            "loras": [{"path": settings.custom_lora_url, "scale": 1.0}],
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

            # 2. Download
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                local_path.write_bytes(resp.content)

            # 3. Upload to R2
            r2_url = await asyncio.get_event_loop().run_in_executor(
                None, upload_to_r2, str(local_path), blob_name
            )

            # 4. Save to Firestore
            doc_ref = db_client.collection("library_images").document(record_id)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: doc_ref.set({
                    "id":              record_id,
                    "subject_id":      subject_id,
                    "tier":            tier,
                    "variation_index": variation_index,
                    "prompt":          base_prompt,
                    "image_url":       r2_url,
                    "created_at":      datetime.now(timezone.utc),
                }),
            )

            # 5. Mark success in SQLite
            db_update(conn=db_conn, sql="""
                UPDATE generation_log
                SET status='success', local_path=?, r2_url=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, params=(str(local_path), r2_url, record_id))

            # 6. Delete local cache file to save disk space
            local_path.unlink(missing_ok=True)

            progress.record(success=True)
            return True

        except Exception as e:
            logger.error("task_failed", record_id=record_id, subject=subject_id,
                         tier=tier, var=variation_index, error=str(e))
            db_update(conn=db_conn, sql="""
                UPDATE generation_log
                SET status='failed', updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, params=(record_id,))
            progress.record(success=False)
            return False


# ── MAIN ──────────────────────────────────────────────────────────────────────
async def main():
    if not getattr(settings, "custom_lora_url", None):
        print("❌ CUSTOM_LORA_URL missing from .env")
        exit(1)

    if not TAXONOMY_DIR.exists():
        print(f"❌ Taxonomy directory not found: {TAXONOMY_DIR}")
        exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    db_conn   = init_db()
    db_client = init_firebase()
    cursor    = db_conn.cursor()

    # ── BUILD QUEUE ───────────────────────────────────────────────────────────
    print("\nParsing taxonomy JSONs...")
    tasks_to_run = []

    for json_file in sorted(TAXONOMY_DIR.glob("*.json")):
        if json_file.name == "master_index.json":
            continue

        with open(json_file) as f:
            data = json.load(f)

        variations = data.get("variations_per_slot", 3)

        for subject in data.get("subjects", []):
            subj_id = subject["subject_id"]
            prompts = subject.get("prompts", {})

            for tier, prompt_text in prompts.items():
                for v in range(1, variations + 1):

                    cursor.execute(
                        "SELECT id, status FROM generation_log "
                        "WHERE subject_id=? AND tier=? AND variation_index=?",
                        (subj_id, tier, v),
                    )
                    row = cursor.fetchone()

                    if not row:
                        record_id = str(uuid.uuid4())
                        with _db_lock:
                            cursor.execute("""
                                INSERT INTO generation_log
                                    (id, subject_id, tier, variation_index, prompt, status)
                                VALUES (?, ?, ?, ?, ?, 'pending')
                            """, (record_id, subj_id, tier, v, prompt_text))
                            db_conn.commit()
                        status = "pending"
                    else:
                        record_id, status = row

                    if status != "success":
                        tasks_to_run.append({
                            "record_id":       record_id,
                            "subject_id":      subj_id,
                            "tier":            tier,
                            "variation_index": v,
                            "prompt":          prompt_text,
                        })

    total     = len(tasks_to_run)
    est_cost  = total * 0.025

    print(f"\n{'─' * 54}")
    print(f"  TailorMade Batch Generator")
    print(f"  LoRA: ...{settings.custom_lora_url[-40:]}")
    print(f"{'─' * 54}")
    print(f"  Pending images : {total}")
    print(f"  Concurrency    : {settings.max_concurrent_fal_calls}")
    print(f"  Est. cost      : ~${est_cost:.2f}")
    print(f"  Est. time      : ~{int(total / settings.max_concurrent_fal_calls * 8 / 60)} min")
    print(f"{'─' * 54}")

    if total == 0:
        print("\n🎉 Library is complete — no pending images.")
        return

    confirm = input("\n  Type YES to start batch: ").strip()
    if confirm != "YES":
        print("  Aborted.")
        return

    # ── RUN ───────────────────────────────────────────────────────────────────
    semaphore = asyncio.Semaphore(settings.max_concurrent_fal_calls)
    progress  = Progress(total)

    print(f"\n  Generating {total} images...\n")

    coroutines = [
        generate_and_store(
            t["record_id"], t["subject_id"], t["tier"], t["variation_index"], t["prompt"],
            semaphore, db_conn, db_client, progress,
        )
        for t in tasks_to_run
    ]

    results = await asyncio.gather(*coroutines)

    success = sum(1 for r in results if r)
    failed  = len(results) - success

    print(f"\n\n{'─' * 54}")
    print(f"  ✅ Succeeded : {success}")
    print(f"  ❌ Failed    : {failed}")
    if failed > 0:
        print(f"  Re-run to retry failed images — successes are skipped.")
    else:
        print(f"  🎉 Library complete!")
    print(f"{'─' * 54}\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("FAL_KEY"):
        print("❌ FAL_KEY not found in .env")
        exit(1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.firebase_service_account_path
    asyncio.run(main())