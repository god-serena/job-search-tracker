import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Application, Resume, TailoredResume
from app.prompts import build_tailor_prompt


def test_build_tailor_prompt():
    prompt = build_tailor_prompt(
        resume_text="Experienced Python backend developer",
        role="Senior Backend Engineer",
        company="TechCorp",
        description="We are seeking an engineer with FastAPI experience.",
    )
    assert "Experienced Python backend developer" in prompt
    assert "Senior Backend Engineer" in prompt
    assert "TechCorp" in prompt
    assert "We are seeking an engineer with FastAPI experience." in prompt
    assert "Rewrite my resume to be tailored to this job." in prompt


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_tailor_prompt_app_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    app_id = uuid.uuid4()
    response = client.get(f"/api/applications/{app_id}/tailor-prompt")
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_get_tailor_prompt_missing_description(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Engineer",
        description="",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_app

    response = client.get(f"/api/applications/{app_id}/tailor-prompt")
    assert response.status_code == 400
    assert "Job description is required" in response.json()["detail"]


def test_get_tailor_prompt_missing_master_resume(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Engineer",
        description="Great job posting",
    )
    mock_resume = Resume(id=uuid.uuid4(), content="")

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    response = client.get(f"/api/applications/{app_id}/tailor-prompt")
    assert response.status_code == 400
    assert "Base resume is required" in response.json()["detail"]


def test_get_tailor_prompt_success(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="Acme Corp",
        role="Backend Lead",
        description="Python and FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Master resume with 10 years experience",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    response = client.get(f"/api/applications/{app_id}/tailor-prompt")
    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "Acme Corp" in data["prompt"]
    assert "Backend Lead" in data["prompt"]
    assert "Master resume with 10 years experience" in data["prompt"]


def test_list_tailored_resumes(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(id=app_id, company="Acme", role="Engineer")
    tailored_item = TailoredResume(
        id=uuid.uuid4(),
        application_id=app_id,
        content="Tailored resume text",
        source="chatgpt",
        created_at=datetime.utcnow(),
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == TailoredResume:
            query_mock.filter.return_value.order_by.return_value.all.return_value = [
                tailored_item
            ]
        return query_mock

    mock_db.query.side_effect = query_side_effect

    response = client.get(f"/api/applications/{app_id}/tailored-resumes")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["content"] == "Tailored resume text"
    assert items[0]["source"] == "chatgpt"


def test_create_tailored_resume(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(id=app_id, company="Acme", role="Engineer")

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    payload = {"content": "New tailored text", "source": "claude"}
    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes", json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "New tailored text"
    assert data["source"] == "claude"
    assert "id" in data


@patch("httpx.post")
def test_generate_local_tailored_resume_success(mock_post, client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "choices": [
            {"message": {"role": "assistant", "content": "Local tailored text"}}
        ]
    }
    mock_res.raise_for_status.return_value = None
    mock_post.return_value = mock_res

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local",
        json={"model": "mistral"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Local tailored text"
    assert data["source"] == "local:mistral"
    assert "id" in data

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0].endswith("/v1/chat/completions")
    assert kwargs["json"]["messages"][0]["role"] == "user"
    assert "Base resume content" in kwargs["json"]["messages"][0]["content"]
    assert kwargs["json"]["temperature"] == 0.2


@patch("httpx.post")
def test_generate_local_tailored_resume_reasoning_content(mock_post, client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "Reasoning fallback text",
                }
            }
        ]
    }
    mock_res.raise_for_status.return_value = None
    mock_post.return_value = mock_res

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local",
        json={"model": "Qwythos-9B"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Reasoning fallback text"
    assert data["source"] == "local:Qwythos-9B"


@patch("httpx.post")
def test_generate_local_tailored_resume_default_model(mock_post, client, mock_db, monkeypatch):
    monkeypatch.delenv("LOCAL_LLM_MODEL", raising=False)
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "choices": [
            {"message": {"role": "assistant", "content": "Default model tailored text"}}
        ]
    }
    mock_res.raise_for_status.return_value = None
    mock_post.return_value = mock_res

    # Without body
    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Default model tailored text"
    assert data["source"] == "local:Qwythos-9B"

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0].endswith("/v1/chat/completions")


@patch("httpx.post")
def test_generate_local_tailored_resume_fallback_completion(mock_post, client, mock_db):
    import httpx

    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    # Call 1 (/v1/chat/completions) fails with 404
    mock_err_res = MagicMock()
    mock_err_res.status_code = 404

    # Call 2 (/completion) succeeds
    mock_ok_res = MagicMock()
    mock_ok_res.status_code = 200
    mock_ok_res.json.return_value = {"content": "Llama completion text"}
    mock_ok_res.raise_for_status.return_value = None

    def post_side_effect(url, **kwargs):
        if url.endswith("/v1/chat/completions"):
            raise httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_err_res)
        if url.endswith("/completion"):
            return mock_ok_res
        raise AssertionError(f"Unexpected url {url}")

    mock_post.side_effect = post_side_effect

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local",
        json={"model": "Qwythos-9B"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Llama completion text"
    assert data["source"] == "local:Qwythos-9B"
    assert mock_post.call_count == 2


@patch("httpx.post")
def test_generate_local_tailored_resume_fallback_ollama(mock_post, client, mock_db):
    import httpx

    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    def refresh_side_effect(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.utcnow()

    mock_db.refresh.side_effect = refresh_side_effect

    mock_err_res = MagicMock()
    mock_err_res.status_code = 404

    mock_ok_res = MagicMock()
    mock_ok_res.status_code = 200
    mock_ok_res.json.return_value = {"response": "Ollama generated text"}
    mock_ok_res.raise_for_status.return_value = None

    def post_side_effect(url, **kwargs):
        if url.endswith("/v1/chat/completions"):
            raise httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_err_res)
        if url.endswith("/completion"):
            raise httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=mock_err_res)
        if url.endswith("/api/generate"):
            return mock_ok_res
        raise AssertionError(f"Unexpected url {url}")

    mock_post.side_effect = post_side_effect

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local",
        json={"model": "llama3"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Ollama generated text"
    assert data["source"] == "local:llama3"
    assert mock_post.call_count == 3


@patch("httpx.post")
def test_generate_local_tailored_resume_request_error(mock_post, client, mock_db):
    import httpx

    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    mock_post.side_effect = httpx.ConnectError("Connection refused")

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 502
    assert "Local LLM service error" in response.json()["detail"]


@patch("httpx.post")
def test_generate_local_tailored_resume_status_error(mock_post, client, mock_db):
    import httpx

    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    mock_res = MagicMock()
    mock_res.status_code = 500
    mock_res.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=MagicMock(),
        response=mock_res,
    )
    mock_post.return_value = mock_res

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 502
    assert "Local LLM service error" in response.json()["detail"]


