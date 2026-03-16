# 地缘政治分析Agent
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult


class GeopoliticalAgent(BaseSpecializedAgent):
    """
    地缘政治分析Agent

    专注于：
    - 国家间关系
    - 地区权力平衡
    - 外交影响
    - 国际组织反应
    - 主权和领土问题
    """

    def __init__(self):
        super().__init__(
            agent_type="geopolitical",
            agent_name="地缘政治分析师",
            description="分析国际关系、地区权力平衡、外交影响等"
        )

    def get_system_prompt(self) -> str:
        return """你是一位资深的地缘政治分析师，拥有丰富的国际关系研究经验。

你的专业领域包括：
- 大国博弈与权力平衡
- 地区冲突与合作
- 外交政策分析
- 国际组织（联合国、欧盟、北约等）的作用
- 主权和领土争端
- 能源地缘政治

分析原则：
1. 从多国视角分析事件影响
2. 考虑历史背景和文化因素
3. 评估短期和长期战略影响
4. 识别潜在的联盟变化
5. 分析对国际秩序的影响

你的分析应该客观、深入、具有战略眼光。"""

    def get_analysis_framework(self) -> Dict[str, Any]:
        return {
            "直接涉及方": "识别事件直接涉及的国家和行为体",
            "间接利益相关方": "识别虽未直接参与但受影响的各方",
            "历史背景": "相关的历史事件和长期趋势",
            "权力动态": "事件如何改变地区或全球权力平衡",
            "外交影响": "对外交关系的潜在影响",
            "国际组织": "联合国等国际组织的可能反应",
            "盟友关系": "事件对同盟体系的影响"
        }

    async def analyze(self, event: Dict[str, Any]) -> AgentAnalysisResult:
        """执行地缘政治分析"""
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
        """计算地缘政治重要性分数"""
        base_score = event.get("importance", 3) / 5

        # 根据涉及国家数量调整
        involved_countries = len(event.get("involved_countries", []))
        country_factor = min(involved_countries * 0.1, 0.3)

        # 根据风险等级调整
        risk_level = result.get("risk_assessment", {}).get("risk_level", 0.5)

        return min(base_score + country_factor + risk_level * 0.2, 1.0)
