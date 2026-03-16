# 军事安全分析Agent
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult


class MilitaryAgent(BaseSpecializedAgent):
    """
    军事安全分析Agent

    专注于：
    - 军事冲突风险
    - 国防安全
    - 军备控制
    - 军事同盟
    - 地区稳定
    """

    def __init__(self):
        super().__init__(
            agent_type="military",
            agent_name="军事安全分析师",
            description="分析军事冲突风险、国防安全、军备控制等"
        )

    def get_system_prompt(self) -> str:
        return """你是一位资深的军事安全分析师
擅长从军事战略、国防安全、军备控制等角度分析事件影响。

你的分析特点：
- 评估军事冲突可能性
- 分析国防安全威胁
- 研究军备控制影响
- 考察军事同盟反应
- 预测地区安全稳定

分析方法：
1. 识别军事相关方
2. 评估军事能力对比
3. 分析战略意图
4. 预测军事行动可能性
5. 评估冲突升级风险

请用专业的军事安全术语进行分析，给出风险等级和态势判断。"""

    def get_analysis_framework(self) -> Dict[str, Any]:
        return {
            "冲突风险": "军事冲突的可能性评估",
            "安全威胁": "对国家安全的影响",
            "军备影响": "对军备控制和核扩散的影响",
            "同盟动态": "军事同盟的反应和调整",
            "地区稳定": "对地区安全格局的影响"
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
        """计算军事重要性分数"""
        base_score = event.get("importance", 3) / 5

        # 根据军事相关度调整
        military_relevance = event.get("military_relevance", "medium")
        relevance_factor = {"high": 0.3, "medium": 0.15, "low": 0.05}.get(military_relevance, 0.1)

        # 根据冲突风险调整
        conflict_risk = result.get("risk_assessment", {}).get("risk_level", 0.5)

        return min(base_score + relevance_factor + conflict_risk * 0.2, 1.0)
