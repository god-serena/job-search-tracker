import uuid
from pathlib import Path
from typing import List
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/applications", tags=["application documents"])
library_router = APIRouter(prefix="/api/application-documents", tags=["application documents"])
MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/octet-stream"},
    ".doc": {"application/msword", "application/octet-stream"},
    ".rtf": {"application/rtf", "text/rtf", "application/octet-stream"},
    ".odt": {"application/vnd.oasis.opendocument.text", "application/octet-stream"},
    ".txt": {"text/plain", "application/octet-stream"},
}


def safe_filename(name: str) -> str:
    # Never use a client-provided path as a server path or response header verbatim.
    cleaned = Path(name.replace("\\", "/")).name
    return "".join(ch for ch in cleaned if ch.isprintable() and ch not in '\"\r\n')[:255] or "document"


@library_router.get("/", response_model=List[schemas.ApplicationDocumentLibraryItem])
def list_all_application_documents(db: Session = Depends(get_db)):
    return crud.get_all_application_documents(db)


@router.post("/{application_id}/documents", response_model=schemas.ApplicationDocumentOut, status_code=201)
async def upload_application_document(
    application_id: uuid.UUID,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not crud.get_application(db, application_id):
        raise HTTPException(status_code=404, detail="Application not found")
    if document_type not in {"resume", "cover_letter"}:
        raise HTTPException(status_code=400, detail="document_type must be resume or cover_letter")
    filename = safe_filename(file.filename or "")
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type. Use PDF, DOC/DOCX, RTF, ODT, or TXT.")
    media_type = (file.content_type or "application/octet-stream").split(";")[0].strip().lower()
    if media_type not in ALLOWED_TYPES[extension]:
        raise HTTPException(status_code=415, detail="File content type does not match a supported document format")
    content = await file.read(MAX_DOCUMENT_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit")
    return crud.create_application_document(
        db, application_id, document_type, filename, media_type, content
    )


@router.get("/{application_id}/documents", response_model=List[schemas.ApplicationDocumentOut])
def list_application_documents(application_id: uuid.UUID, db: Session = Depends(get_db)):
    if not crud.get_application(db, application_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return crud.get_application_documents(db, application_id)


@router.get("/{application_id}/documents/{document_id}/download")
def download_application_document(application_id: uuid.UUID, document_id: uuid.UUID, db: Session = Depends(get_db)):
    document = crud.get_application_document(db, document_id)
    if not document or document.application_id != application_id:
        raise HTTPException(status_code=404, detail="Document not found")
    filename = safe_filename(document.filename)
    ascii_filename = filename.encode("ascii", "replace").decode("ascii").replace("?", "_")
    return Response(
        content=document.content,
        media_type=document.media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{quote(filename)}",
            "X-Content-Type-Options": "nosniff",
        },
    )
