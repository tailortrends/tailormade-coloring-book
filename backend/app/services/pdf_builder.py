"""
PDF generation using reportlab (pure Python, no system library dependencies).

Features:
- Cover page with full-page hero image + semi-transparent title overlay
- Clean image-only coloring pages (no text, no borders, no page numbers)
- Autocrop white margins so subjects fill the page
- Print-ready 8.5 x 11 inches at proper margins
"""

import asyncio
import tempfile
import shutil
import os
import math
from io import BytesIO
from typing import Optional
import httpx
import structlog

logger = structlog.get_logger()

# Page size: 8.5 x 11 inches in points (1 inch = 72 points)
PAGE_W = 8.5 * 72   # 612
PAGE_H = 11.0 * 72  # 792
MARGIN = 0.5 * 72   # 36pt = 0.5 inch
BORDER_INSET = 0.35 * 72  # 25pt inset from margin for decorative border (cover only)


# ─── Theme border definitions ─────────────────────────────────────────────────

def _draw_border_ocean(c, x, y, w, h):
    """Wavy ocean border with bubble corners."""
    from reportlab.lib.colors import HexColor
    c.saveState()
    c.setStrokeColor(HexColor("#5BA4CF"))
    c.setLineWidth(2.5)

    # Draw wavy lines on top and bottom
    wave_amp = 4
    wave_len = 18
    for side in ["top", "bottom"]:
        base_y = y + h if side == "top" else y
        points = []
        num_waves = int(w / wave_len)
        for i in range(num_waves + 1):
            px = x + (i * wave_len)
            if px > x + w:
                px = x + w
            direction = 1 if i % 2 == 0 else -1
            if side == "bottom":
                direction *= -1
            py = base_y + (wave_amp * direction)
            points.append((px, py))
        if len(points) >= 2:
            p = c.beginPath()
            p.moveTo(points[0][0], points[0][1])
            for px, py in points[1:]:
                p.lineTo(px, py)
            c.drawPath(p, stroke=1, fill=0)

    # Side lines (straight with slight style)
    c.setLineWidth(2)
    c.line(x, y, x, y + h)
    c.line(x + w, y, x + w, y + h)

    # Corner bubbles
    c.setFillColor(HexColor("#5BA4CF"))
    for corner_x, corner_y in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
        c.circle(corner_x, corner_y, 5, fill=1, stroke=0)
        c.circle(corner_x + (8 if corner_x == x else -8),
                corner_y + (6 if corner_y == y else -6), 3, fill=1, stroke=0)

    c.restoreState()


def _draw_border_fantasy(c, x, y, w, h):
    """Star and sparkle border for fantasy themes."""
    from reportlab.lib.colors import HexColor
    c.saveState()
    c.setStrokeColor(HexColor("#9B59B6"))
    c.setLineWidth(2)
    c.roundRect(x, y, w, h, 10, fill=0, stroke=1)

    # Inner decorative line
    c.setStrokeColor(HexColor("#D5A6E6"))
    c.setLineWidth(1)
    c.roundRect(x + 5, y + 5, w - 10, h - 10, 8, fill=0, stroke=1)

    # Star decorations at corners and midpoints
    c.setFillColor(HexColor("#9B59B6"))
    star_positions = [
        (x + 2, y + 2), (x + w - 2, y + 2),
        (x + 2, y + h - 2), (x + w - 2, y + h - 2),
        (x + w / 2, y + 2), (x + w / 2, y + h - 2),
    ]
    for sx, sy in star_positions:
        _draw_small_star(c, sx, sy, 6)

    c.restoreState()


