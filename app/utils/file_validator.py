from fastapi import HTTPException, UploadFile
from app.logger import logger

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv"}
ALLOWED_MIME_TYPES = {"text/csv", "application/csv", "text/plain"}


async def validate_csv_file(file: UploadFile) -> bytes:

    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(
            "Invalid file extension rejected",
            extra={"file_name": filename, "extension": extension}  # ← renamed
        )
        raise HTTPException(
            status_code=400,
            detail=f"Only .csv files are accepted. Got: '{extension}'"
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(
            "Invalid MIME type rejected",
            extra={"file_name": filename, "content_type": file.content_type}  # ← renamed
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: '{file.content_type}'. Must be a CSV file."
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE_BYTES:
        logger.warning(
            "File too large rejected",
            extra={
                "file_name": filename,  # ← renamed
                "size_bytes": len(contents),
                "max_bytes": MAX_FILE_SIZE_BYTES
            }
        )
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 5MB. Got: {round(len(contents) / 1024 / 1024, 2)}MB"
        )

    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    logger.info(
        "File validation passed",
        extra={
            "file_name": filename,  # ← renamed
            "size_bytes": len(contents),
            "content_type": file.content_type
        }
    )

    return contents