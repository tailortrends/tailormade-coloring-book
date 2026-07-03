"""
Tests for content-safety behavior — especially that Layer 2 (Anthropic) fails
CLOSED. No real Anthropic calls are made; the client is stubbed.
"""

import os
import asyncio
from unittest.mock import patch, MagicMock

os.environ.setdefault("FAL_KEY", "test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("R2_ACCOUNT_ID", "test")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("R2_BUCKET_NAME", "test")
os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")

from app.services import content_filter
from app.models.book import BookRequest


def _benign_request() -> BookRequest:
    return BookRequest(
        title="Ocean Friends",
        theme="ocean",
        age_range="4-6",
        page_count=6,
        story_prompt="A happy dolphin makes new friends",
        character_names=["Mia"],
    )


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _anthropic_returning(text: str):
    """Build a fake Anthropic class whose messages.create returns `text`."""
    fake_client = MagicMock()
    fake_msg = MagicMock()
    fake_msg.content = [MagicMock(text=text)]
    fake_client.messages.create.return_value = fake_msg
    return MagicMock(return_value=fake_client)


def test_keyword_boundary_no_false_positive():
    """Benign words containing a blocked substring must NOT trip the keyword layer."""
    ok, reason = content_filter._keyword_check("a charming and skillful classic scene")
    assert ok is True, reason


def test_keyword_boundary_still_blocks_whole_word():
    """A blocked word as a whole word is still caught."""
    ok, reason = content_filter._keyword_check("a scene with a gun")
    assert ok is False
    assert "gun" in reason


def test_keyword_layer_blocks_before_anthropic():
    """A request tripping the keyword list is blocked without calling Anthropic."""
    req = BookRequest(title="Bomb Squad", theme="vehicles", age_range="6-9")
    with patch.object(content_filter, "Anthropic") as mock_anthropic:
        is_safe, reason = _run(content_filter.check_content_safety(req))
    assert is_safe is False
    assert "blocked keyword" in reason
    mock_anthropic.assert_not_called()


def test_anthropic_safe_allows():
    """Benign request + Anthropic says SAFE → allowed."""
    with patch.object(content_filter, "Anthropic", _anthropic_returning("SAFE")):
        is_safe, reason = _run(content_filter.check_content_safety(_benign_request()))
    assert is_safe is True


def test_anthropic_unsafe_blocks():
    """Anthropic says UNSAFE → blocked with its reason."""
    with patch.object(content_filter, "Anthropic",
                      _anthropic_returning("UNSAFE: depicts weapons")):
        is_safe, reason = _run(content_filter.check_content_safety(_benign_request()))
    assert is_safe is False
    assert "weapons" in reason


def test_anthropic_error_fails_closed():
    """If the Anthropic call raises, the request must be BLOCKED, not allowed."""
    fake_client = MagicMock()
    fake_client.messages.create.side_effect = RuntimeError("api down / out of credits")
    with patch.object(content_filter, "Anthropic", MagicMock(return_value=fake_client)):
        is_safe, reason = _run(content_filter.check_content_safety(_benign_request()))
    assert is_safe is False
    assert reason  # a user-facing "couldn't verify" message, not empty
