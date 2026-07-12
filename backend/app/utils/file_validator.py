from pathlib import Path

from fastapi import HTTPException, UploadFile, status

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_upload(file: UploadFile, max_bytes: int) -> None:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type.")
    size = getattr(file, "size", None)
    if size is not None and size > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large.")
