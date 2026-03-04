import boto3
from botocore.config import Config
import asyncio
import structlog
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def _get_r2_client():
    """FIX 5: Credentials always from settings, never hardcoded."""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


async def upload_image(image_bytes: bytes, book_id: str, page_number: int) -> str:
    """Upload a page image to R2, return public URL."""
    key = f"books/{book_id}/page_{page_number:03d}.png"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _get_r2_client().put_object(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Body=image_bytes,
            ContentType="image/png",
        ),
    )
    url = f"{settings.r2_public_url}/{key}"
    logger.info("image_uploaded", key=key, url=url)
    return url


async def upload_pdf(pdf_bytes: bytes, book_id: str) -> str:
    """Upload the final PDF to R2, return public URL."""
    key = f"books/{book_id}/book.pdf"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _get_r2_client().put_object(
            Bucket=settings.r2_bucket_name,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        ),
    )
    url = f"{settings.r2_public_url}/{key}"
    logger.info("pdf_uploaded", key=key, url=url)
    return url
