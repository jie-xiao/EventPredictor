"""
Agent Unit Tests
Tests for individual Agent classes
"""
import pytest
from app.agents.pipeline import (
    BaseAgent,
    InfoCollectorAgent,
    AnalyzerAgent,
    PredictorAgent,
    AgentPipeline
)
from app.api.models import (
    Event,
    CollectedInfo,
    Analysis,
    Prediction,
    TrendDirection
)


class TestBaseAgent:
    """Test BaseAgent abstract class"""

    def test_base_agent_has_name(self):
        """Test that BaseAgent has name attribute"""
        class TestAgent(BaseAgent):
            def run(self, input_data):
                return input_data

        agent = TestAgent(name="TestAgent", role="Tester", description="A test agent")
        assert agent.name == "TestAgent"
        assert agent.role == "Tester"
        assert agent.description == "A test agent"

    def test_base_agent_repr(self):
        """Test BaseAgent string representation"""
        class TestAgent(BaseAgent):
            def run(self, input_data):
                return input_data

        agent = TestAgent(name="TestAgent", role="Tester", description="A test agent")
        repr_str = repr(agent)
        assert "TestAgent" in repr_str
        assert "Tester" in repr_str


class TestInfoCollectorAgent:
    """Test InfoCollectorAgent"""

    @pytest.fixture
    def agent(self):
        return InfoCollectorAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes"""
        assert agent.name == "InfoCollector"
        assert agent.role == "Information Gathering"

    def test_collect_basic_info(self, agent, sample_event):
        """Test basic info collection"""
        result = agent.run(sample_event)
        
        assert isinstance(result, CollectedInfo)
        assert result.basic_info["title"] == sample_event.title
        assert result.basic_info["description"] == sample_event.description
        assert result.basic_info["category"] == sample_event.category

    def test_collect_importance_label(self, agent, sample_event):
        """Test importance label mapping"""
        result = agent.run(sample_event)
        
        # importance=5 should map to "高"
        assert result.basic_info["importance_label"] == "高"

    def test_collect_importance_label_levels(self, agent):
        """Test all importance levels"""
        test_cases = [
            (1, "低"),
            (2, "较低"),
            (3, "中等"),
            (4, "较高"),
            (5, "高"),
        ]
        
        for importance, expected_label in test_cases:
            event = Event(
                id="test",
                title="Test",
                description="Test",
                source="test",
                timestamp="2026-03-12T10:00:00Z",
                category="Other",
                importance=importance
            )
            result = agent.run(event)
            assert result.basic_info["importance_label"] == expected_label

    def test_collect_summary_generation(self, agent, sample_event):
        """Test summary is generated"""
        result = agent.run(sample_event)
        
        assert result.summary != ""
        assert sample_event.title in result.summary
        assert sample_event.category in result.summary

    def test_collect_related_events_empty(self, agent, sample_event):
        """Test related events is initialized as empty list"""
        result = agent.run(sample_event)
        
        assert isinstance(result.related_events, list)
        assert len(result.related_events) == 0

    def test_collect_market_data_none(self, agent, sample_event):
        """Test market data is None by default"""
        result = agent.run(sample_event)
        
        assert result.market_data is None


class TestAnalyzerAgent:
    """Test AnalyzerAgent"""

    @pytest.fixture
    def agent(self):
        return AnalyzerAgent()

    @pytest.fixture
    def sample_collected_info(self, sample_event):
        # Use InfoCollector to create proper CollectedInfo
        collector = InfoCollectorAgent()
        return collector.run(sample_event)

    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes"""
        assert agent.name == "Analyzer"
        assert agent.role == "Deep Analysis"

    def test_analyze_returns_analysis(self, agent, sample_collected_info):
        """Test analyze returns Analysis object"""
        result = agent.run(sample_collected_info)
        
        assert isinstance(result, Analysis)
        assert result.impact_scope != ""
        assert result.duration != ""

    def test_analyze_impact_scope_global(self, agent, sample_event):
        """Test high importance events get global scope"""
        # Set high importance
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=5
        )
        collector = InfoCollectorAgent()
        collected = collector.run(event)
        result = agent.run(collected)
        
        assert result.impact_scope == "Global"

    def test_analyze_impact_scope_by_category(self, agent, sample_event):
        """Test impact scope varies by category"""
        test_cases = [
            ("Monetary Policy", 3, "Global"),
            ("Geopolitical", 3, "Regional"),
            ("Technology", 3, "Industry"),
            ("Natural Disaster", 3, "Regional"),
            ("Social", 3, "Local"),
        ]
        
        for category, importance, expected_scope in test_cases:
            event = Event(
                id="test",
                title="Test",
                description="Test",
                source="test",
                timestamp="2026-03-12T10:00:00Z",
                category=category,
                importance=importance
            )
            collector = InfoCollectorAgent()
            collected = collector.run(event)
            result = agent.run(collected)
            assert result.impact_scope == expected_scope, f"Failed for category {category}"

    def test_analyze_duration_by_category(self, agent):
        """Test duration varies by category"""
        test_cases = [
            ("Monetary Policy", "Medium-term (1-3 months)"),
            ("Geopolitical", "Long-term (3-12 months)"),
            ("Natural Disaster", "Short-term (1-7 days)"),
            ("Social", "Short-term (1-7 days)"),
        ]
        
        for category, expected_duration in test_cases:
            event = Event(
                id="test",
                title="Test",
                description="Test",
                source="test",
                timestamp="2026-03-12T10:00:00Z",
                category=category,
                importance=3
            )
            collector = InfoCollectorAgent()
            collected = collector.run(event)
            result = agent.run(collected)
            assert result.duration == expected_duration, f"Failed for category {category}"

    def test_analyze_sentiment_positive(self, agent):
        """Test positive sentiment for monetary policy"""
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=3
        )
        collector = InfoCollectorAgent()
        collected = collector.run(event)
        result = agent.run(collected)
        
        assert "Positive" in result.sentiment

    def test_analyze_sentiment_negative(self, agent):
        """Test negative sentiment for geopolitical events"""
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Geopolitical",
            importance=3
        )
        collector = InfoCollectorAgent()
        collected = collector.run(event)
        result = agent.run(collected)
        
        assert "Negative" in result.sentiment

    def test_analyze_key_factors_extracted(self, agent, sample_collected_info):
        """Test key factors are extracted"""
        result = agent.run(sample_collected_info)
        
        assert isinstance(result.key_factors, list)
        assert len(result.key_factors) > 0

    def test_analyze_key_factors_max_5(self, agent):
        """Test key factors are limited to 5"""
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=3
        )
        collector = InfoCollectorAgent()
        collected = collector.run(event)
        result = agent.run(collected)
        
        assert len(result.key_factors) <= 5

    def test_analyze_insights_generated(self, agent, sample_collected_info):
        """Test insights are generated"""
        result = agent.run(sample_collected_info)
        
        assert result.insights != ""
        assert "影响范围" in result.insights or "impact" in result.insights.lower()


