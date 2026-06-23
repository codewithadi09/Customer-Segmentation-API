from fastapi import HTTPException, UploadFile
from app.logger import logger

# 5MB maximum — generous for a CSV, but blocks anyone trying to crash your server
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv"}
ALLOWED_MIME_TYPES = {"text/csv", "application/csv", "text/plain"}


async def validate_csv_file(file: UploadFile) -> bytes:

    # Check file extension
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(
            "Invalid file extension rejected",
            extra={"filename": filename, "extension": extension}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Only .csv files are accepted. Got: '{extension}'"
        )

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(
            "Invalid MIME type rejected",
            extra={"filename": filename, "content_type": file.content_type}
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: '{file.content_type}'. Must be a CSV file."
        )

    # Read and check file size
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE_BYTES:
        logger.warning(
            "File too large rejected",
            extra={
                "filename": filename,
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
            "filename": filename,
            "size_bytes": len(contents),
            "content_type": file.content_type
        }
    )

    return contents