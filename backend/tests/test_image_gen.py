import asyncio
import io
import os
import tempfile

from PIL import Image, ImageDraw

os.environ.setdefault("FAL_KEY", "test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("R2_ACCOUNT_ID", "test")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("R2_BUCKET_NAME", "test")
os.environ.setdefault("R2_PUBLIC_URL", "https://test.r2.dev")

from app.models.book import Scene
from app.services import image_gen


def _png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_line_art_validation_accepts_clean_bw():
    image = Image.new("RGB", (200, 200), "white")
    draw = ImageDraw.Draw(image)
    for i in range(0, 200, 12):
        draw.line([(i, 0), (i, 200)], fill="black", width=2)
        draw.line([(0, i), (200, i)], fill="black", width=2)

    valid, reason = image_gen._is_valid_image(_png_bytes(image), page_number=1)
    assert valid is True
    assert reason == "pass"


def test_line_art_validation_rejects_mid_gray():
    image = Image.new("RGB", (200, 200), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 160, 160), fill=(128, 128, 128))
    for i in range(0, 200, 20):
        draw.line([(i, 0), (i, 200)], fill="black", width=2)

    valid, reason = image_gen._is_valid_image(_png_bytes(image), page_number=2)
    assert valid is False
    assert reason == "mid_gray"


def test_validate_is_line_art_path_helper():
    line_art = Image.new("RGB", (100, 100), "white")
    draw = ImageDraw.Draw(line_art)
    draw.line([(0, 0), (99, 99)], fill="black", width=4)

    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        line_art.save(tmp.name)
        assert image_gen.validate_is_line_art(tmp.name) is True


def test_kontext_call_sends_negative_prompt(monkeypatch):
    captured = {}

    def fake_run(endpoint, arguments, headers=None):
        captured["endpoint"] = endpoint
        captured["arguments"] = arguments
        captured["headers"] = headers
        return {"images": [{"url": "https://fal.example/image.png"}]}

    monkeypatch.setattr(image_gen.fal_client, "run", fake_run)

    scene = Scene(
        page_number=1,
        main_subject="rocket",
        subject_hint="rocket",
        theme="space",
        complexity="simple",
    )
    prompt = image_gen._build_prompt(scene, age_range="4-6")
    url, _ = asyncio.get_event_loop().run_until_complete(
        image_gen._call_kontext(prompt, page_number=1)
    )

    assert url == "https://fal.example/image.png"
    assert captured["arguments"]["negative_prompt"] == image_gen.NEGATIVE_PROMPT


def test_kontext_call_sends_short_lifecycle_header(monkeypatch):
    """Every fal generation must ask fal to expire its own CDN copy quickly, so
    generated children's content doesn't linger on a public third-party URL."""
    captured = {}

    def fake_run(endpoint, arguments, headers=None):
        captured["headers"] = headers
        return {"images": [{"url": "https://fal.example/image.png"}]}

    monkeypatch.setattr(image_gen.fal_client, "run", fake_run)

    scene = Scene(
        page_number=1,
        main_subject="rocket",
        subject_hint="rocket",
        theme="space",
        complexity="simple",
    )
    prompt = image_gen._build_prompt(scene, age_range="4-6")
    asyncio.get_event_loop().run_until_complete(
        image_gen._call_kontext(prompt, page_number=1)
    )

    headers = captured["headers"] or {}
    assert image_gen.FAL_OUTPUT_LIFECYCLE_HEADER in headers
    # Value is a short, finite TTL (fal default without this is ~7 days).
    import json as _json
    pref = _json.loads(headers[image_gen.FAL_OUTPUT_LIFECYCLE_HEADER])
    assert pref["expiration_duration_seconds"] <= 86400
    assert pref["expiration_duration_seconds"] > 0
