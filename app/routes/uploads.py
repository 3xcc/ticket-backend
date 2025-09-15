from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
import uuid

from app.dependencies.auth import require_admin

router = APIRouter(prefix="/uploads", tags=["Uploads"])

# Directory for template backgrounds
UPLOAD_DIR = Path("uploads/templates")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"image/png", "image/jpeg"}


@router.post("/template-background")
async def upload_template_background(
    file: UploadFile = File(...),
    _ = Depends(require_admin)
):
    """
    Upload a background image for ticket templates.
    Only admins can upload.
    Returns the public URL for the uploaded file.
    """
    # Validate MIME type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(ALLOWED_TYPES)}"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE // (1024 * 1024)} MB"
        )

    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    dest_path = UPLOAD_DIR / filename

    # Save file
    dest_path.write_bytes(content)

    # Return public URL
    public_url = f"/static/template-backgrounds/{filename}"
    return {"url": public_url}
