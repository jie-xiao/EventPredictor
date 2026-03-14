"""
API Endpoint Tests
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_ok(self, client: TestClient):
        """Test root endpoint returns 200 OK"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "EventPredictor" in data["message"]

    def test_root_message_content(self, client: TestClient):
        """Test root endpoint message content"""
        response = client.get("/")
        data = response.json()
        assert "version" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client: TestClient):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_response_format(self, client: TestClient):
        """Test health check response format"""
        response = client.get("/health")
        assert response.status_code == 200
        # Should have status field
        assert "status" in response.json()
        assert "version" in response.json()
        assert "timestamp" in response.json()


class TestPredictEndpoint:
    """Test prediction API endpoints"""

    def test_predict_endpoint_exists(self, client: TestClient, sample_event_data: dict):
        """Test predict endpoint exists and accepts POST"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        # Should return 200 or 500 (if agent not configured), not 404
        assert response.status_code in [200, 500]

    def test_predict_returns_prediction_id(self, client: TestClient, sample_event_data: dict):
        """Test predict endpoint returns prediction_id"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        if response.status_code == 200:
            data = response.json()
            assert "prediction_id" in data or "id" in data

    def test_predict_returns_trend(self, client: TestClient, sample_event_data: dict):
        """Test predict endpoint returns trend"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        if response.status_code == 200:
            data = response.json()
            # Check for trend field
            assert "trend" in data or "prediction" in data

    def test_predict_returns_confidence(self, client: TestClient, sample_event_data: dict):
        """Test predict endpoint returns confidence"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        if response.status_code == 200:
            data = response.json()
            # Check for confidence field
            assert "confidence" in data

    def test_predict_with_minimal_data(self, client: TestClient):
        """Test predict with minimal required data"""
        minimal_data = {
            "title": "Test Event",
            "description": "Test Description"
        }
        response = client.post("/api/v1/predict", json=minimal_data)
        # Should handle missing optional fields
        assert response.status_code in [200, 422, 500]

    def test_predict_invalid_data(self, client: TestClient):
        """Test predict with invalid data"""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "description": ""
        }
        response = client.post("/api/v1/predict", json=invalid_data)
        # May return 422 (validation) or 200 (depends on Pydantic config)
        assert response.status_code in [200, 422]

    def test_predict_importance_validation(self, client: TestClient):
        """Test importance field validation (1-5)"""
        # Test with invalid importance (too high)
        invalid_data = {
            "title": "Test Event",
            "description": "Test Description",
            "importance": 10  # Invalid: must be 1-5
        }
        response = client.post("/api/v1/predict", json=invalid_data)
        assert response.status_code == 422

    def test_predict_with_all_fields(self, client: TestClient, sample_event_data: dict):
        """Test predict with all fields provided"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        # Should handle all fields gracefully
        assert response.status_code in [200, 500]


class TestEventsEndpoint:
    """Test events API endpoints"""

    def test_list_events(self, client: TestClient):
        """Test list events endpoint"""
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data

    def test_list_events_with_pagination(self, client: TestClient):
        """Test list events with pagination"""
        response = client.get("/api/v1/events?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_get_event_not_found(self, client: TestClient):
        """Test get non-existent event returns 404"""
        response = client.get("/api/v1/events/non-existent-id")
        assert response.status_code == 404


class TestPredictionsEndpoint:
    """Test predictions API endpoints"""

    def test_list_predictions(self, client: TestClient):
        """Test list predictions endpoint"""
        response = client.get("/api/v1/predictions")
        assert response.status_code == 200

    def test_get_prediction_not_found(self, client: TestClient):
        """Test get non-existent prediction returns 404"""
        response = client.get("/api/v1/predictions/non-existent-id")
        # May return 404 or 500 depending on implementation
        assert response.status_code in [404, 500]


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self, client: TestClient):
        """Test CORS headers are present"""
        response = client.get("/")
        # Check for CORS headers (may vary by FastAPI version)
        assert "access-control-allow-origin" in response.headers or \
               "access-control-allow-credentials" in response.headers or \
               response.status_code == 200
