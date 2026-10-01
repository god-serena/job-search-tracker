import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("/", response_model=List[schemas.ApplicationOut])
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_applications(db, status=status)


@router.post("/", response_model=schemas.ApplicationOut, status_code=201)
def create_application(
    application: schemas.ApplicationCreate, db: Session = Depends(get_db)
):
    return crud.create_application(db, application)


@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application(application_id: uuid.UUID, db: Session = Depends(get_db)):
    db_application = crud.get_application(db, application_id)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application


@router.patch("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: uuid.UUID,
    application: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    db_application = crud.update_application(db, application_id, application)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: uuid.UUID, db: Session = Depends(get_db)):
    db_application = crud.delete_application(db, application_id)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    return None
