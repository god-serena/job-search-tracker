"""Database-backed coverage for document persistence and application association.

Run from the backend container against its configured test database, e.g.:
`docker compose -f docker-compose.test.yml exec backend-test pytest -q tests/test_application_documents_integration.py`
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Application, ApplicationDocument


@pytest.fixture
def persisted_application():
    db = SessionLocal()
    application = Application(
        company=f"Attachment integration {uuid.uuid4()}", role="Test role"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    try:
        yield application.id
    finally:
        # Delete children explicitly so cleanup remains reliable even when a
        # database has foreign-key cascade enforcement disabled.
        db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == application.id
        ).delete(synchronize_session=False)
        db.delete(application)
        db.commit()
        db.close()


def test_document_upload_is_persisted_listed_and_downloaded(persisted_application):
    content = b"original cover letter contents\n"
    with TestClient(app) as client:
        uploaded = client.post(
            f"/api/applications/{persisted_application}/documents",
            data={"document_type": "cover_letter"},
            files={"file": ("cover-letter.txt", content, "text/plain")},
        )
        assert uploaded.status_code == 201, uploaded.text
        metadata = uploaded.json()
        assert metadata["application_id"] == str(persisted_application)
        assert metadata["document_type"] == "cover_letter"
        assert metadata["filename"] == "cover-letter.txt"

        db = SessionLocal()
        try:
            stored = db.query(ApplicationDocument).filter_by(id=metadata["id"]).one()
            assert stored.application_id == persisted_application
            assert stored.content == content
        finally:
            db.close()

        listed = client.get(f"/api/applications/{persisted_application}/documents")
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()] == [metadata["id"]]
        assert "content" not in listed.json()[0]

        downloaded = client.get(
            f"/api/applications/{persisted_application}/documents/{metadata['id']}/download"
        )
        assert downloaded.status_code == 200
        assert downloaded.content == content
        assert "attachment" in downloaded.headers["content-disposition"]

        rejected = client.post(
            f"/api/applications/{persisted_application}/documents",
            data={"document_type": "resume"},
            files={"file": ("bad.exe", b"not allowed", "application/octet-stream")},
        )
        assert rejected.status_code == 415
