import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Application


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_stats_empty(client, mock_db):
    mock_db.query.return_value.all.return_value = []

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 0
    assert data["by_status"] == {
        "wishlist": 0,
        "applied": 0,
        "interviewing": 0,
        "offer": 0,
        "rejected": 0,
    }
    assert data["interview_rate"] == 0.0
    assert data["offer_rate"] == 0.0
    assert data["active_pipeline"] == 0
    assert data["follow_ups_due"] == 0


def test_get_stats_with_applications(client, mock_db):
    today = date.today()
    past_date = today - timedelta(days=2)
    future_date = today + timedelta(days=5)

    apps = [
        Application(
            id=uuid.uuid4(),
            company="Company A",
            role="Role A",
            status="wishlist",
            follow_up_date=past_date,
        ),
        Application(
            id=uuid.uuid4(),
            company="Company B",
            role="Role B",
            status="applied",
            follow_up_date=today,
        ),
        Application(
            id=uuid.uuid4(),
            company="Company C",
            role="Role C",
            status="interviewing",
            follow_up_date=future_date,
        ),
        Application(
            id=uuid.uuid4(),
            company="Company D",
            role="Role D",
            status="offer",
            follow_up_date=past_date,
        ),
        Application(
            id=uuid.uuid4(),
            company="Company E",
            role="Role E",
            status="rejected",
            follow_up_date=past_date,
        ),
    ]
    mock_db.query.return_value.all.return_value = apps

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()

    assert data["total_applications"] == 5
    assert data["by_status"] == {
        "wishlist": 1,
        "applied": 1,
        "interviewing": 1,
        "offer": 1,
        "rejected": 1,
    }
    assert data["active_pipeline"] == 2
    assert data["follow_ups_due"] == 2
    assert data["interview_rate"] == 50.0
    assert data["offer_rate"] == 25.0


def test_get_stats_only_wishlist(client, mock_db):
    apps = [
        Application(id=uuid.uuid4(), company="Co A", role="Eng", status="wishlist"),
        Application(id=uuid.uuid4(), company="Co B", role="Eng", status="wishlist"),
    ]
    mock_db.query.return_value.all.return_value = apps

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 2
    assert data["by_status"]["wishlist"] == 2
    assert data["interview_rate"] == 0.0
    assert data["offer_rate"] == 0.0
    assert data["active_pipeline"] == 0


def test_get_stats_rounding(client, mock_db):
    # 3 submitted applications: 1 interviewing, 2 applied -> interview_rate = 33.3%
    apps = [
        Application(id=uuid.uuid4(), company="Co 1", role="Eng", status="interviewing"),
        Application(id=uuid.uuid4(), company="Co 2", role="Eng", status="applied"),
        Application(id=uuid.uuid4(), company="Co 3", role="Eng", status="applied"),
    ]
    mock_db.query.return_value.all.return_value = apps

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_applications"] == 3
    assert data["interview_rate"] == 33.3
    assert data["offer_rate"] == 0.0
    assert data["active_pipeline"] == 3
