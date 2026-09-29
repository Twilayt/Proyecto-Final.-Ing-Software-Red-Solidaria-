from app.models import Role

DONOR_PAYLOAD = {
    "organization": "Empresa Alimentos del Norte",
    "phone": "+52 614 123 4567",
    "city": "Chihuahua",
    "resource_type": "Alimentos no perecederos",
    "available_quantity": "25 cajas",
    "notes": "Recolección de lunes a viernes",
}


def test_user_creates_and_lists_own_profile(client, create_user, login_headers):
    create_user(email="donante@example.com")
    headers = login_headers("donante@example.com")

    created = client.post("/api/v1/donors", json=DONOR_PAYLOAD, headers=headers)
    assert created.status_code == 201
    assert created.json()["status"] == "pending"
    assert created.json()["city"] == "Chihuahua"

    own = client.get("/api/v1/donors/me", headers=headers)
    assert own.status_code == 200
    assert len(own.json()) == 1
    assert own.json()[0]["resource_type"] == "Alimentos no perecederos"


def test_admin_lists_filters_and_approves_profile(client, create_user, login_headers):
    create_user(email="donante@example.com")
    create_user(email="admin@example.com", role=Role.ADMIN)
    donor_headers = login_headers("donante@example.com")
    admin_headers = login_headers("admin@example.com")

    profile = client.post("/api/v1/donors", json=DONOR_PAYLOAD, headers=donor_headers).json()
    profile_id = profile["id"]

    listing = client.get("/api/v1/donors?status=pending", headers=admin_headers)
    assert listing.status_code == 200
    assert [item["id"] for item in listing.json()] == [profile_id]

    approved = client.patch(
        f"/api/v1/donors/{profile_id}/status",
        json={"status": "approved"},
        headers=admin_headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_owner_and_admin_access_rules(client, create_user, login_headers):
    create_user(email="owner@example.com")
    create_user(email="other@example.com")
    create_user(email="admin@example.com", role=Role.ADMIN)
    owner_headers = login_headers("owner@example.com")
    other_headers = login_headers("other@example.com")
    admin_headers = login_headers("admin@example.com")

    profile_id = client.post(
        "/api/v1/donors", json=DONOR_PAYLOAD, headers=owner_headers
    ).json()["id"]

    assert client.get(f"/api/v1/donors/{profile_id}", headers=owner_headers).status_code == 200
    assert client.get(f"/api/v1/donors/{profile_id}", headers=other_headers).status_code == 403
    assert client.get(f"/api/v1/donors/{profile_id}", headers=admin_headers).status_code == 200


def test_owner_deletes_profile_and_missing_profile_returns_404(
    client, create_user, login_headers
):
    create_user(email="owner@example.com")
    headers = login_headers("owner@example.com")
    profile_id = client.post("/api/v1/donors", json=DONOR_PAYLOAD, headers=headers).json()["id"]

    deleted = client.delete(f"/api/v1/donors/{profile_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/donors/{profile_id}", headers=headers).status_code == 404


def test_non_owner_cannot_delete_and_user_cannot_approve(
    client, create_user, login_headers
):
    create_user(email="owner@example.com")
    create_user(email="other@example.com")
    owner_headers = login_headers("owner@example.com")
    other_headers = login_headers("other@example.com")
    profile_id = client.post(
        "/api/v1/donors", json=DONOR_PAYLOAD, headers=owner_headers
    ).json()["id"]

    denied_delete = client.delete(f"/api/v1/donors/{profile_id}", headers=other_headers)
    assert denied_delete.status_code == 403
    denied_status = client.patch(
        f"/api/v1/donors/{profile_id}/status",
        json={"status": "approved"},
        headers=owner_headers,
    )
    assert denied_status.status_code == 403


def test_donor_input_rejects_invalid_phone(client, create_user, login_headers):
    create_user(email="donante@example.com")
    invalid = {**DONOR_PAYLOAD, "phone": "<script>alert(1)</script>"}
    response = client.post(
        "/api/v1/donors", json=invalid, headers=login_headers("donante@example.com")
    )
    assert response.status_code == 422
