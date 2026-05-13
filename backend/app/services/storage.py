import asyncio
from urllib.parse import unquote, urlparse

import boto3
from botocore.config import Config
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = None

IMAGE_URL_EXPIRY_SECONDS = 3600
PDF_URL_EXPIRY_SECONDS = 86400


def _get_r2_client():
    """Return an R2 S3-compatible client."""
    current_settings = settings or get_settings()
    return boto3.client(
        "s3",
        endpoint_url=f"https://{current_settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=current_settings.r2_access_key_id,
        aws_secret_access_key=current_settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def get_r2_client():
    """Public alias used by services that need direct R2 access."""
    return _get_r2_client()


def get_object_key(*parts: object) -> str:
    """Build a normalized R2 object key from path parts."""
    return "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))


def get_book_page_key(book_id: str, page_number: int) -> str:
    return get_object_key("books", book_id, f"page_{page_number:03d}.png")


def get_book_pdf_key(book_id: str) -> str:
    return get_object_key("books", book_id, "book.pdf")


def object_key_from_url(value: str | None) -> str | None:
    """Convert an old public R2 URL or a signed R2 URL back to an object key."""
    if not value:
        return None
    if not value.startswith(("http://", "https://")):
        return value.lstrip("/")

    parsed = urlparse(value)
    path = unquote(parsed.path.lstrip("/"))
    if path:
        return path
    return None


def generate_presigned_url(object_key: str, expiry_seconds: int = IMAGE_URL_EXPIRY_SECONDS) -> str:
    """Generate a time-limited signed URL for a private R2 object."""
    current_settings = settings or get_settings()
    client = get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": current_settings.r2_bucket_name, "Key": object_key},
        ExpiresIn=expiry_seconds,
    )


def signed_url_for_key_or_url(value: str | None, expiry_seconds: int = IMAGE_URL_EXPIRY_SECONDS) -> str | None:
    """Return a signed URL for an R2 key or legacy R2 URL."""
    key = object_key_from_url(value)
    if not key:
        return None
    try:
        return generate_presigned_url(key, expiry_seconds=expiry_seconds)
    except Exception as e:
        logger.warning("presigned_url_failed", object_key=key, error=str(e))
        return None


def _content_type_for_filename(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        return "image/jpeg"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".pdf"):
        return "application/pdf"
    return "image/png"


async def upload_image(image_bytes: bytes, book_id: str, page_number: int) -> str:
    """Upload a page image to R2 and return the object key."""
    key = get_book_page_key(book_id, page_number)
    current_settings = settings or get_settings()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _get_r2_client().put_object(
            Bucket=current_settings.r2_bucket_name,
            Key=key,
            Body=image_bytes,
            ContentType="image/png",
        ),
    )
    logger.info("image_uploaded", key=key)
    return key


async def upload_pdf(pdf_bytes: bytes, book_id: str) -> str:
    """Upload the final PDF to R2 and return the object key."""
    key = get_book_pdf_key(book_id)
    current_settings = settings or get_settings()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _get_r2_client().put_object(
            Bucket=current_settings.r2_bucket_name,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        ),
    )
    logger.info("pdf_uploaded", key=key)
    return key


async def upload_character_asset(image_bytes: bytes, character_id: str, filename: str) -> str:
    """Upload a character asset to R2 and return the object key."""
    key = get_object_key("characters", character_id, filename)
    current_settings = settings or get_settings()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _get_r2_client().put_object(
            Bucket=current_settings.r2_bucket_name,
            Key=key,
            Body=image_bytes,
            ContentType=_content_type_for_filename(filename),
        ),
    )
    logger.info("character_asset_uploaded", key=key)
    return key


async def get_object_bytes(object_key: str) -> bytes:
    """Read a private R2 object into memory."""
    loop = asyncio.get_event_loop()
    current_settings = settings or get_settings()

    def _read() -> bytes:
        response = _get_r2_client().get_object(Bucket=current_settings.r2_bucket_name, Key=object_key)
        return response["Body"].read()

    return await loop.run_in_executor(None, _read)


async def delete_book_assets(book_id: str) -> None:
    """Delete all R2 objects under books/{book_id}/."""
    prefix = get_object_key("books", book_id) + "/"
    loop = asyncio.get_event_loop()
    current_settings = settings or get_settings()

    def _delete():
        client = _get_r2_client()
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=current_settings.r2_bucket_name, Prefix=prefix):
            objects = page.get("Contents", [])
            if objects:
                client.delete_objects(
                    Bucket=current_settings.r2_bucket_name,
                    Delete={"Objects": [{"Key": o["Key"]} for o in objects]},
                )

    await loop.run_in_executor(None, _delete)
    logger.info("book_assets_deleted", book_id=book_id, prefix=prefix)


async def delete_character_assets(character_id: str) -> None:
    """Delete all R2 objects under characters/{character_id}/."""
    prefix = get_object_key("characters", character_id) + "/"
    loop = asyncio.get_event_loop()
    current_settings = settings or get_settings()

    def _delete():
        client = _get_r2_client()
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=current_settings.r2_bucket_name, Prefix=prefix):
            objects = page.get("Contents", [])
            if objects:
                client.delete_objects(
                    Bucket=current_settings.r2_bucket_name,
                    Delete={"Objects": [{"Key": o["Key"]} for o in objects]},
                )

    await loop.run_in_executor(None, _delete)
    logger.info("character_assets_deleted", character_id=character_id, prefix=prefix)
