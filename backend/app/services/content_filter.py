"""
FIX 4: Filter ALL user-supplied fields (title + theme + story_prompt + character_names).
       Normalize unicode to defeat substitution attacks (Cyrillic lookalikes etc).
FIX 3: Wrap Anthropic call with tenacity. Fall back to keyword-only on total failure.
"""

import unicodedata
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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
    """FIX 4: Normalize unicode to defeat substitution attacks."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def _build_full_text(request: BookRequest) -> str:
    """FIX 4: Concatenate ALL user-supplied fields into one string for checking."""
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


# FIX 3: Retry Anthropic calls
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=False,  # DO NOT reraise — fall back to keyword check on failure
)
def _anthropic_check(text: str) -> tuple[bool, str] | None:
    """Layer 2: Anthropic semantic check. Returns None if API fails."""
    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-haiku-4-5",
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
    if result.startswith("UNSAFE"):
        return False, result.replace("UNSAFE: ", "")
    return True, ""


async def check_content_safety(request: BookRequest) -> tuple[bool, str]:
    """
    FIX 4: Check ALL fields, not just theme.
    Two-layer check: keyword (fast) then Anthropic (semantic).
    Falls back to keyword-only if Anthropic is unavailable.
    """
    # Build full text from ALL user-supplied fields (FIX 4)
    full_text = _build_full_text(request)
    logger.info("content_check_start", text_length=len(full_text))

    # Layer 1: keyword check (always runs)
    is_safe, reason = _keyword_check(full_text)
    if not is_safe:
        logger.warning("content_blocked_keyword", reason=reason)
        return False, reason

    # Layer 2: Anthropic semantic check (with fallback)
    try:
        result = _anthropic_check(full_text)
        if result is None:
            # Anthropic unavailable after all retries — keyword check passed, allow
            logger.warning("content_anthropic_unavailable_fallback")
            return True, ""
        is_safe, reason = result
        if not is_safe:
            logger.warning("content_blocked_anthropic", reason=reason)
        return is_safe, reason
    except Exception as e:
        logger.error("content_check_error", error=str(e))
        return True, ""  # Fail open — keyword check already passed
