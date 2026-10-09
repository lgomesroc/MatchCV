
from fastapi.testclient import TestClient

from MatchCV.Api.main import app


class TestApiContract:
    def test_analysis_endpoint_is_documented_in_openapi(self):
        client = TestClient(app)

        response = client.get("/openapi.json")

        assert response.status_code == 200

        schema = response.json()
        assert "/api/v1/analysis/resume" in schema["paths"]
        assert "post" in schema["paths"]["/api/v1/analysis/resume"]

    def test_health_endpoint_is_documented_in_openapi(self):
        client = TestClient(app)

        response = client.get("/openapi.json")

        assert response.status_code == 200

        schema = response.json()
        assert "/health" in schema["paths"]
        assert "get" in schema["paths"]["/health"]

    def test_cors_allows_angular_frontend_origin(self):
        client = TestClient(app)

        response = client.options(
            "/api/v1/analysis/resume",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == (
            "http://localhost:4200"
        )
