# tests/test_calibration_service.py
import pytest


@pytest.fixture
def sample_scores():
    return [
        {"confidence": 0.9, "correct": True},
        {"confidence": 0.8, "correct": True},
        {"confidence": 0.7, "correct": True},
        {"confidence": 0.6, "correct": False},
        {"confidence": 0.5, "correct": True},
        {"confidence": 0.4, "correct": False},
        {"confidence": 0.3, "correct": False},
        {"confidence": 0.2, "correct": False},
        {"confidence": 0.1, "correct": True},
    ]


@pytest.mark.asyncio
async def test_calibrate_platt_scaling(sample_scores):
    from app.services.calibration_service import calibration_service
    calibrated = await calibration_service.calibrate(sample_scores)
    assert calibrated is not None
    assert len(calibrated) == len(sample_scores)
    for c in calibrated:
        assert "calibrated_confidence" in c
        assert 0.0 <= c["calibrated_confidence"] <= 1.0


@pytest.mark.asyncio
async def test_compute_brier_from_calibrated(sample_scores):
    from app.services.calibration_service import calibration_service
    brier = calibration_service._compute_brier_score(sample_scores)
    assert brier is not None
    assert 0.0 <= brier <= 1.0


@pytest.mark.asyncio
async def test_get_calibration_rating():
    from app.services.calibration_service import calibration_service
    assert calibration_service._get_rating(0.05) == "优秀"
    assert calibration_service._get_rating(0.12) == "良好"
    assert calibration_service._get_rating(0.20) == "一般"
    assert calibration_service._get_rating(0.30) == "需改进"


@pytest.mark.asyncio
async def test_calibrate_empty():
    from app.services.calibration_service import calibration_service
    result = await calibration_service.calibrate([])
    assert result == []
