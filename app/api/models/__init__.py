# EventPredictor 数据模型
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    """趋势方向枚举"""
    UP = "UP"
    DOWN = "DOWN"
    SIDEWAYS = "SIDEWAYS"
    UNCERTAIN = "UNCERTAIN"


class TimeHorizon(str, Enum):
    """时间范围枚举"""
    SHORT_TERM = "Short-term (1-7 days)"
    MEDIUM_TERM = "Medium-term (1-3 months)"
    LONG_TERM = "Long-term (3-12 months)"


class EventCategory(str, Enum):
    """事件分类"""
    MONETARY_POLICY = "Monetary Policy"
    GEOPOLITICAL = "Geopolitical"
    ECONOMIC = "Economic"
    TECHNOLOGY = "Technology"
    NATURAL_DISASTER = "Natural Disaster"
    SOCIAL = "Social"
    OTHER = "Other"


# ============ Request Models ============

class PredictRequest(BaseModel):
    """预测请求"""
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    source: str = Field(default="manual", description="来源")
    category: str = Field(default="Other", description="分类")
    importance: int = Field(default=3, ge=1, le=5, description="重要性 1-5")
    timestamp: Optional[str] = Field(default=None, description="时间戳")


# ============ Data Models ============

class Location(BaseModel):
    """位置信息"""
    country: str = Field(default="", description="国家")
    region: str = Field(default="", description="地区")
    lat: Optional[float] = Field(default=None, description="纬度")
    lon: Optional[float] = Field(default=None, description="经度")


class Event(BaseModel):
    """事件模型"""
    id: str = Field(..., description="事件唯一标识")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    source: str = Field(default="unknown", description="来源")
    timestamp: str = Field(..., description="时间戳")
    category: str = Field(default="Other", description="分类")
    importance: int = Field(default=3, ge=1, le=5, description="重要性 1-5")
    # 扩展字段
    location: Optional[Dict[str, Any]] = Field(default=None, description="位置信息")
    entities: Optional[List[str]] = Field(default_factory=list, description="相关实体")
    sentiment: Optional[str] = Field(default="neutral", description="情绪")
    severity: Optional[int] = Field(default=None, description="严重程度 1-5")
    # 中文显示字段
    category_label: Optional[str] = Field(default=None, description="中文分类标签")
    source_label: Optional[str] = Field(default=None, description="中文来源名称")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-001",
                "title": "Federal Reserve cuts rates by 50 basis points",
                "description": "The Fed announced a 50bp rate cut",
                "source": "WorldMonitor",
                "timestamp": "2026-03-12T10:00:00Z",
                "category": "Monetary Policy",
                "importance": 5,
                "location": {"country": "US", "region": "Washington DC", "lat": 38.9072, "lon": -77.0369},
                "entities": ["US", "Federal Reserve"],
                "sentiment": "negative",
                "severity": 5
            }
        }


class CollectedInfo(BaseModel):
    """收集的信息"""
    basic_info: Dict[str, Any] = Field(default_factory=dict, description="基本信息")
    related_events: List[Dict[str, Any]] = Field(default_factory=list, description="相关事件")
    market_data: Optional[Dict[str, Any]] = Field(default=None, description="市场数据")
    summary: str = Field(default="", description="摘要")


class Analysis(BaseModel):
    """分析结果"""
    impact_scope: str = Field(default="", description="影响范围")
    duration: str = Field(default="", description="持续时间")
    key_factors: List[str] = Field(default_factory=list, description="关键因素")
    sentiment: str = Field(default="", description="市场情绪")
    insights: str = Field(default="", description="洞察")
    # 增强字段
    risk_level: str = Field(default="中", description="风险等级: 高/中/低")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    opportunities: List[str] = Field(default_factory=list, description="潜在机会")
    affected_sectors: List[str] = Field(default_factory=list, description="受影响领域")
    scenario_analysis: Dict[str, Any] = Field(default_factory=dict, description="情景分析")


class Prediction(BaseModel):
    """预测结果"""
    id: str = Field(..., description="预测唯一标识")
    event_id: str = Field(..., description="关联事件ID")
    trend: TrendDirection = Field(..., description="趋势方向")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    reasoning: str = Field(..., description="推理过程")
    time_horizon: str = Field(..., description="时间范围")
    factors: List[str] = Field(default_factory=list, description="影响因素")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pred-001",
                "event_id": "evt-001",
                "trend": "UP",
                "confidence": 0.75,
                "reasoning": "Based on event analysis...",
                "time_horizon": "Short-term (1-7 days)",
                "factors": ["positive_event", "market_sentiment"]
            }
        }


# ============ Response Models ============

