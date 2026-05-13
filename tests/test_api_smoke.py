from app.core.security import create_access_token


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_screenshot(client):
    response = client.post(
        "/api/v1/upload/screenshot",
        files={"file": ("shot.png", b"binary-data", "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["queued"] is True
    assert "request_id" in body


def test_search(client):
    response = client.get("/api/v1/search", params={"q": "phone"})
    assert response.status_code == 200


def test_admin_pending_requires_auth(client):
    response = client.get("/api/v1/admin/reviews/pending")
    assert response.status_code == 401


def test_admin_pending_with_admin_token(client):
    token = create_access_token(subject="admin@reviewdunia.com", is_admin=True)
    response = client.get(
        "/api/v1/admin/reviews/pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
