import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import ApplicationDocument


@pytest.fixture
def client(monkeypatch):
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr("app.routers.application_documents.crud.get_application", lambda *_: object())
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_upload_lists_and_downloads_original(client, monkeypatch):
    app_id = uuid.uuid4()
    stored = ApplicationDocument(
        id=uuid.uuid4(), application_id=app_id, document_type="resume",
        filename="resume.pdf", media_type="application/pdf", content=b"%PDF-original",
        created_at=datetime.utcnow(),
    )
    monkeypatch.setattr("app.routers.application_documents.crud.create_application_document", lambda *args: stored)
    response = client.post(
        f"/api/applications/{app_id}/documents",
        data={"document_type": "resume"},
        files={"file": ("resume.pdf", b"%PDF-original", "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "resume.pdf"
    assert response.json()["document_type"] == "resume"

    monkeypatch.setattr("app.routers.application_documents.crud.get_application_documents", lambda *_: [stored])
    listed = client.get(f"/api/applications/{app_id}/documents")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert "content" not in listed.json()[0]

    monkeypatch.setattr("app.routers.application_documents.crud.get_application_document", lambda *_: stored)
    downloaded = client.get(f"/api/applications/{app_id}/documents/{stored.id}/download")
    assert downloaded.status_code == 200
    assert downloaded.content == b"%PDF-original"
    assert downloaded.headers["content-type"] == "application/pdf"
    assert "attachment" in downloaded.headers["content-disposition"]


def test_upload_rejects_unsupported_type_and_invalid_document_kind(client):
    app_id = uuid.uuid4()
    unsupported = client.post(
        f"/api/applications/{app_id}/documents",
        data={"document_type": "resume"},
        files={"file": ("resume.exe", b"bad", "application/octet-stream")},
    )
    assert unsupported.status_code == 415

    invalid_kind = client.post(
        f"/api/applications/{app_id}/documents",
        data={"document_type": "portfolio"},
        files={"file": ("resume.pdf", b"%PDF", "application/pdf")},
    )
    assert invalid_kind.status_code == 400


def test_upload_rejects_files_over_10_mib(client):
    app_id = uuid.uuid4()
    response = client.post(
        f"/api/applications/{app_id}/documents",
        data={"document_type": "cover_letter"},
        files={"file": ("letter.txt", b"x" * (10 * 1024 * 1024 + 1), "text/plain")},
    )
    assert response.status_code == 413


def test_download_document_from_different_application_is_denied(client, monkeypatch):
    requested_app_id = uuid.uuid4()
    other_app_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    doc = ApplicationDocument(
        id=doc_id,
        application_id=other_app_id,
        document_type="resume",
        filename="x.pdf",
        media_type="application/pdf",
        content=b"x",
        created_at=datetime.utcnow(),
    )
    monkeypatch.setattr(
        "app.routers.application_documents.crud.get_application_document",
        lambda *_: doc,
    )
    response = client.get(
        f"/api/applications/{requested_app_id}/documents/{doc_id}/download"
    )
    assert response.status_code == 404