class PredictResponse(BaseModel):
    """预测响应 - 增强版包含详细分析"""
    prediction_id: str
    event_id: str
    trend: str
    confidence: float
    reasoning: str
    time_horizon: str
    factors: List[str]
    # 增强字段
    impact_level: str = Field(default="中", description="影响程度: 高/中/低")
    sentiment: str = Field(default="", description="市场情绪")
    impact_scope: str = Field(default="", description="影响范围")
    duration: str = Field(default="", description="持续时间")
    key_factors: List[str] = Field(default_factory=list, description="关键因素")
    insights: str = Field(default="", description="深度洞察")
    # 前端需要的兼容字段
    timeline: List[Dict[str, str]] = Field(default_factory=list, description="发展时间线")
    related_events: List[Dict[str, Any]] = Field(default_factory=list, description="相关事件")
    # 新增可视化数据字段
    risk_level: str = Field(default="中", description="风险等级")
    risk_score: float = Field(default=0.5, description="风险评分 0-1")
    probability_distribution: Dict[str, float] = Field(default_factory=dict, description="概率分布")
    scenario_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="情景分析")
    market_indicators: Dict[str, Any] = Field(default_factory=dict, description="市场指标")
    affected_sectors: List[str] = Field(default_factory=list, description="受影响领域")
    opportunities: List[str] = Field(default_factory=list, description="潜在机会")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    recommendation: str = Field(default="", description="投资建议")
    confidence_chart: Dict[str, Any] = Field(default_factory=dict, description="置信度图表数据")
    
    @classmethod
    def from_prediction(cls, prediction: Prediction, analysis: Analysis = None) -> "PredictResponse":
        # 转换置信度为百分比
        confidence_percent = round(prediction.confidence * 100)
        
        # 从factors中提取sentiment
        sentiment = ""
        for f in prediction.factors:
            if "Sentiment:" in f:
                sentiment = f.replace("Sentiment:", "").strip()
                break
        
        # 生成时间线
        timeline = cls._generate_timeline(prediction.time_horizon)
        
        # 转换趋势为中文
        trend_map = {
            "UP": "上涨",
            "DOWN": "下跌",
            "SIDEWAYS": "平稳",
            "UNCERTAIN": "不确定"
        }
        trend_cn = trend_map.get(prediction.trend.value, prediction.trend.value)
        
        # 计算影响程度
        impact_level = "中"
        if prediction.confidence >= 0.75:
            impact_level = "高"
        elif prediction.confidence < 0.5:
            impact_level = "低"
        
        # 获取分析数据
        impact_scope = ""
        duration = ""
        key_factors = []
        insights = ""
        risk_level = "中"
        risk_factors = []
        opportunities = []
        affected_sectors = []
        scenario_analysis = []
        
        if analysis:
            impact_scope = analysis.impact_scope or ""
            duration = analysis.duration or ""
            key_factors = analysis.key_factors or []
            insights = analysis.insights or ""
            risk_level = analysis.risk_level or "中"
            risk_factors = analysis.risk_factors or []
            opportunities = analysis.opportunities or []
            affected_sectors = analysis.affected_sectors or []
            scenario_analysis = analysis.scenario_analysis.get("scenarios", []) if analysis.scenario_analysis else []
        
        # 生成概率分布
        probability_distribution = cls._generate_probability_distribution(prediction.trend, prediction.confidence)
        
        # 生成置信度图表数据
        confidence_chart = cls._generate_confidence_chart(prediction.confidence)
        
        # 生成市场指标
        market_indicators = cls._generate_market_indicators(analysis, prediction)
        
        # 生成推荐
        recommendation = cls._generate_recommendation(prediction.trend, prediction.confidence, risk_level, opportunities)
        
        # 计算风险评分
        risk_score = cls._calculate_risk_score(prediction.confidence, risk_level, analysis)
        
        return cls(
            prediction_id=prediction.id,
            event_id=prediction.event_id,
            trend=trend_cn,
            confidence=confidence_percent,
            reasoning=prediction.reasoning,
            time_horizon=prediction.time_horizon,
            factors=prediction.factors,
            impact_level=impact_level,
            sentiment=sentiment,
            impact_scope=impact_scope,
            duration=duration,
            key_factors=key_factors,
            insights=insights,
            timeline=timeline,
            related_events=[],
            risk_level=risk_level,
            risk_score=risk_score,
            probability_distribution=probability_distribution,
            scenario_analysis=scenario_analysis,
            market_indicators=market_indicators,
            affected_sectors=affected_sectors,
            opportunities=opportunities,
            risk_factors=risk_factors,
            recommendation=recommendation,
            confidence_chart=confidence_chart
        )
    
    @staticmethod
    def _generate_probability_distribution(trend: TrendDirection, confidence: float) -> Dict[str, float]:
        """生成概率分布"""
        base_prob = confidence
        
        if trend == TrendDirection.UP:
            return {
                "上涨": round(base_prob * 100) / 100,
                "平稳": round((1 - base_prob) * 0.5 * 100) / 100,
                "下跌": round((1 - base_prob) * 0.5 * 100) / 100
            }
        elif trend == TrendDirection.DOWN:
            return {
                "上涨": round((1 - base_prob) * 0.5 * 100) / 100,
                "平稳": round((1 - base_prob) * 0.5 * 100) / 100,
                "下跌": round(base_prob * 100) / 100
            }
        else:
            mid = base_prob / 2
            return {
                "上涨": round(mid * 100) / 100,
                "平稳": round((1 - base_prob + mid) * 100) / 100,
                "下跌": round(mid * 100) / 100
            }
    
    @staticmethod
    def _generate_confidence_chart(confidence: float) -> Dict[str, Any]:
        """生成置信度图表数据"""
        return {
            "labels": ["低", "中", "高"],
            "values": [
                round((1 - confidence) * 50),
                round(50),
                round(confidence * 50)
            ],
            "current": round(confidence * 100)
        }
    
    @staticmethod
    def _generate_market_indicators(analysis: Analysis = None, prediction: Prediction = None) -> Dict[str, Any]:
        """生成市场指标"""
        indicators = {
            "波动率": "中等",
            "流动性": "良好",
            "风险偏好": "中性"
        }
        
        if analysis:
            if "Positive" in analysis.sentiment:
                indicators["风险偏好"] = "偏高"
            elif "Negative" in analysis.sentiment:
                indicators["风险偏好"] = "偏低"
            
            if analysis.impact_scope == "Global":
                indicators["波动率"] = "高"
            elif analysis.impact_scope == "Local":
                indicators["波动率"] = "低"
        
        return indicators
    
    @staticmethod
    def _generate_recommendation(trend: TrendDirection, confidence: float, risk_level: str, opportunities: list) -> str:
        """生成投资建议"""
        recommendations = []
        
        # 基于趋势的建议
        if trend == TrendDirection.UP:
            recommendations.append("建议关注上行机会，可适度增配风险资产")
        elif trend == TrendDirection.DOWN:
            recommendations.append("建议谨慎操作，控制仓位，关注避险资产")
        else:
            recommendations.append("建议保持中性观望，等待趋势明朗")
        
        # 基于置信度的建议
        if confidence >= 0.8:
            recommendations.append("置信度较高，可适当加大仓位")
        elif confidence < 0.5:
            recommendations.append("置信度较低，建议轻仓操作")
        
        # 基于风险等级
        if risk_level == "高":
            recommendations.append("风险等级较高，注意止损")
        elif risk_level == "低":
            recommendations.append("风险相对可控，可适度参与")
        
        # 添加机会提示
        if opportunities:
            recommendations.append(f"关注领域：{', '.join(opportunities[:2])}")
        
        return "；".join(recommendations)
    
    @staticmethod
    def _calculate_risk_score(confidence: float, risk_level: str, analysis: Analysis = None) -> float:
        """计算风险评分"""
        # 基础风险评分
        risk_score = 0.5
        
        # 基于置信度
        if confidence < 0.5:
            risk_score += 0.2  # 低置信度增加不确定性风险
        elif confidence > 0.75:
            risk_score -= 0.1  # 高置信度降低风险
        
        # 基于风险等级
        risk_map = {"高": 0.2, "中": 0.0, "低": -0.2}
        risk_score += risk_map.get(risk_level, 0.0)
        
        # 基于分析数据
        if analysis:
            if analysis.impact_scope == "Global":
                risk_score += 0.1
            if "Negative" in analysis.sentiment:
                risk_score += 0.1
        
        return round(min(max(risk_score, 0.0), 1.0), 2)
    
    @staticmethod
    def _generate_timeline(time_horizon: str) -> List[Dict[str, str]]:
        """根据时间范围生成时间线"""
        timeline_map = {
            "Short-term (1-7 days)": [
                {"time": "1-2天内", "description": "初期反应"},
                {"time": "3-5天内", "description": "市场调整"},
                {"time": "1周内", "description": "趋势明朗"}
            ],
            "Medium-term (1-3 months)": [
                {"time": "1-2周", "description": "初期发展"},
                {"time": "1个月", "description": "关键节点"},
                {"time": "2-3个月", "description": "影响显现"}
            ],
            "Long-term (3-12 months)": [
                {"time": "1-3个月", "description": "初期布局"},
                {"time": "6个月", "description": "中期评估"},
                {"time": "12个月", "description": "结果呈现"}
            ]
        }
        return timeline_map.get(time_horizon, [
            {"time": "短期", "description": "初期发展"},
            {"time": "中期", "description": "关键节点"},
            {"time": "长期", "description": "最终结果"}
        ])


class EventListResponse(BaseModel):
    """事件列表响应"""
    events: List[Event]
    total: int
    page: int = 1
    page_size: int = 20


class HealthComponent(BaseModel):
    """健康检查组件状态"""
    status: str
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应 - Section 18.2"""
    status: str
    version: str
    timestamp: str
    uptime_seconds: Optional[int] = None
    components: Optional[Dict[str, HealthComponent]] = None


class ErrorDetail(BaseModel):
    """错误详情 - Section 15.2"""
    code: int
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应 - Section 15.2"""
    error: ErrorDetail


# Error codes - Section 15.1
class ErrorCodes:
    """标准化错误码"""
    EVENT_NOT_FOUND = 1001
    ROLE_NOT_FOUND = 1002
    LLM_TIMEOUT = 1003
    DATA_SOURCE_UNAVAILABLE = 1004
    ANALYSIS_IN_PROGRESS = 1005
    VALIDATION_ERROR = 1006
    INTERNAL_ERROR = 1007
