"""Integration tests for the authentication API (no-database demo mode)."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def _unique_email() -> str:
    return f"user_{uuid.uuid4().hex[:8]}@test.dev"


class TestRegister:
    def test_register_success(self, client):
        email = _unique_email()
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "测试用户", "role": "patient"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["access_token"]
        assert body["refresh_token"]
        assert body["user"]["email"] == email
        assert body["user"]["name"] == "测试用户"

    def test_register_duplicate_email(self, client):
        email = _unique_email()
        payload = {"email": email, "password": "Passw0rd!", "name": "A", "role": "patient"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 201
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_short_password_rejected(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": _unique_email(), "password": "short", "name": "A", "role": "patient"},
        )
        assert resp.status_code == 422

    def test_register_invalid_email_rejected(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "Passw0rd!", "name": "A", "role": "patient"},
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_with_registered_credentials(self, client):
        email = _unique_email()
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "B", "role": "doctor"},
        )
        resp = client.post(
            "/api/v1/auth/login", json={"email": email, "password": "Passw0rd!", "role": "doctor"}
        )
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "doctor"

    def test_login_wrong_password_rejected(self, client):
        email = _unique_email()
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "C", "role": "patient"},
        )
        resp = client.post(
            "/api/v1/auth/login", json={"email": email, "password": "WrongPass1", "role": "patient"}
        )
        assert resp.status_code == 401

    def test_login_unknown_falls_back_to_demo_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "stranger@test.dev", "password": "whatever", "role": "patient"},
        )
        assert resp.status_code == 200
        assert resp.json()["user"]["id"] == "patient_demo_001"


class TestProtectedRoutes:
    def test_patients_requires_token(self, client):
        resp = client.get("/api/v1/patients")
        assert resp.status_code == 401

    def test_patients_crud_with_token(self, client):
        email = _unique_email()
        reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "D", "role": "patient"},
        )
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        created = client.post(
            "/api/v1/patients",
            headers=headers,
            json={"name": "王五", "gender": "男", "allergies": ["磺胺"]},
        )
        assert created.status_code == 201
        patient_id = created.json()["id"]
        assert created.json()["allergies"] == ["磺胺"]

        listed = client.get("/api/v1/patients", headers=headers)
        assert listed.status_code == 200
        assert any(p["id"] == patient_id for p in listed.json()["items"])
        # Seeded demo patients remain visible (unowned)
        assert any(p["id"] == "patient_demo_001" for p in listed.json()["items"])

        deleted = client.delete(f"/api/v1/patients/{patient_id}", headers=headers)
        assert deleted.status_code == 200
        assert client.get(f"/api/v1/patients/{patient_id}", headers=headers).status_code == 404

    def test_refresh_flow(self, client):
        email = _unique_email()
        reg = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "E", "role": "patient"},
        )
        refresh_token = reg.json()["refresh_token"]
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        assert resp.json()["access_token"]


class TestOwnership:
    def _register(self, client, name):
        reg = client.post(
            "/api/v1/auth/register",
            json={"email": _unique_email(), "password": "Passw0rd!", "name": name, "role": "patient"},
        )
        return {"Authorization": f"Bearer {reg.json()['access_token']}"}

    def test_other_users_patient_is_forbidden(self, client):
        headers_a = self._register(client, "OwnerA")
        headers_b = self._register(client, "OwnerB")

        created = client.post("/api/v1/patients", headers=headers_a, json={"name": "私有患者"})
        patient_id = created.json()["id"]

        assert client.get(f"/api/v1/patients/{patient_id}", headers=headers_b).status_code == 403
        listed_b = client.get("/api/v1/patients", headers=headers_b).json()
        assert all(p["id"] != patient_id for p in listed_b["items"])

    def test_records_of_foreign_patient_forbidden(self, client):
        headers_a = self._register(client, "OwnerA")
        headers_b = self._register(client, "OwnerB")

        created = client.post("/api/v1/patients", headers=headers_a, json={"name": "私有患者"})
        patient_id = created.json()["id"]
        client.post(
            f"/api/v1/records/patient/{patient_id}",
            headers=headers_a,
            json={"diagnosis": "感冒", "plan": "休息"},
        )

        assert (
            client.get(f"/api/v1/records/patient/{patient_id}", headers=headers_b).status_code == 403
        )