def _draw_border_animals(c, x, y, w, h):
    """Paw print border for animal themes."""
    from reportlab.lib.colors import HexColor
    c.saveState()
    c.setStrokeColor(HexColor("#8B6914"))
    c.setLineWidth(2)
    c.roundRect(x, y, w, h, 8, fill=0, stroke=1)

    # Paw prints along top and bottom
    c.setFillColor(HexColor("#C4A46C"))
    spacing = 60
    for px in range(int(x + 30), int(x + w - 30), spacing):
        _draw_paw_print(c, px, y + h + 2, 4)
        _draw_paw_print(c, px + spacing // 2, y - 6, 4)

    c.restoreState()


def _draw_border_default(c, x, y, w, h):
    """Clean double-line frame for any theme."""
    from reportlab.lib.colors import HexColor
    c.saveState()

    # Outer line
    c.setStrokeColor(HexColor("#4A90D9"))
    c.setLineWidth(2.5)
    c.roundRect(x, y, w, h, 6, fill=0, stroke=1)

    # Inner line
    c.setStrokeColor(HexColor("#A8CBE8"))
    c.setLineWidth(1)
    c.roundRect(x + 5, y + 5, w - 10, h - 10, 4, fill=0, stroke=1)

    # Corner dots
    c.setFillColor(HexColor("#4A90D9"))
    for cx, cy in [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]:
        c.circle(cx, cy, 4, fill=1, stroke=0)

    c.restoreState()


# ─── Helper drawing functions ─────────────────────────────────────────────────

def _draw_small_star(c, x, y, size):
    """Draw a small 5-pointed star at (x, y)."""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.4
        px = x + r * math.cos(angle)
        py = y + r * math.sin(angle)
        points.append((px, py))
    if points:
        p = c.beginPath()
        p.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            p.lineTo(px, py)
        p.close()
        c.drawPath(p, fill=1, stroke=0)


def _draw_paw_print(c, x, y, size):
    """Draw a simple paw print at (x, y)."""
    # Main pad
    c.circle(x, y, size * 0.8, fill=1, stroke=0)
    # Toe pads
    offsets = [(-size, size * 1.2), (0, size * 1.5), (size, size * 1.2)]
    for ox, oy in offsets:
        c.circle(x + ox, y + oy, size * 0.45, fill=1, stroke=0)


def _get_border_drawer(theme: str):
    """Return the appropriate border drawing function for a theme."""
    theme_lower = theme.lower()
    if theme_lower in ("ocean", "sea", "underwater", "beach", "pirate"):
        return _draw_border_ocean
    elif theme_lower in ("fantasy", "fairy", "magic", "unicorn", "dragon", "castle"):
        return _draw_border_fantasy
    elif theme_lower in ("animals", "safari", "jungle", "zoo", "pets", "farm"):
        return _draw_border_animals
    elif theme_lower in ("dinosaur", "dino", "prehistoric"):
        return _draw_border_animals  # Reuse paw-like prints for dinos
    else:
        return _draw_border_default


# ─── Image autocrop ──────────────────────────────────────────────────────────

def _autocrop_image(img_path: str) -> str:
    """
    Crop white margins from image so the subject fills the frame.
    Saves cropped version to a sibling path, returns new path.
    Handles both white-background PNGs and PNGs with transparency.
    """
    from PIL import Image, ImageOps

    img = Image.open(img_path).convert("RGB")
    gray = img.convert("L")

    # Invert so content = white, background = black
    inverted = ImageOps.invert(gray)
    bbox = inverted.getbbox()

    if bbox:
        w, h = img.size
        # Only crop bottom and sides, never crop the top
        # This preserves sky/water/background at top
        bbox = (
            max(0, bbox[0] - int(w * 0.02)),  # left: 2% padding
            0,                                  # top: always 0
            min(w, bbox[2] + int(w * 0.02)),  # right: 2% padding
            min(h, bbox[3] + int(h * 0.03))   # bottom: 3% padding
        )
        img = img.crop(bbox)

    cropped_path = img_path.replace(".png", "_cropped.png")
    if cropped_path == img_path:
        # Fallback if filename doesn't end in .png
        cropped_path = img_path + "_cropped.png"
    img.save(cropped_path)
    return cropped_path


# ─── PDF building ─────────────────────────────────────────────────────────────

async def build_pdf(
    book_id: str,
    title: str,
    page_image_urls: list[str],
    age_range: str,
    theme: str = "default",
    cover_hero_path: Optional[str] = None,
) -> bytes:
    """
    Build a print-ready PDF with full-page cover hero image and clean
    image-only coloring pages. Images are streamed to temp disk.
    """
    if len(page_image_urls) > 20:
        raise ValueError(f"Page count {len(page_image_urls)} exceeds maximum of 20")

    tmp_dir = tempfile.mkdtemp(prefix=f"tailormade_{book_id}_")
    logger.info("pdf_build_start", book_id=book_id, pages=len(page_image_urls), tmp_dir=tmp_dir)

    try:
        # Download all images to disk concurrently
        image_paths = await _download_images_to_disk(page_image_urls, tmp_dir)

        # Render PDF in thread pool (reportlab is sync)
        pdf_bytes = await asyncio.get_event_loop().run_in_executor(
            None, _render_pdf, title, age_range, image_paths,
            cover_hero_path, theme
        )

        logger.info("pdf_build_success", book_id=book_id, pdf_size_kb=len(pdf_bytes) // 1024)
        return pdf_bytes

    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            logger.info("pdf_temp_cleanup", tmp_dir=tmp_dir)
        except Exception:
            pass


async def _download_images_to_disk(urls: list[str], tmp_dir: str) -> list[str]:
    """Download all images concurrently to temp disk files."""

    async def download_one(url: str, index: int) -> str:
        path = os.path.join(tmp_dir, f"page_{index:03d}.png")
        if url.startswith("file://") or os.path.exists(url):
            return url
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            with open(path, "wb") as f:
                f.write(response.content)
        return path

    paths = await asyncio.gather(
        *[download_one(url, i) for i, url in enumerate(urls)]
    )
    return list(paths)


def _render_pdf(
    title: str,
    age_range: str,
    image_paths: list[str],
    cover_hero_path: Optional[str],
    theme: str,
) -> bytes:
    """Render PDF: cover page with hero image, then clean image-only coloring pages."""
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))

    # ── COVER PAGE (hero image + title overlay) ──
    _draw_cover(c, title, age_range, cover_hero_path)
    c.showPage()

    # ── COLORING PAGES (image only — no text, no borders, no page numbers) ──
    for img_path in image_paths:
        _draw_image_page(c, img_path)
        c.showPage()

    c.save()
    return buffer.getvalue()


