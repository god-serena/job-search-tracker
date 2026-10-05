import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_applications(db: Session, status: Optional[str] = None):
    query = db.query(models.Application)
    if status:
        query = query.filter(models.Application.status == status)
    return query.order_by(models.Application.updated_at.desc()).all()


def get_application(db: Session, application_id: uuid.UUID):
    return (
        db.query(models.Application)
        .filter(models.Application.id == application_id)
        .first()
    )


def create_application(db: Session, application: schemas.ApplicationCreate):
    db_application = models.Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_application(
    db: Session, application_id: uuid.UUID, application: schemas.ApplicationUpdate
):
    db_application = get_application(db, application_id)
    if not db_application:
        return None
    for field, value in application.model_dump(exclude_unset=True).items():
        setattr(db_application, field, value)
    db.commit()
    db.refresh(db_application)
    return db_application


def delete_application(db: Session, application_id: uuid.UUID):
    db_application = get_application(db, application_id)
    if not db_application:
        return None
    db.delete(db_application)
    db.commit()
    return db_application

def get_or_create_resume(db: Session):
    resume = db.query(models.Resume).first()
    if not resume:
        resume = models.Resume(content="")
        db.add(resume)
        db.commit()
        db.refresh(resume)
    return resume


def update_resume(db: Session, content: str):
    resume = get_or_create_resume(db)
    resume.content = content
    db.commit()
    db.refresh(resume)
    return resume


def get_tailored_resumes(db: Session, application_id: uuid.UUID):
    return (
        db.query(models.TailoredResume)
        .filter(models.TailoredResume.application_id == application_id)
        .order_by(models.TailoredResume.created_at.desc())
        .all()
    )


def create_tailored_resume(
    db: Session, application_id: uuid.UUID, data: schemas.TailoredResumeCreate
):
    tailored = models.TailoredResume(
        application_id=application_id,
        content=data.content,
        source=data.source,
    )
    db.add(tailored)
    db.commit()
    db.refresh(tailored)
    return tailored


def get_application_documents(db: Session, application_id: uuid.UUID):
    return (
        db.query(models.ApplicationDocument)
        .filter(models.ApplicationDocument.application_id == application_id)
        .order_by(models.ApplicationDocument.created_at.desc())
        .all()
    )


def create_application_document(db: Session, application_id: uuid.UUID, document_type: str,
                               filename: str, media_type: str, content: bytes):
    document = models.ApplicationDocument(
        application_id=application_id, document_type=document_type,
        filename=filename, media_type=media_type, content=content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_application_document(db: Session, document_id: uuid.UUID):
    return db.query(models.ApplicationDocument).filter(
        models.ApplicationDocument.id == document_id
    ).first()


def get_all_application_documents(db: Session):
    rows = (
        db.query(models.ApplicationDocument, models.Application.company, models.Application.role)
        .join(models.Application, models.Application.id == models.ApplicationDocument.application_id)
        .order_by(models.ApplicationDocument.created_at.desc())
        .all()
    )
    return [
        {
            "id": document.id,
            "application_id": document.application_id,
            "document_type": document.document_type,
            "filename": document.filename,
            "media_type": document.media_type,
            "created_at": document.created_at,
            "company": company,
            "role": role,
        }
        for document, company, role in rows
    ]


def get_application_stats(db: Session) -> schemas.StatsOut:
    applications = db.query(models.Application).all()
    total_applications = len(applications)

    by_status = {
        "wishlist": 0,
        "applied": 0,
        "interviewing": 0,
        "offer": 0,
        "rejected": 0,
        "cancelled": 0,
    }
    active_pipeline = 0
    follow_ups_due = 0
    today = date.today()

    for app in applications:
        status = app.status.value if hasattr(app.status, "value") else str(app.status)
        if status in by_status:
            by_status[status] += 1
        else:
            by_status[status] = 1

        if status in ("applied", "interviewing"):
            active_pipeline += 1

        if (
            app.follow_up_date is not None
            and app.follow_up_date <= today
            and status not in ("offer", "rejected", "cancelled")
        ):
            follow_ups_due += 1

    submitted = total_applications - by_status.get("wishlist", 0) - by_status.get("cancelled", 0)
    if submitted > 0:
        interview_rate = round(
            ((by_status.get("interviewing", 0) + by_status.get("offer", 0)) / submitted) * 100.0,
            1,
        )
        offer_rate = round((by_status.get("offer", 0) / submitted) * 100.0, 1)
    else:
        interview_rate = 0.0
        offer_rate = 0.0

    return schemas.StatsOut(
        total_applications=total_applications,
        by_status=by_status,
        interview_rate=interview_rate,
        offer_rate=offer_rate,
        active_pipeline=active_pipeline,
        follow_ups_due=follow_ups_due,
    )
