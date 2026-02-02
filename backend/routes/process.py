"""Image processing API routes."""

from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response

from backend.image_processor import ImageProcessor
from backend.utils.file_handling import temp_file, save_upload_file

router = APIRouter(prefix="/api", tags=["processing"])

# Will be set by main.py at startup
processor: Optional[ImageProcessor] = None

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def set_processor(image_processor: ImageProcessor) -> None:
    """Set the image processor instance."""
    global processor
    processor = image_processor


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_loaded": processor.model_loaded if processor else False,
    }


@router.post("/process")
async def process_image(file: UploadFile = File(...)):
    """
    Process an image to remove its background.

    Args:
        file: The uploaded image file.

    Returns:
        PNG image with transparent background.
    """
    if processor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Validate content type
    content_type = file.content_type or ""
    if not processor.is_supported_format(content_type):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {content_type}. Supported: JPEG, PNG, WebP, GIF",
        )

    # Check file size by reading content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Process the image
    try:
        result = processor.remove_background_from_bytes(content)
        return Response(
            content=result,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=processed.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