def _draw_cover(c, title: str, age_range: str, cover_hero_path: Optional[str]):
    """
    Cover layout:
    - Cover hero image fills the ENTIRE page as background
    - Semi-transparent white rounded rectangle in the top-third
    - Title, subtitle, and age badge inside the overlay box
    - Background art visible around and beneath the box
    """
    from reportlab.lib.colors import HexColor, white, Color
    from reportlab.lib.utils import ImageReader

    # ── Full-page hero background image ──
    logger.info("draw_cover_called",
               cover_hero_path=cover_hero_path,
               path_exists=os.path.exists(cover_hero_path) if cover_hero_path else False)
    if cover_hero_path:
        try:
            # Autocrop then draw edge-to-edge
            cropped = _autocrop_image(cover_hero_path)
            img = ImageReader(cropped)
            c.drawImage(cropped, 0, 0, width=PAGE_W, height=PAGE_H,
                       preserveAspectRatio=False)
        except Exception as e:
            logger.warning("cover_hero_load_failed", error=str(e))
            # Fallback: light background
            c.setFillColor(HexColor("#F8FAFF"))
            c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    else:
        # No hero image—use a clean light background
        c.setFillColor(HexColor("#F8FAFF"))
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ── Semi-transparent white overlay box in the top-third ──
    box_margin = MARGIN + 20
    box_w = PAGE_W - 2 * box_margin
    box_h = PAGE_H * 0.22
    box_x = box_margin
    box_y = PAGE_H - MARGIN - box_h - 30  # Top area with small padding

    # Semi-transparent white fill (85% opacity)
    c.saveState()
    c.setFillColor(Color(1, 1, 1, alpha=0.85))
    c.setStrokeColor(Color(1, 1, 1, alpha=0.4))
    c.setLineWidth(1.5)
    c.roundRect(box_x, box_y, box_w, box_h, 16, fill=1, stroke=1)
    c.restoreState()

    # ── Title text ──
    c.setFillColor(HexColor("#1A1A2E"))
    c.setFont("Helvetica-Bold", 30)
    # Word wrap if title is long (>25 chars)
    if len(title) > 25:
        words = title.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        _draw_centered_text(c, line1, box_y + box_h * 0.72)
        _draw_centered_text(c, line2, box_y + box_h * 0.52)
    else:
        _draw_centered_text(c, title, box_y + box_h * 0.65)

    # ── Subtitle ──
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica", 13)
    _draw_centered_text(c, "A personalized coloring book", box_y + box_h * 0.32)

    # ── Age badge ──
    badge_w, badge_h = 86, 26
    badge_x = PAGE_W / 2 - badge_w / 2
    badge_y = box_y + box_h * 0.08
    c.setFillColor(HexColor("#2B6CEE"))
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 10, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    _draw_centered_text(c, f"Ages {age_range}", badge_y + 8)


def _draw_image_page(c, img_path: str):
    """
    Draw one coloring page.
    ONLY the image — no text, no borders, no page numbers, no captions.
    Children color these pages. Any printed elements ruin the coloring experience.
    Images go edge-to-edge with zero margins.
    """
    # Autocrop white margins so subject fills the page
    img_path = _autocrop_image(img_path)

    from reportlab.lib.utils import ImageReader

    # Full page — zero margins for edge-to-edge coloring pages
    avail_w = PAGE_W
    avail_h = PAGE_H

    try:
        img = ImageReader(img_path)
        img_w, img_h = img.getSize()

        # Scale to fill 100% of page — true edge-to-edge
        scale = min(avail_w / img_w, avail_h / img_h)
        draw_w = img_w * scale
        draw_h = img_h * scale

        # Center on page
        x = (PAGE_W - draw_w) / 2
        y = (PAGE_H - draw_h) / 2

        c.drawImage(img_path, x, y, width=draw_w, height=draw_h,
                   preserveAspectRatio=True)

    except Exception as e:
        logger.warning("pdf_image_load_failed", path=img_path, error=str(e))


def _draw_centered_text(c, text: str, y: float):
    """Draw text centered horizontally on the page. Used by cover only."""
    c.drawCentredString(PAGE_W / 2, y, text)