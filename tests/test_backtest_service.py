# tests/test_backtest_service.py
import pytest
from datetime import datetime, timezone


@pytest.fixture
def sample_predictions():
    return [
        {
            "prediction_id": "pred-001",
            "event_id": "evt-001",
            "event_title": "Test Event 1",
            "predicted_trend": "UP",
            "confidence": 0.75,
            "outcome_status": "correct",
            "predicted_at": "2026-05-01T00:00:00+00:00",
            "resolved_at": "2026-05-08T00:00:00+00:00",
        },
        {
            "prediction_id": "pred-002",
            "event_id": "evt-002",
            "event_title": "Test Event 2",
            "predicted_trend": "DOWN",
            "confidence": 0.60,
            "outcome_status": "incorrect",
            "predicted_at": "2026-05-01T00:00:00+00:00",
            "resolved_at": "2026-05-08T00:00:00+00:00",
        },
        {
            "prediction_id": "pred-003",
            "event_id": "evt-003",
            "event_title": "Test Event 3",
            "predicted_trend": "UP",
            "confidence": 0.90,
            "outcome_status": "correct",
            "predicted_at": "2026-05-01T00:00:00+00:00",
            "resolved_at": "2026-05-08T00:00:00+00:00",
        },
    ]


@pytest.mark.asyncio
async def test_compute_brier_score(sample_predictions):
    from app.services.backtest_service import backtest_service
    brier = backtest_service._compute_brier_score(sample_predictions)
    assert brier is not None
    assert 0.0 <= brier <= 1.0


@pytest.mark.asyncio
async def test_compute_directional_accuracy(sample_predictions):
    from app.services.backtest_service import backtest_service
    acc = backtest_service._compute_directional_accuracy(sample_predictions)
    assert acc is not None
    assert 0.0 <= acc <= 1.0
    # 2 correct out of 3 = ~0.667
    assert abs(acc - 2.0/3.0) < 0.1


@pytest.mark.asyncio
async def test_generate_calibration_curve(sample_predictions):
    from app.services.backtest_service import backtest_service
    curve = backtest_service._generate_calibration_curve(sample_predictions, n_bins=5)
    assert isinstance(curve, list)
    assert len(curve) <= 5
    for point in curve:
        assert "bin_low" in point
        assert "bin_high" in point
        assert "avg_predicted" in point
        assert "avg_actual" in point
        assert "count" in point


@pytest.mark.asyncio
async def test_run_backtest_empty():
    """Backtest with no resolved predictions should return neutral metrics."""
    from app.services.backtest_service import backtest_service
    result = await backtest_service.run_backtest(predictions=[])
    assert result["event_count"] == 0
    assert result["resolved_count"] == 0
    assert result["brier_score"] == 0.0
    assert result["directional_accuracy"] == 0.0
