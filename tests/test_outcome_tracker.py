# tests/test_outcome_tracker.py
import pytest
from datetime import datetime, timezone


@pytest.fixture
def pending_predictions():
    return [
        {
            "prediction_id": "pred-001",
            "event_id": "evt-001",
            "event_title": "Test Event",
            "predicted_trend": "UP",
            "confidence": 0.75,
            "outcome_status": "pending",
            "predicted_at": "2026-05-01T00:00:00+00:00",
        }
    ]


@pytest.mark.asyncio
async def test_check_resolution_pending(pending_predictions):
    from app.services.outcome_tracker import outcome_tracker
    # A prediction from 10 days ago should still be pending if not expired
    result = outcome_tracker._check_single_prediction(pending_predictions[0])
    assert result is not None
    assert "outcome_status" in result


@pytest.mark.asyncio
async def test_resolve_manually():
    from app.services.outcome_tracker import outcome_tracker
    prediction = {
        "prediction_id": "pred-test",
        "event_id": "evt-test",
        "predicted_trend": "UP",
        "confidence": 0.8,
        "outcome_status": "pending",
    }
    resolved = outcome_tracker._apply_resolution(prediction, "correct", "manual")
    assert resolved["outcome_status"] == "correct"
    assert resolved["resolution_source"] == "manual"
    assert resolved["resolved_at"] is not None


@pytest.mark.asyncio
async def test_get_resolution_stats():
    from app.services.outcome_tracker import outcome_tracker
    stats = outcome_tracker._compute_stats([])
    assert stats["total"] == 0
    assert stats["correct"] == 0
    assert stats["accuracy"] == 0.0
