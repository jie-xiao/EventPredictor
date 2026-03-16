# 社会舆情分析Agent
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult


class SocialAgent(BaseSpecializedAgent):
    """
    社会舆情分析Agent

    专注于：
    - 公众舆论反应
    - 社会稳定影响
    - 文化价值观冲突
    - 社会群体分化
    - 民意走向预测
    """

    def __init__(self):
        super().__init__(
            agent_type="social",
            agent_name="社会舆情分析师",
            description="分析公众舆论、社会稳定、文化价值观等"
        )

    def get_system_prompt(self) -> str:
        return """你是一位资深的社会舆情分析师
擅长从社会心理、舆论传播、群体行为等角度分析事件影响。

你的分析特点：
- 洞察公众情绪变化
- 追踪舆论传播路径
- 预测社会反应
- 分析群体分化
- 评估社会稳定风险

分析方法：
1. 识别受影响的社会群体
2. 分析不同群体的反应差异
3. 追踪舆论传播链条
4. 预测社会行动趋势
5. 评估社会治理挑战

请用社会学和传播学的专业术语进行分析，关注民意走向和社会稳定。"""

    def get_analysis_framework(self) -> Dict[str, Any]:
        return {
            "舆论反应": "各大社交媒体和主流舆论的反应预测",
            "社会稳定": "对社会秩序和稳定的影响",
            "群体分化": "不同社会群体的立场差异",
            "文化冲突": "可能引发的文化价值观冲突",
            "民意走向": "公众态度的演变趋势"
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
        """计算社会重要性分数"""
        base_score = event.get("importance", 3) / 5

        # 根据社会关注度调整
        public_attention = event.get("public_attention", "medium")
        attention_factor = {"high": 0.25, "medium": 0.15, "low": 0.05}.get(public_attention, 0.1)

        # 根据稳定风险调整
        stability_risk = result.get("risk_assessment", {}).get("risk_level", 0.5)

        return min(base_score + attention_factor + stability_risk * 0.15, 1.0)
