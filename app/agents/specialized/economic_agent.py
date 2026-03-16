# 经济分析Agent
from typing import Dict, Any, List
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult


class EconomicAgent(BaseSpecializedAgent):
    """
    经济分析Agent

    专注于：
    - 宏观经济影响
    - 产业链影响
    - 金融市场反应
    - 贸易关系
    - 投资环境
    """

    def __init__(self):
        super().__init__(
            agent_type="economic",
            agent_name="经济分析师",
            description="分析宏观经济、产业链、金融市场、贸易等"
        )

    def get_system_prompt(self) -> str:
        return """你是一位资深的经济分析师，擅长从宏观经济、产业、金融、贸易等角度分析事件影响。

你的分析特点：
- 关注GDP、通胀、就业等宏观指标
- 分析产业链上下游影响
- 评估金融市场波动
- 研究国际贸易格局变化
- 考察投资环境和商业信心

分析方法：
1. 识别直接经济影响
2. 追踪间接连锁效应
3. 评估短期和长期影响
4. 量化经济成本和收益
5. 提出经济政策建议

请用专业的经济学语言进行分析，给出具体的数据和指标预测。"""

    def get_analysis_framework(self) -> Dict[str, Any]:
        return {
            "宏观影响": "对GDP、通胀、就业的影响",
            "产业影响": "受影响的主要行业",
            "金融市场": "股市、债市、汇率的预期反应",
            "贸易影响": "进出口贸易的变化",
            "投资环境": "国内外投资信心的影响"
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
        """计算经济重要性分数"""
        base_score = event.get("importance", 3) / 5

        # 根据涉及的经济体量调整
        economic_scale = event.get("economic_scale", "medium")
        scale_factor = {"large": 0.3, "medium": 0.2, "small": 0.1}.get(economic_scale, 0.15)

        # 根据金融影响调整
        financial_impact = result.get("risk_assessment", {}).get("risk_level", 0.5)

        return min(base_score + scale_factor + financial_impact * 0.2, 1.0)
