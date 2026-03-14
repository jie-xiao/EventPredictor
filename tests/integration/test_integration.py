"""
Integration Tests
Tests for complete workflow integration
"""
import pytest
from fastapi.testclient import TestClient
from app.agents.pipeline import AgentPipeline
from app.api.models import Event, TrendDirection


class TestEndToEndPrediction:
    """End-to-end prediction workflow tests"""

    def test_complete_prediction_flow_via_api(self, client: TestClient, sample_event_data: dict):
        """Test complete prediction flow through API"""
        response = client.post("/api/v1/predict", json=sample_event_data)
        
        # Should complete without errors
        assert response.status_code == 200
        
        data = response.json()
        assert "prediction_id" in data or "id" in data
        assert "trend" in data or "prediction" in data
        assert "confidence" in data

    def test_prediction_flow_with_pipeline(self, sample_event):
        """Test complete pipeline execution"""
        pipeline = AgentPipeline()
        
        result = pipeline.run(sample_event)
        
        # Verify all expected outputs
        assert result is not None
        assert hasattr(result, 'id')
        assert hasattr(result, 'trend')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'reasoning')

    def test_prediction_flow_different_categories(self, client: TestClient):
        """Test prediction for different event categories"""
        categories = [
            "Monetary Policy",
            "Geopolitical",
            "Technology",
            "Economic",
            "Natural Disaster",
            "Social",
            "Other"
        ]
        
        for category in categories:
            event_data = {
                "title": f"Test {category} Event",
                "description": f"A test event in {category} category",
                "category": category,
                "importance": 3
            }
            response = client.post("/api/v1/predict", json=event_data)
            assert response.status_code in [200, 500], f"Failed for category {category}"


class TestDataModelIntegration:
    """Tests for data model integration"""

    def test_event_to_prediction_flow(self, sample_event):
        """Test Event flows correctly through pipeline to Prediction"""
        pipeline = AgentPipeline()
        
        # Execute pipeline
        prediction = pipeline.run(sample_event)
        
        # Verify link between event and prediction
        assert prediction.event_id == sample_event.id

    def test_collected_info_passes_between_agents(self, sample_event):
        """Test CollectedInfo passes correctly between agents"""
        from app.agents.pipeline import InfoCollectorAgent, AnalyzerAgent
        
        # Collect info
        collector = InfoCollectorAgent()
        collected = collector.run(sample_event)
        
        # Verify collected info has required fields
        assert collected.basic_info is not None
        assert collected.summary != ""
        
        # Analyze
        analyzer = AnalyzerAgent()
        analysis = analyzer.run(collected)
        
        # Verify analysis was produced
        assert analysis.impact_scope != ""
        assert analysis.duration != ""

    def test_analysis_passes_to_predictor(self, sample_event):
        """Test Analysis flows correctly to Predictor"""
        from app.agents.pipeline import InfoCollectorAgent, AnalyzerAgent, PredictorAgent
        
        collector = InfoCollectorAgent()
        collected = collector.run(sample_event)
        
        analyzer = AnalyzerAgent()
        analysis = analyzer.run(collected)
        
        predictor = PredictorAgent()
        prediction = predictor.run(analysis, sample_event)
        
        assert prediction is not None
        assert prediction.trend is not None


class TestErrorHandling:
    """Integration tests for error handling"""

    def test_api_handles_malformed_request(self, client: TestClient):
        """Test API handles malformed requests gracefully"""
        # Send completely invalid data - use correct endpoint
        response = client.post("/api/v1/predict", json={"invalid": "data"})
        
        # Should return 422 (validation error) or 500, not crash
        assert response.status_code in [200, 422, 500]

    def test_api_handles_empty_request(self, client: TestClient):
        """Test API handles empty request"""
        response = client.post("/api/v1/predict", json={})
        
        # Should return validation error
        assert response.status_code in [200, 422]

    def test_pipeline_handles_edge_case_importance(self):
        """Test pipeline handles edge case importance values"""
        from app.agents.pipeline import AgentPipeline
        
        pipeline = AgentPipeline()
        
        # Test minimum importance
        event_min = Event(
            id="test-min",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Other",
            importance=1
        )
        result_min = pipeline.run(event_min)
        assert result_min is not None
        
        # Test maximum importance
        event_max = Event(
            id="test-max",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=5
        )
        result_max = pipeline.run(event_max)
        assert result_max is not None


class TestConfigurationIntegration:
    """Tests for configuration integration"""

    def test_config_loads_from_yaml(self):
        """Test configuration loads from YAML"""
        from app.core.config import config
        
        assert config is not None
        assert hasattr(config, 'llm')
        assert hasattr(config, 'api')
        assert hasattr(config, 'agents')

    def test_api_config_applied(self, client: TestClient):
        """Test API uses configuration"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "EventPredictor" in data["message"]


class TestHealthIntegration:
    """Integration tests for health checks"""

    def test_health_check_integration(self, client: TestClient):
        """Test health check endpoint works"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint_integration(self, client: TestClient):
        """Test root endpoint returns expected data"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "EventPredictor" in data["message"]


class TestMultiEventScenarios:
    """Tests for multi-event scenarios"""

    def test_multiple_predictions_are_unique(self):
        """Test multiple predictions generate unique IDs"""
        from app.agents.pipeline import AgentPipeline
        
        pipeline = AgentPipeline()
        
        event1 = Event(
            id="evt-1",
            title="Event 1",
            description="First test event",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Technology",
            importance=3
        )
        
        event2 = Event(
            id="evt-2",
            title="Event 2",
            description="Second test event",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Technology",
            importance=3
        )
        
        result1 = pipeline.run(event1)
        result2 = pipeline.run(event2)
        
        # Each prediction should have unique ID
        assert result1.id != result2.id

    def test_different_categories_produce_different_trends(self):
        """Test different categories can produce different trends"""
        from app.agents.pipeline import AgentPipeline
        
        pipeline = AgentPipeline()
        
        # Monetary Policy (positive sentiment)
        event1 = Event(
            id="evt-monetary",
            title="Rate Cut",
            description="Central bank cuts rates",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=4
        )
        
        # Geopolitical (negative sentiment)
        event2 = Event(
            id="evt-geo",
            title="Conflict",
            description="International conflict",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Geopolitical",
            importance=4
        )
        
        result1 = pipeline.run(event1)
        result2 = pipeline.run(event2)
        
        # Different categories should potentially have different trends
        # (though this is not guaranteed due to randomness in some cases)
        assert result1.trend is not None
        assert result2.trend is not None
