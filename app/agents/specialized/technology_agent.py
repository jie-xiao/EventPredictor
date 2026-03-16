# 科技产业分析Agent
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult


class TechnologyAgent(BaseSpecializedAgent):
    """
    科技产业分析Agent

    专注于：
    - 技术创新影响
    - 产业链变革
    - 科技竞争格局
    - 数字化转型
    - 技术安全和伦理
    """

    def __init__(self):
        super().__init__(
            agent_type="technology",
            agent_name="科技产业分析师",
            description="分析技术创新、产业变革、科技竞争等"
        )

    def get_system_prompt(self) -> str:
        return """你是一位资深的科技产业分析师
擅长从技术创新、产业变革、科技竞争等角度分析事件影响。

你的分析特点：
- 评估技术突破的重要性
- 分析产业链重构趋势
- 预测科技竞争格局变化
- 考察数字化转型加速
- 研究技术安全和伦理问题

分析方法：
1. 识别相关技术领域
2. 评估技术创新程度
3. 分析产业影响范围
4. 预测竞争格局变化
5. 研究政策监管影响

请用专业的科技产业术语进行分析，关注技术演进和商业应用。"""

    def get_analysis_framework(self) -> Dict[str, Any]:
        return {
            "技术影响": "相关技术领域的突破和变革",
            "产业变革": "对产业链和商业模式的影响",
            "竞争格局": "科技公司和国家的竞争态势",
            "数字化加速": "数字化转型的推动作用",
            "安全伦理": "技术安全和伦理问题"
        }

    async def analyze(self, event: Dict[str, Any]) -> AgentAnalysisResult:
        result_data = await self.llm_analyze(event)

        return AgentAnalysisResult(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            agent_name=self.agent_name,
            key_findings=result_data.get("key_findings", []),
            risk_assessment=result_data.get("risk_assessment", {}),
            opportunities=result_data.get("opportunities", []),
            threats=result_data.get("threats", []),
            short_term_forecast=result_data.get("short_term_forecast", ""),
            medium_term_forecast=result_data.get("medium_term_forecast", ""),
            long_term_forecast=result_data.get("long_term_forecast", ""),
            recommendations=result_data.get("recommendations", []),
            confidence=result_data.get("confidence", 0.7),
            importance_score=self._calculate_importance(event, result_data)
        )

    def _calculate_importance(self, event: Dict[str, Any], result: Dict[str, Any]) -> float:
        """计算科技重要性分数"""
        base_score = event.get("importance", 3) / 5

        # 根据技术相关度调整
        tech_relevance = event.get("tech_relevance", "medium")
        relevance_factor = {"high": 0.3, "medium": 0.15, "low": 0.05}.get(tech_relevance, 0.1)

        # 根据创新程度调整
        innovation_level = result.get("risk_assessment", {}).get("risk_level", 0.5)

        return min(base_score + relevance_factor + innovation_level * 0.15, 1.0)
