
from fastapi.testclient import TestClient

from MatchCV.Api.main import app


class TestSwaggerSecurity:
    def test_docs_rejects_missing_credentials(self, monkeypatch):
        monkeypatch.setenv("SWAGGER_USERNAME", "swagger-test")
        monkeypatch.setenv("SWAGGER_PASSWORD", "senha-de-teste-forte")

        client = TestClient(app)

        response = client.get("/docs")

        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Basic"

    def test_docs_accepts_valid_credentials(self, monkeypatch):
        monkeypatch.setenv("SWAGGER_USERNAME", "swagger-test")
        monkeypatch.setenv("SWAGGER_PASSWORD", "senha-de-teste-forte")

        client = TestClient(app)

        response = client.get(
            "/docs",
            auth=("swagger-test", "senha-de-teste-forte"),
        )

        assert response.status_code == 200
        assert "Swagger UI" in response.text

    def test_openapi_rejects_invalid_credentials(self, monkeypatch):
        monkeypatch.setenv("SWAGGER_USERNAME", "swagger-test")
        monkeypatch.setenv("SWAGGER_PASSWORD", "senha-de-teste-forte")

        client = TestClient(app)

        response = client.get(
            "/openapi.json",
            auth=("swagger-test", "senha-errada"),
        )

        assert response.status_code == 401

    def test_redoc_requires_credentials(self, monkeypatch):
        monkeypatch.setenv("SWAGGER_USERNAME", "swagger-test")
        monkeypatch.setenv("SWAGGER_PASSWORD", "senha-de-teste-forte")

        client = TestClient(app)

        response = client.get("/redoc")

        assert response.status_code == 401

    def test_health_remains_public(self):
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_docs_are_disabled_without_configuration(self, monkeypatch):
        monkeypatch.delenv("SWAGGER_USERNAME", raising=False)
        monkeypatch.delenv("SWAGGER_PASSWORD", raising=False)

        client = TestClient(app)

        response = client.get("/docs")

        assert response.status_code == 404
