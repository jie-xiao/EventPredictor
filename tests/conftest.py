"""
Pytest configuration and shared fixtures
"""
import sys
import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.api.models import Event, TrendDirection


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_event() -> Event:
    """Create a sample event for testing"""
    return Event(
        id="evt-test-001",
        title="Federal Reserve cuts rates by 50 basis points",
        description="The Federal Reserve announced a 50bp interest rate cut",
        source="test",
        timestamp="2026-03-12T10:00:00Z",
        category="Monetary Policy",
        importance=5
    )


@pytest.fixture
def sample_event_data() -> dict:
    """Create sample event data dict for API testing"""
    return {
        "title": "Federal Reserve cuts rates by 50 basis points",
        "description": "The Federal Reserve announced a 50bp interest rate cut",
        "source": "test",
        "category": "Monetary Policy",
        "importance": 5,
        "timestamp": "2026-03-12T10:00:00Z"
    }


@pytest.fixture
def sample_geopolitical_event() -> Event:
    """Create a geopolitical event for testing"""
    return Event(
        id="evt-test-002",
        title="International Trade Agreement Signed",
        description="Major trade agreement signed between two superpowers",
        source="test",
        timestamp="2026-03-12T10:00:00Z",
        category="Geopolitical",
        importance=4
    )


@pytest.fixture
def sample_tech_event() -> Event:
    """Create a technology event for testing"""
    return Event(
        id="evt-test-003",
        title="AI Breakthrough Announced",
        description="New AI model achieves breakthrough in reasoning",
        source="test",
        timestamp="2026-03-12T10:00:00Z",
        category="Technology",
        importance=4
    )
