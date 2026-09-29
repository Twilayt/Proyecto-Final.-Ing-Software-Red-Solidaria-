from fastapi.testclient import TestClient

from app.models import Role


def test_health_and_security_headers(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_register_login_and_read_me(client: TestClient):
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "email": "DONANTE@example.com",
            "full_name": "Ana Donante",
            "password": "ClaveSegura123",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["email"] == "donante@example.com"
    assert registration.json()["role"] == "user"
    assert "password" not in registration.json()

    login = client.post(
        "/api/v1/auth/token",
        data={"username": "donante@example.com", "password": "ClaveSegura123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["full_name"] == "Ana Donante"


def test_registration_validations_and_duplicate(client: TestClient):
    weak = client.post(
        "/api/v1/auth/register",
        json={"email": "x@example.com", "full_name": "X", "password": "debil"},
    )
    assert weak.status_code == 422

    payload = {
        "email": "repetido@example.com",
        "full_name": "Usuario Repetido",
        "password": "ClaveSegura123",
    }
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    duplicate = client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 409


def test_login_rejects_bad_password_and_inactive_user(client: TestClient, create_user):
    create_user(email="activo@example.com")
    bad = client.post(
        "/api/v1/auth/token",
        data={"username": "activo@example.com", "password": "Incorrecta123"},
    )
    assert bad.status_code == 401

    create_user(email="inactivo@example.com", active=False)
    inactive = client.post(
        "/api/v1/auth/token",
        data={"username": "inactivo@example.com", "password": "Segura12345"},
    )
    assert inactive.status_code == 403


def test_protected_route_rejects_missing_or_invalid_token(client: TestClient):
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer token-invalido"}
    )
    assert response.status_code == 401


def test_regular_user_cannot_list_all_donors(
    client: TestClient, create_user, login_headers
):
    create_user(email="normal@example.com", role=Role.USER)
    response = client.get(
        "/api/v1/donors", headers=login_headers("normal@example.com")
    )
    assert response.status_code == 403

