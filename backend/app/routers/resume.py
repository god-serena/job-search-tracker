from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..extractors import extract_text_from_file

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.get("/", response_model=schemas.ResumeOut)
@router.get("", response_model=schemas.ResumeOut)
def get_resume(db: Session = Depends(get_db)):
    return crud.get_or_create_resume(db)


@router.put("/", response_model=schemas.ResumeOut)
@router.put("", response_model=schemas.ResumeOut)
def update_resume(
    resume_in: schemas.ResumeUpdate, db: Session = Depends(get_db)
):
    return crud.update_resume(db, resume_in.content)


@router.post("/extract-preview")
async def extract_preview(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        text = extract_text_from_file(file.filename or "", file_bytes)
        return {
            "filename": file.filename or "",
            "content": text,
            "char_count": len(text),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload", response_model=schemas.ResumeOut)
async def upload_resume(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    try:
        file_bytes = await file.read()
        text = extract_text_from_file(file.filename or "", file_bytes)
        return crud.update_resume(db, content=text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
