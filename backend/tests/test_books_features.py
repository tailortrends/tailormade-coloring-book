import asyncio
import io
import os
import zipfile
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

os.environ.setdefault("FAL_KEY", "test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("R2_ACCOUNT_ID", "test")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("R2_BUCKET_NAME", "test")
os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")
os.environ.setdefault("STRIPE_MODE", "test")
os.environ.setdefault("STRIPE_TEST_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_TEST_PUBLISHABLE_KEY", "pk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_testsecret")
os.environ.setdefault("STRIPE_FAMILY_PRICE_ID", "price_family_123")
os.environ.setdefault("STRIPE_TEACHER_PRICE_ID", "price_teacher_456")
os.environ.setdefault("STRIPE_SINGLE_PRICE_ID", "price_single_789")

from app.main import app
from app.routers import books
from app.services import pdf_builder


def test_build_pdf_watermark_flag_follows_tier(monkeypatch):
    captured = []

    async def fake_download(urls, tmp_dir):
        return ["/tmp/page.png"]

    def fake_render(title, age_range, image_paths, cover_hero_path, theme, add_watermark=False):
        captured.append(add_watermark)
        return b"%PDF-test"

    monkeypatch.setattr(pdf_builder, "_download_images_to_disk", fake_download)
    monkeypatch.setattr(pdf_builder, "_render_pdf", fake_render)

    asyncio.get_event_loop().run_until_complete(
        pdf_builder.build_pdf("free-book", "Free", ["ignored"], "4-6", user_tier="free")
    )
    asyncio.get_event_loop().run_until_complete(
        pdf_builder.build_pdf("paid-book", "Paid", ["ignored"], "4-6", user_tier="family")
    )

    assert captured == [True, False]


def test_download_zip_rejects_free_users(monkeypatch):
    monkeypatch.setattr(
        books.firebase,
        "get_user_stripe_info",
        AsyncMock(return_value={"subscription_tier": "free", "subscription_active": False}),
    )
    app.dependency_overrides[books.get_current_user] = lambda: {"uid": "user-1"}
    client = TestClient(app)

    response = client.post("/api/v1/books/download-zip", json={"book_ids": ["book-1"]})

    assert response.status_code == 403
    assert response.json()["detail"] == "Bulk download requires a paid plan"
    app.dependency_overrides.clear()


def test_download_zip_returns_owned_pdfs_for_paid_users(monkeypatch):
    async def fake_get_book(book_id):
        return {
            "book_id": book_id,
            "uid": "user-1",
            "user_id": "user-1",
            "title": f"Book {book_id}",
            "pdf_key": f"books/{book_id}/book.pdf",
        }

    monkeypatch.setattr(
        books.firebase,
        "get_user_stripe_info",
        AsyncMock(return_value={"subscription_tier": "teacher", "subscription_active": True}),
    )
    monkeypatch.setattr(books.firebase, "get_book", fake_get_book)
    monkeypatch.setattr(books.storage, "get_object_bytes", AsyncMock(return_value=b"%PDF-test"))
    app.dependency_overrides[books.get_current_user] = lambda: {"uid": "user-1"}
    client = TestClient(app)

    response = client.post(
        "/api/v1/books/download-zip",
        json={"book_ids": ["book-1", "book-2"]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert sorted(archive.namelist()) == ["Book_book-1.pdf", "Book_book-2.pdf"]
        assert archive.read("Book_book-1.pdf") == b"%PDF-test"
    app.dependency_overrides.clear()