class TestPredictorAgent:
    """Test PredictorAgent"""

    @pytest.fixture
    def agent(self):
        return PredictorAgent()

    @pytest.fixture
    def sample_analysis(self, sample_event):
        # Create analysis through the pipeline
        collector = InfoCollectorAgent()
        collected = collector.run(sample_event)
        
        analyzer = AnalyzerAgent()
        return analyzer.run(collected)

    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes"""
        assert agent.name == "Predictor"
        assert agent.role == "Trend Prediction"

    def test_predict_returns_prediction(self, agent, sample_analysis, sample_event):
        """Test predict returns Prediction object"""
        result = agent.run(sample_analysis, sample_event)
        
        assert isinstance(result, Prediction)
        assert result.id.startswith("pred-")
        assert result.event_id == sample_event.id

    def test_predict_trend_determination(self, agent):
        """Test trend is correctly determined"""
        # Positive sentiment should lead to UP trend
        positive_analysis = Analysis(
            impact_scope="Global",
            duration="Medium-term (1-3 months)",
            key_factors=["Factor1", "Factor2"],
            sentiment="Positive",
            insights="Test insights"
        )
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=3
        )
        
        result = agent.run(positive_analysis, event)
        assert result.trend == TrendDirection.UP

    def test_predict_confidence_range(self, agent, sample_analysis, sample_event):
        """Test confidence is within valid range"""
        result = agent.run(sample_analysis, sample_event)
        
        assert 0.0 <= result.confidence <= 1.0
        assert result.confidence >= 0.3  # Minimum confidence

    def test_predict_confidence_high_for_global(self, agent):
        """Test global scope increases confidence"""
        high_impact_analysis = Analysis(
            impact_scope="Global",
            duration="Long-term (3-12 months)",
            key_factors=["Factor1", "Factor2", "Factor3"],
            sentiment="Strongly Positive",
            insights="Test insights"
        )
        event = Event(
            id="test",
            title="Test",
            description="Test",
            source="test",
            timestamp="2026-03-12T10:00:00Z",
            category="Monetary Policy",
            importance=5
        )
        
        result = agent.run(high_impact_analysis, event)
        assert result.confidence >= 0.7

    def test_predict_time_horizon_from_analysis(self, agent, sample_analysis, sample_event):
        """Test time horizon is taken from analysis"""
        result = agent.run(sample_analysis, sample_event)
        
        assert result.time_horizon != ""

    def test_predict_reasoning_generated(self, agent, sample_analysis, sample_event):
        """Test reasoning is generated"""
        result = agent.run(sample_analysis, sample_event)
        
        assert result.reasoning != ""
        assert "趋势" in result.reasoning or "trend" in result.reasoning.lower()

    def test_predict_factors_included(self, agent, sample_analysis, sample_event):
        """Test factors are included in prediction"""
        result = agent.run(sample_analysis, sample_event)
        
        assert isinstance(result.factors, list)
        assert len(result.factors) > 0


class TestAgentPipeline:
    """Test AgentPipeline"""

    @pytest.fixture
    def pipeline(self):
        return AgentPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes all agents"""
        assert pipeline.info_collector is not None
        assert pipeline.analyzer is not None
        assert pipeline.predictor is not None

    def test_pipeline_run_returns_prediction(self, pipeline, sample_event):
        """Test pipeline run returns Prediction"""
        result = pipeline.run(sample_event)
        
        assert isinstance(result, Prediction)
        assert result.id.startswith("pred-")
        assert result.event_id == sample_event.id

    def test_pipeline_complete_flow(self, pipeline, sample_event):
        """Test complete pipeline flow"""
        result = pipeline.run(sample_event)
        
        # All fields should be populated
        assert result.trend is not None
        assert result.confidence > 0
        assert result.reasoning != ""
        assert result.time_horizon != ""
        assert len(result.factors) > 0

    def test_pipeline_different_events(self, pipeline, sample_geopolitical_event):
        """Test pipeline with different event types"""
        result = pipeline.run(sample_geopolitical_event)
        
        assert isinstance(result, Prediction)
        # Geopolitical events should typically have negative sentiment
        assert result.trend in [TrendDirection.DOWN, TrendDirection.SIDEWAYS]
