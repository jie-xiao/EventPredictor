# tests/test_feature_extractor.py
import pytest
from datetime import datetime, timezone


@pytest.fixture
def sample_event():
    return {
        "id": "evt-001",
        "title": "US announces new tariffs on Chinese imports",
        "description": "The US government announced a 25% tariff on $200B of Chinese goods.",
        "source": "rss:reuters",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": "Trade",
        "severity": 4,
        "entities": ["US", "China"],
        "sentiment": "negative",
    }


@pytest.fixture
def sample_polymarket():
    return {
        "event_id": "evt-001",
        "probability": 0.72,
        "volume": 150000.0,
        "question": "Will US impose tariffs on China in Q2 2026?",
    }


@pytest.mark.asyncio
async def test_extract_basic_features(sample_event):
    from app.services.feature_extractor import FeatureExtractor
    extractor = FeatureExtractor()
    features = await extractor.extract(sample_event)
    assert features["event_id"] == "evt-001"
    assert features["event_type"] is not None
    assert -1.0 <= features["sentiment"] <= 1.0
    assert 0.0 <= features["severity"] <= 1.0
    assert isinstance(features["entities"], list)
    assert len(features["entities"]) >= 2


@pytest.mark.asyncio
async def test_extract_with_polymarket(sample_event, sample_polymarket):
    from app.services.feature_extractor import FeatureExtractor
    extractor = FeatureExtractor()
    features = await extractor.extract(sample_event, polymarket_data=sample_polymarket)
    assert features["market_prob"] == 0.72
    assert features["market_volume"] == 150000.0


@pytest.mark.asyncio
async def test_extract_novelty(sample_event):
    from app.services.feature_extractor import FeatureExtractor
    extractor = FeatureExtractor()
    # First extraction
    f1 = await extractor.extract(sample_event)
    assert f1["novelty_score"] > 0.5  # First occurrence should be novel
