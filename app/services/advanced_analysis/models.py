# P2.2 高级分析引擎 — Pydantic 模型定义
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============ 通用请求 ============

class AdvancedAnalysisRequest(BaseModel):
    """高级分析请求"""
    title: str
    description: str
    category: str = "Other"
    importance: int = Field(default=3, ge=1, le=5)
    timestamp: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


# ============ 蒙特卡洛模拟 ============

class ScenarioVariable(BaseModel):
    """情景变量"""
    name: str
    description: str = ""
    distribution_type: str = "normal"  # normal / uniform / beta / triangular
    params: Dict[str, float] = Field(default_factory=lambda: {"mean": 0.5, "std": 0.15})
    impact_direction: float = Field(default=1.0, ge=-1.0, le=1.0)  # +1 positive, -1 negative
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class MonteCarloScenarioLLMResponse(BaseModel):
    """LLM 生成的蒙特卡洛情景参数"""
    variables: List[ScenarioVariable] = Field(default_factory=list)
    base_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    trend_direction: str = "SIDEWAYS"  # UP / DOWN / SIDEWAYS
    key_assumptions: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class MonteCarloResult(BaseModel):
    """蒙特卡洛模拟结果"""
    n_simulations: int = 1000
    probability_distribution: Dict[str, float] = Field(default_factory=dict)
    mean: float = 0.0
    std: float = 0.0
    CI_95: List[float] = Field(default_factory=lambda: [0.0, 1.0])
    CI_80: List[float] = Field(default_factory=lambda: [0.1, 0.9])
    sensitivity_analysis: Dict[str, float] = Field(default_factory=dict)
    trend: str = "SIDEWAYS"
    confidence: float = 0.5
    simulation_details: List[Dict[str, Any]] = Field(default_factory=list)
    variables_used: List[ScenarioVariable] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class MonteCarloResponse(BaseModel):
    """蒙特卡洛 API 响应"""
    event_title: str
    result: MonteCarloResult
    timestamp: str


# ============ 贝叶斯网络 ============

class BayesianNode(BaseModel):
    """贝叶斯网络节点"""
    id: str
    name: str
    description: str = ""
    node_type: str = "factor"  # factor / evidence / hypothesis
    prior_probability: float = Field(default=0.5, ge=0.0, le=1.0)


class BayesianEdge(BaseModel):
    """贝叶斯网络边"""
    source_id: str
    target_id: str
    conditional_probability: float = Field(default=0.7, ge=0.0, le=1.0)
    relationship_type: str = "influence"  # influence / cause / correlate


class BayesianNetworkLLMResponse(BaseModel):
    """LLM 生成的贝叶斯网络结构"""
    nodes: List[BayesianNode] = Field(default_factory=list)
    edges: List[BayesianEdge] = Field(default_factory=list)
    evidence_nodes: List[str] = Field(default_factory=list)
    hypothesis_node: str = "outcome"
    reasoning: str = ""


class BayesianResult(BaseModel):
    """贝叶斯网络推理结果"""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[BayesianEdge] = Field(default_factory=list)
    posteriors: Dict[str, float] = Field(default_factory=dict)
    main_hypothesis_posterior: float = 0.5
    evidence_impact: Dict[str, float] = Field(default_factory=dict)
    influence_diagram: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""


class BayesianResponse(BaseModel):
    """贝叶斯分析 API 响应"""
    event_title: str
    result: BayesianResult
    timestamp: str


# ============ 因果推理 ============

class CausalFactor(BaseModel):
    """因果因素"""
    id: str
    name: str
    description: str = ""
    factor_type: str = "cause"  # cause / effect / mediator / confounder
    direction: float = Field(default=1.0, ge=-1.0, le=1.0)
    strength: float = Field(default=0.5, ge=0.0, le=1.0)


class CausalLink(BaseModel):
    """因果链接"""
    source_id: str
    target_id: str
    mechanism: str = ""
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    lag_time: str = "immediate"  # immediate / short / medium / long


class CausalGraphLLMResponse(BaseModel):
    """LLM 生成的因果图结构"""
    factors: List[CausalFactor] = Field(default_factory=list)
    links: List[CausalLink] = Field(default_factory=list)
    confounders: List[str] = Field(default_factory=list)
    main_effect: str = ""
    reasoning: str = ""


class CausalResult(BaseModel):
    """因果推理结果"""
    factors: List[CausalFactor] = Field(default_factory=list)
    links: List[CausalLink] = Field(default_factory=list)
    direct_effects: Dict[str, float] = Field(default_factory=dict)
    indirect_effects: Dict[str, float] = Field(default_factory=dict)
    total_effects: Dict[str, float] = Field(default_factory=dict)
    confounders: List[str] = Field(default_factory=list)
    causal_paths: List[Dict[str, Any]] = Field(default_factory=list)
    graph_data: Dict[str, Any] = Field(default_factory=dict)


class CausalResponse(BaseModel):
    """因果分析 API 响应"""
    event_title: str
    result: CausalResult
    timestamp: str


# ============ 集成预测 ============

class MethodResult(BaseModel):
    """单个分析方法结果"""
    method_name: str
    trend: str = "SIDEWAYS"
    confidence: float = 0.5
    key_findings: List[str] = Field(default_factory=list)
    weight: float = 1.0


class EnsembleResult(BaseModel):
    """集成预测结果"""
    methods: List[MethodResult] = Field(default_factory=list)
    unified_trend: str = "SIDEWAYS"
    unified_confidence: float = 0.5
    CI: List[float] = Field(default_factory=lambda: [0.3, 0.7])
    agreement_score: float = 0.5
    weighted_probabilities: Dict[str, float] = Field(default_factory=dict)
    method_weights: Dict[str, float] = Field(default_factory=dict)
    uncertainty_calibration: Dict[str, Any] = Field(default_factory=dict)
    recommendation: str = ""
    detailed_results: Dict[str, Any] = Field(default_factory=dict)


class EnsembleResponse(BaseModel):
    """集成预测 API 响应"""
    event_title: str
    result: EnsembleResult
    timestamp: str


# ============ 方法列表 ============

class AnalysisMethodInfo(BaseModel):
    """分析方法信息"""
    id: str
    name: str
    description: str
    endpoint: str


class AnalysisMethodsResponse(BaseModel):
    """分析方法列表"""
    methods: List[AnalysisMethodInfo] = Field(default_factory=list)
