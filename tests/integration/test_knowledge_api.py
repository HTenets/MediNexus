"""Integration tests for the knowledge search API.

Guards the page that used to fetch non-existent /api/mock/* endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def headers():
    """Register a throwaway account and return its auth headers."""
    from tests.integration.test_auth_api import _unique_email

    resp = client_post_register(_unique_email())
    assert resp.status_code == 201
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def client_post_register(email: str):
    with TestClient(app) as c:
        return c.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Passw0rd!", "name": "KB", "role": "patient"},
        )


class TestKnowledgeSearch:
    def test_requires_authentication(self, client):
        assert client.get("/api/v1/knowledge/search?q=咳嗽").status_code == 401

    def test_rejects_empty_query(self, client, headers):
        assert client.get("/api/v1/knowledge/search?q=", headers=headers).status_code == 422

    def test_returns_all_three_source_buckets(self, client, headers):
        resp = client.get("/api/v1/knowledge/search?q=发热咳嗽", headers=headers)

        assert resp.status_code == 200
        body = resp.json()
        assert set(body) >= {"query", "cases", "theory", "papers", "total"}
        assert body["total"] > 0, "knowledge search returned no results"

    def test_results_carry_confidence_weights(self, client, headers):
        body = client.get("/api/v1/knowledge/search?q=胸痛", headers=headers).json()

        items = body["cases"] + body["theory"] + body["papers"]
        assert items, "expected at least one result"
        for item in items:
            assert item["title"]
            assert item["content"]
            assert 0 < item["confidence"] <= 1.0

    def test_reports_retrieval_route(self, client, headers):
        body = client.get("/api/v1/knowledge/search?q=头痛", headers=headers).json()

        # No Qdrant in the test environment, so BM25 is the active route.
        assert body["route"] == "bm25"

    def test_query_with_no_corpus_overlap_returns_nothing(self, client, headers):
        # Query must share no tokens with the knowledge base (Latin-only, so
        # the Chinese bi-gram tokenizer cannot match incidental characters).
        body = client.get("/api/v1/knowledge/search?q=xyzzy plugh frobnicate", headers=headers).json()

        assert body["total"] == 0
        assert body["cases"] == []
        assert body["theory"] == []
        assert body["papers"] == []


class TestKnowledgeHealth:
    def test_reports_component_status(self, client):
        body = client.get("/api/v1/knowledge/health").json()

        assert body["bm25"] is True
        assert body["graph"] is True
