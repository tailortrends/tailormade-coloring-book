"""
Content filter: two-layer check (keyword + Anthropic semantic).
Checks ALL user-supplied fields (title, theme, story_prompt, character_names).
Normalizes unicode to defeat substitution attacks.
Runs sync Anthropic call in executor to avoid blocking the async event loop.
"""

import asyncio
import unicodedata
from anthropic import Anthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import structlog
from app.config import get_settings
from app.models.book import BookRequest

logger = structlog.get_logger()
settings = get_settings()

BLOCKED_KEYWORDS = [
    "violence",
    "gore",
    "blood",
    "weapon",
    "gun",
    "knife",
    "drug",
    "sex",
    "nude",
    "naked",
    "adult",
    "explicit",
    "hate",
    "racist",
    "terror",
    "bomb",
    "kill",
    "death",
    "suicide",
    "abuse",
    "harm",
]


def _normalize_text(text: str) -> str:
    """Normalize unicode to defeat substitution attacks."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def _build_full_text(request: BookRequest) -> str:
    """Concatenate ALL user-supplied fields into one string for checking."""
    parts = [
        request.title or "",
        request.theme or "",
        request.story_prompt or "",
    ] + (request.character_names or [])
    return " ".join(parts)


def _keyword_check(text: str) -> tuple[bool, str]:
    """Layer 1: Fast keyword check. Returns (is_safe, reason)."""
    normalized = _normalize_text(text)
    for keyword in BLOCKED_KEYWORDS:
        if keyword in normalized:
            return False, f"Content contains blocked keyword: '{keyword}'"
    return True, ""


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
    retry=retry_if_exception_type(Exception),
    reraise=True,  # Let the exception propagate so we can catch & log it
)
def _anthropic_check(text: str) -> tuple[bool, str]:
    """Layer 2: Anthropic semantic check."""
    logger.info("anthropic_check_attempt", text_length=len(text))
    client = Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=10.0,  # Hard 10s timeout per request
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Is the following children's coloring book request safe and appropriate "
                    f"for children ages 2-12? Reply with only 'SAFE' or 'UNSAFE: <reason>'.\n\n"
                    f"Request: {text[:500]}"
                ),
            }
        ],
    )
    result = response.content[0].text.strip()
    logger.info("anthropic_check_result", result=result[:100])
    if result.startswith("UNSAFE"):
        return False, result.replace("UNSAFE: ", "")
    return True, ""


async def check_content_safety(request: BookRequest) -> tuple[bool, str]:
    """
    Two-layer check: keyword (fast) then Anthropic (semantic).
    Falls back to keyword-only if Anthropic is unavailable.
    """
    full_text = _build_full_text(request)
    logger.info("content_check_start", text_length=len(full_text))

    # Layer 1: keyword check (always runs, instant)
    is_safe, reason = _keyword_check(full_text)
    if not is_safe:
        logger.warning("content_blocked_keyword", reason=reason)
        return False, reason

    # Layer 2: Anthropic semantic check (run sync call in executor)
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _anthropic_check, full_text)
        is_safe, reason = result
        if not is_safe:
            logger.warning("content_blocked_anthropic", reason=reason)
        return is_safe, reason
    except Exception as e:
        # Log the REAL error instead of silently swallowing it
        logger.error(
            "content_anthropic_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        # Fail open — keyword check already passed
        return True, ""