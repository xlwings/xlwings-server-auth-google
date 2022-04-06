from fastapi.testclient import TestClient

from app import settings
from app.core.auth import User, authenticate
from app.main import app

data = {
    "client": "Google Apps Script",
    "version": "dev",
    "book": {"name": "xxx", "active_sheet_index": 0, "selection": "A1"},
    "sheets": [
        {
            "name": "Sheet1",
            "values": [[]],
        },
    ],
}


async def authenticate_override():
    return User(id="123", email="test@test.com", email_verified=True, domain="test.com")


client = TestClient(app)

# app
def test_get_root():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_get_docs():
    response = client.get("/docs")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_get_redoc():
    response = client.get("/redoc")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# hello1
def test_post_myspreadsheet_hello1_no_token():
    # FastAPI unexpectedly returns 403 instead of 401
    response = client.post("/myspreadsheet/hello1", json=data)
    assert response.status_code == 403


def test_post_myspreadsheet_hello1_wrong_token():
    response = client.post(
        "/myspreadsheet/hello1", json=data, headers={"Authorization": "xxx"}
    )
    assert response.status_code == 401


def test_post_hello1_authenticated():
    app.dependency_overrides[authenticate] = authenticate_override
    response = client.post("/myspreadsheet/hello1", json=data)
    assert response.status_code == 200
    app.dependency_overrides = {}


# hello2
def test_post_myspreadsheet_hello2_no_token():
    response = client.post("/myspreadsheet/hello2", json=data)
    assert response.status_code == 403


def test_post_myspreadsheet_hello2_wrong_token():
    response = client.post(
        "/myspreadsheet/hello2", json=data, headers={"Authorization": "xxx"}
    )
    assert response.status_code == 401


def test_post_hello2_authenticated():
    app.dependency_overrides[authenticate] = authenticate_override
    response = client.post("/myspreadsheet/hello2", json=data)
    assert response.status_code == 200
    app.dependency_overrides = {}


# hello3
def test_post_myspreadsheet_hello3_no_token():
    response = client.post("/myspreadsheet/hello3", json=data)
    assert response.status_code == 403


def test_post_myspreadsheet_hello3_wrong_token():
    response = client.post(
        "/myspreadsheet/hello3", json=data, headers={"Authorization": "xxx"}
    )
    assert response.status_code == 401


def test_post_hello3_unauthorized():
    app.dependency_overrides[authenticate] = authenticate_override
    response = client.post("/myspreadsheet/hello3", json=data)
    assert response.status_code == 403
    app.dependency_overrides = {}


def test_post_hello3_authorized():
    settings.group_admin = ["test@test.com"]
    app.dependency_overrides[authenticate] = authenticate_override
    response = client.post("/myspreadsheet/hello3", json=data)
    assert response.status_code == 200
    app.dependency_overrides = {}
