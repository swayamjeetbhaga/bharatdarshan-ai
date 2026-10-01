import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile

MEDIA_ROOT = Path(__file__).resolve().parent.parent.parent / "media"
ATTRACTION_PHOTOS_DIR = MEDIA_ROOT / "attractions"

MAX_PHOTO_BYTES = 8 * 1024 * 1024  # 8 MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

async def save_attraction_photo(attraction_id: int, file: UploadFile) -> str:
    """Saves an uploaded photo to local disk and returns its public URL path
    (to be prefixed with the API origin by the frontend). Validates content
    type and size — the extension and filename are never taken from the
    client, so this can't be used to plant arbitrary files."""
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if not extension:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image type. Use JPEG, PNG, WEBP, or GIF.",
        )

    contents = await file.read()
    if len(contents) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (max 8 MB).")
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file.")

    directory = ATTRACTION_PHOTOS_DIR / str(attraction_id)
    directory.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{extension}"
    (directory / filename).write_bytes(contents)

    return f"/media/attractions/{attraction_id}/{filename}"
