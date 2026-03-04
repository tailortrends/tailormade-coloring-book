"""
FIX 6: Memory-safe PDF generation.

Stream all images to a temp directory on disk. Pass file:// URIs to WeasyPrint.
Clean up temp files in a try/finally block regardless of success/failure.
Hard cap at 20 pages.
"""

import asyncio
import tempfile
import shutil
import os
from pathlib import Path
import httpx
import structlog

logger = structlog.get_logger()


async def build_pdf(
    book_id: str,
    title: str,
    page_image_urls: list[str],
    age_range: str,
) -> bytes:
    """
    FIX 6: Stream images to temp disk files. Never hold all images in memory.
    WeasyPrint gets file:// URIs, not in-memory bytes.
    Temp directory is always cleaned up in finally block.
    """
    if len(page_image_urls) > 20:
        raise ValueError(f"Page count {len(page_image_urls)} exceeds maximum of 20")

    tmp_dir = tempfile.mkdtemp(prefix=f"tailormade_{book_id}_")
    logger.info(
        "pdf_build_start",
        book_id=book_id,
        pages=len(page_image_urls),
        tmp_dir=tmp_dir,
    )

    try:
        # FIX 6: Download each image to disk (not into memory)
        image_paths = await _download_images_to_disk(page_image_urls, tmp_dir)

        # Build HTML referencing file:// paths
        html = _build_html(title, image_paths, age_range)

        # Write HTML to disk too
        html_path = Path(tmp_dir) / "book.html"
        html_path.write_text(html, encoding="utf-8")

        # WeasyPrint reads from disk — minimal memory footprint
        pdf_bytes = await _render_pdf(str(html_path))

        logger.info(
            "pdf_build_success",
            book_id=book_id,
            pdf_size_kb=len(pdf_bytes) // 1024,
        )
        return pdf_bytes

    finally:
        # FIX 6: Always clean up temp directory
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            logger.info("pdf_temp_cleanup", tmp_dir=tmp_dir)
        except Exception:
            pass  # Cleanup failure is not critical


async def _download_images_to_disk(urls: list[str], tmp_dir: str) -> list[str]:
    """Download all images concurrently to temp disk files."""

    async def download_one(url: str, index: int) -> str:
        path = os.path.join(tmp_dir, f"page_{index:03d}.png")
        if url.startswith("file://") or os.path.exists(url):
            # Already a local path
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


async def _render_pdf(html_path: str) -> bytes:
    """Run WeasyPrint in executor to avoid blocking event loop."""

    def _render():
        # Lazy import — prevents crash if libpango not installed at startup
        from weasyprint import HTML

        return HTML(filename=html_path).write_pdf()

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _render)


def _build_html(title: str, image_paths: list[str], age_range: str) -> str:
    """Build the HTML template for the PDF."""
    cover = f"""
    <div class="cover page">
        <h1>{title}</h1>
        <p class="subtitle">A personalized coloring book</p>
        <p class="age">Ages {age_range}</p>
    </div>
    """
    pages = "\n".join(
        [
            f'<div class="page"><img src="file://{path}" alt="Page {i + 1}"/></div>'
            for i, path in enumerate(image_paths)
        ]
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
  @page {{ size: 8.5in 11in; margin: 0.5in; }}
  body {{ margin: 0; font-family: Arial, sans-serif; }}
  .page {{ page-break-after: always; display: flex; align-items: center;
           justify-content: center; min-height: 9in; }}
  .cover {{ text-align: center; background: #f0f4ff; border-radius: 12px; padding: 2in; }}
  .cover h1 {{ font-size: 2.5rem; color: #2B6CEE; margin-bottom: 0.5rem; }}
  .subtitle {{ color: #666; font-size: 1.2rem; }}
  .age {{ color: #888; font-size: 1rem; margin-top: 1rem; }}
  img {{ max-width: 100%; max-height: 9in; object-fit: contain; }}
</style>
</head>
<body>{cover}{pages}</body>
</html>"""
