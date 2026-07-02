"""
Free-tier books must not expose clean, unwatermarked interior page images — the
watermarked PDF is the only artifact handed back. Paid tiers still get pages.
No external calls are made; this exercises the response-shaping helper directly.
"""

import os

os.environ.setdefault("FAL_KEY", "test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("R2_ACCOUNT_ID", "test")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("R2_BUCKET_NAME", "test")
os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")

from app.routers import books
from app.services import storage


def _fake_signed(monkeypatch):
    monkeypatch.setattr(
        storage, "generate_presigned_url",
        lambda key, expiry_seconds=0: f"https://signed/{key}",
    )


def _book(watermarked: bool) -> dict:
    return {
        "book_id": "b1",
        "uid": "user-1",
        "title": "Ocean Friends",
        "theme": "ocean",
        "age_range": "4-6",
        "page_count": 2,
        "page_keys": ["books/b1/page_001.png", "books/b1/page_002.png"],
        "pdf_key": "books/b1/book.pdf",
        "status": "complete",
        "watermarked": watermarked,
        "created_at": __import__("datetime").datetime.now(),
    }


def test_free_book_hides_page_urls(monkeypatch):
    _fake_signed(monkeypatch)
    resp = books._book_response_from_data(_book(watermarked=True))
    assert resp.pdf_url is not None          # watermarked PDF still available
    assert resp.page_urls == []              # no clean page images
    assert resp.page_count == 2              # count preserved


def test_paid_book_exposes_page_urls(monkeypatch):
    _fake_signed(monkeypatch)
    resp = books._book_response_from_data(_book(watermarked=False))
    assert len(resp.page_urls) == 2
