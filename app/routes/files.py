from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
from sqlmodel import Session
from app.db.session import get_session
from app.models.file import StoredFile
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/files", tags=["Files"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    stored = StoredFile(
        filename=file.filename,
        content_type=file.content_type,
        data=content
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)

    return {
        "id": stored.id,
        "filename": stored.filename,
        "content_type": stored.content_type
    }


@router.get("/{file_id}")
def get_file(
    file_id: str,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)  # or loosen this for public assets
):
    stored = session.get(StoredFile, file_id)
    if not stored:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(content=stored.data, media_type=stored.content_type)