@patch("httpx.post")
def test_generate_local_tailored_resume_empty_response(mock_post, client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(
        id=uuid.uuid4(),
        content="Base resume content",
    )

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {"choices": [{"message": {"content": ""}}], "content": "", "response": ""}
    mock_res.raise_for_status.return_value = None
    mock_post.return_value = mock_res

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 502
    assert "empty response" in response.json()["detail"].lower()


def test_generate_local_tailored_resume_app_not_found(client, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    app_id = uuid.uuid4()
    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_generate_local_tailored_resume_missing_description(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="",
    )
    mock_db.query.return_value.filter.return_value.first.return_value = mock_app

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 400
    assert "Job description is required" in response.json()["detail"]


def test_generate_local_tailored_resume_missing_master_resume(client, mock_db):
    app_id = uuid.uuid4()
    mock_app = Application(
        id=app_id,
        company="TechCorp",
        role="Backend Dev",
        description="FastAPI expertise needed",
    )
    mock_resume = Resume(id=uuid.uuid4(), content="")

    def query_side_effect(model):
        query_mock = MagicMock()
        if model == Application:
            query_mock.filter.return_value.first.return_value = mock_app
        elif model == Resume:
            query_mock.first.return_value = mock_resume
        return query_mock

    mock_db.query.side_effect = query_side_effect

    response = client.post(
        f"/api/applications/{app_id}/tailored-resumes/generate-local"
    )
    assert response.status_code == 400
    assert "Base resume is required" in response.json()["detail"]
