
from fastapi.testclient import TestClient

from MatchCV.Api.main import app


class TestHealthEndpoint:
    def test_health_returns_successful_response(self):
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "MatchCV API",
        }
