"""
Data Model Tests
Tests for Pydantic data models
"""
import pytest
from datetime import datetime
from app.api.models import (
    Event,
    CollectedInfo,
    Analysis,
    Prediction,
    TrendDirection,
    TimeHorizon,
    EventCategory,
    PredictRequest,
    PredictResponse,
    HealthResponse,
    ErrorResponse
)


class TestEventModel:
    """Test Event model"""

    def test_event_creation(self):
        """Test Event model creation"""
        event = Event(
            id="evt-001",
            title="Test Event",
            description="A test event",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Technology",
            importance=4
        )
        
        assert event.id == "evt-001"
        assert event.title == "Test Event"
        assert event.importance == 4

    def test_event_importance_validation(self):
        """Test importance must be 1-5"""
        with pytest.raises(Exception):
            Event(
                id="evt-001",
                title="Test",
                description="Test",
                source="test",
                timestamp="2026-03-12T10:00:00Z",
                category="Other",
                importance=10  # Invalid
            )

    def test_event_default_values(self):
        """Test default values"""
        event = Event(
            id="evt-001",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z"
        )
        
        assert event.category == "Other"
        assert event.importance == 3

    def test_event_json_schema(self):
        """Test Event JSON schema generation"""
        event = Event(
            id="evt-001",
            title="Test Event",
            description="A test event",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Technology",
            importance=4
        )
        
        schema = event.model_json_schema()
        assert "title" in schema
        assert "description" in schema


class TestTrendDirection:
    """Test TrendDirection enum"""

    def test_trend_direction_values(self):
        """Test TrendDirection enum values"""
        assert TrendDirection.UP.value == "UP"
        assert TrendDirection.DOWN.value == "DOWN"
        assert TrendDirection.SIDEWAYS.value == "SIDEWAYS"
        assert TrendDirection.UNCERTAIN.value == "UNCERTAIN"

    def test_trend_direction_from_string(self):
        """Test creating TrendDirection from string"""
        assert TrendDirection("UP") == TrendDirection.UP
        assert TrendDirection("DOWN") == TrendDirection.DOWN


class TestCollectedInfo:
    """Test CollectedInfo model"""

    def test_collected_info_creation(self):
        """Test CollectedInfo creation"""
        info = CollectedInfo(
            basic_info={"key": "value"},
            related_events=[],
            summary="Test summary"
        )
        
        assert info.basic_info["key"] == "value"
        assert info.summary == "Test summary"

    def test_collected_info_defaults(self):
        """Test default values"""
        info = CollectedInfo()
        
        assert info.basic_info == {}
        assert info.related_events == []
        assert info.market_data is None


class TestAnalysis:
    """Test Analysis model"""

    def test_analysis_creation(self):
        """Test Analysis creation"""
        analysis = Analysis(
            impact_scope="Global",
            duration="Medium-term",
            key_factors=["Factor1", "Factor2"],
            sentiment="Positive",
            insights="Test insights"
        )
        
        assert analysis.impact_scope == "Global"
        assert len(analysis.key_factors) == 2


class TestPrediction:
    """Test Prediction model"""

    def test_prediction_creation(self):
        """Test Prediction creation"""
        prediction = Prediction(
            id="pred-001",
            event_id="evt-001",
            trend=TrendDirection.UP,
            confidence=0.75,
            reasoning="Test reasoning",
            time_horizon="Short-term (1-7 days)",
            factors=["Factor1"]
        )
        
        assert prediction.id == "pred-001"
        assert prediction.trend == TrendDirection.UP
        assert prediction.confidence == 0.75

    def test_prediction_confidence_validation(self):
        """Test confidence must be 0-1"""
        with pytest.raises(Exception):
            Prediction(
                id="pred-001",
                event_id="evt-001",
                trend=TrendDirection.UP,
                confidence=1.5,  # Invalid
                reasoning="Test",
                time_horizon="Short-term",
                factors=[]
            )


class TestPredictRequest:
    """Test PredictRequest model"""

    def test_predict_request_creation(self):
        """Test PredictRequest creation"""
        request = PredictRequest(
            title="Test Event",
            description="Test description"
        )
        
        assert request.title == "Test Event"
        assert request.description == "Test description"

    def test_predict_request_defaults(self):
        """Test default values"""
        request = PredictRequest(
            title="Test",
            description="Test"
        )
        
        assert request.source == "manual"
        assert request.category == "Other"
        assert request.importance == 3


class TestPredictResponse:
    """Test PredictResponse model"""

    def test_predict_response_from_prediction(self):
        """Test creating response from Prediction"""
        prediction = Prediction(
            id="pred-001",
            event_id="evt-001",
            trend=TrendDirection.UP,
            confidence=0.75,
            reasoning="Test reasoning",
            time_horizon="Short-term",
            factors=["Factor1"]
        )

        response = PredictResponse.from_prediction(prediction)

        assert response.prediction_id == "pred-001"
        assert response.event_id == "evt-001"
        # trend is converted to Chinese in PredictResponse
        assert response.trend in ["UP", "上涨"]
        # confidence is converted to percentage (0.75 -> 75)
        assert response.confidence == 75


class TestHealthResponse:
    """Test HealthResponse model"""

    def test_health_response_creation(self):
        """Test HealthResponse creation"""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp="2026-03-12T10:00:00Z"
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"


class TestErrorResponse:
    """Test ErrorResponse model - Section 15.2"""

    def test_error_response_creation(self):
        """Test ErrorResponse creation with new format"""
        from app.api.models import ErrorDetail
        response = ErrorResponse(
            error=ErrorDetail(
                code=1006,
                message="Validation error"
            )
        )

        assert response.error.code == 1006
        assert response.error.message == "Validation error"

    def test_error_response_with_detail(self):
        """Test ErrorResponse with detail"""
        from app.api.models import ErrorDetail
        response = ErrorResponse(
            error=ErrorDetail(
                code=1001,
                message="Event not found",
                detail="evt-001 does not exist"
            )
        )

        assert response.error.code == 1001
        assert response.error.message == "Event not found"
        assert response.error.detail == "evt-001 does not exist"
