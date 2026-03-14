# 情景推演服务 - 生成多情景预测分析
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.services.llm_service import llm_service, ScenarioResponse, Scenario, ScenarioStep


class ScenarioService:
    """情景推演服务 - 生成多个可能的未来发展情景"""

    def __init__(self):
        self.llm = llm_service

    async def generate_scenarios(
        self,
        event: Dict[str, Any],
        analysis_result: Optional[Dict[str, Any]] = None,
        num_scenarios: int = 3
    ) -> Dict[str, Any]:
        """
        生成情景推演

        Args:
            event: 事件信息
            analysis_result: 之前的分析结果（可选）
            num_scenarios: 生成的情景数量 (2-5)

        Returns:
            包含多个情景的推演结果
        """
        # 限制情景数量
        num_scenarios = max(2, min(5, num_scenarios))

        # 构建提示词
        prompt = self._build_scenario_prompt(event, analysis_result, num_scenarios)

        try:
            # 使用LLM生成结构化情景
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=ScenarioResponse,
                system_prompt=self._get_system_prompt()
            )

            return {
                "event_id": event.get("id", "unknown"),
                "scenarios": [self._scenario_to_dict(s) for s in response.scenarios],
                "most_likely_scenario": response.most_likely_scenario,
                "overall_assessment": response.overall_assessment,
                "key_uncertainties": response.key_uncertainties,
                "recommendation": response.recommendation,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"Scenario generation failed: {e}")
            # 返回基于规则的备用情景
            return self._generate_fallback_scenarios(event, num_scenarios)

    def _build_scenario_prompt(
        self,
        event: Dict[str, Any],
        analysis_result: Optional[Dict[str, Any]],
        num_scenarios: int
    ) -> str:
        """构建情景推演提示词"""

        # 事件基础信息
        event_info = f"""
事件标题：{event.get('title', 'N/A')}
事件描述：{event.get('description', 'N/A')}
事件类别：{event.get('category', 'N/A')}
严重程度：{event.get('importance', 3)}/5
时间：{event.get('timestamp', 'N/A')}
"""

        # 如果有分析结果，加入上下文
        analysis_context = ""
        if analysis_result:
            # 提取角色分析摘要
            role_summaries = []
            for analysis in analysis_result.get("analyses", [])[:3]:
                role_summaries.append(f"- {analysis.get('role_name', 'Unknown')}: {analysis.get('stance', 'N/A')}")

            if role_summaries:
                analysis_context = f"""
已有分析摘要：
{chr(10).join(role_summaries)}

共识点：{', '.join(analysis_result.get('cross_analysis', {}).get('consensus', ['无']))}
"""

        prompt = f"""请针对以下事件生成{num_scenarios}个可能的未来发展情景。

{event_info}
{analysis_context}

请生成{num_scenarios}个不同的情景，包括：
1. 乐观情景 - 事件向积极方向发展
2. 基准情景 - 最可能的发展路径
3. 悲观情景 - 事件可能恶化的情况

对于每个情景，请提供：
- 情景ID和名称
- 情景描述
- 发生概率 (0-1)
- 时间线步骤（每个步骤包含时间、描述、概率、关键事件）
- 关键影响因素
- 潜在结果

最后请给出：
- 最可能的情景名称
- 整体评估
- 关键不确定因素列表
- 战略建议

请确保分析客观、全面，考虑多种可能性。"""

        return prompt

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位资深的政治经济分析师和战略规划专家，擅长进行情景分析和战略推演。

你的分析特点是：
1. 客观性：基于事实和逻辑，避免主观偏见
2. 全面性：考虑政治、经济、社会、技术等多维因素
3. 动态性：考虑事件的动态演变和相互作用
4. 实用性：提供具体可操作的建议

在进行情景推演时，你会：
- 识别关键驱动因素和不确定因素
- 构建逻辑一致的情景逻辑链
- 评估各情景的概率和影响
- 提供清晰的战略建议"""

    def _scenario_to_dict(self, scenario: Scenario) -> Dict[str, Any]:
        """将情景模型转换为字典"""
        return {
            "id": scenario.id,
            "name": scenario.name,
            "description": scenario.description,
            "probability": scenario.probability,
            "steps": [
                {
                    "time": step.time,
                    "description": step.description,
                    "probability": step.probability,
                    "key_events": step.key_events
                }
                for step in scenario.steps
            ],
            "key_factors": scenario.key_factors,
            "potential_outcomes": scenario.potential_outcomes
        }

    def _generate_fallback_scenarios(
        self,
        event: Dict[str, Any],
        num_scenarios: int
    ) -> Dict[str, Any]:
        """生成备用情景（当LLM调用失败时）"""
        importance = event.get("importance", 3)

        scenarios = [
            {
                "id": "optimistic",
                "name": "乐观情景",
                "description": "事件得到妥善处理，影响逐步减弱",
                "probability": 0.25,
                "steps": [
                    {
                        "time": "1-3天",
                        "description": "各方达成初步共识",
                        "probability": 0.7,
                        "key_events": ["对话开启", "紧张缓解"]
                    },
                    {
                        "time": "1-2周",
                        "description": "问题得到实质性解决",
                        "probability": 0.5,
                        "key_events": ["协议达成", "影响消散"]
                    }
                ],
                "key_factors": ["建设性对话", "合作意愿"],
                "potential_outcomes": ["局势稳定", "关系改善"]
            },
            {
                "id": "baseline",
                "name": "基准情景",
                "description": "事件按当前趋势发展，影响有限",
                "probability": 0.50,
                "steps": [
                    {
                        "time": "1-3天",
                        "description": "各方观望评估",
                        "probability": 0.8,
                        "key_events": ["持续关注", "准备应对"]
                    },
                    {
                        "time": "1-2周",
                        "description": "局势趋于稳定",
                        "probability": 0.6,
                        "key_events": ["常态恢复", "影响可控"]
                    }
                ],
                "key_factors": ["政策稳定性", "市场韧性"],
                "potential_outcomes": ["影响可控", "逐步恢复"]
            },
            {
                "id": "pessimistic",
                "name": "悲观情景",
                "description": "事态可能升级，影响扩大",
                "probability": 0.25,
                "steps": [
                    {
                        "time": "1-3天",
                        "description": "紧张局势加剧",
                        "probability": 0.4,
                        "key_events": ["冲突升级", "措施升级"]
                    },
                    {
                        "time": "1-2周",
                        "description": "影响持续扩大",
                        "probability": 0.3,
                        "key_events": ["连锁反应", "广泛影响"]
                    }
                ],
                "key_factors": ["政策不确定性", "外部干预"],
                "potential_outcomes": ["长期影响", "结构性变化"]
            }
        ]

        return {
            "event_id": event.get("id", "unknown"),
            "scenarios": scenarios[:num_scenarios],
            "most_likely_scenario": "基准情景",
            "overall_assessment": f"基于事件严重程度({importance}/5)，预计事态发展具有中等不确定性",
            "key_uncertainties": ["政策响应", "外部因素", "市场反应"],
            "recommendation": "建议持续关注事态发展，准备多种应对方案",
            "generated_at": datetime.utcnow().isoformat()
        }

    async def refine_scenario(
        self,
        event: Dict[str, Any],
        scenario_id: str,
        new_information: str
    ) -> Dict[str, Any]:
        """
        根据新信息优化特定情景

        Args:
            event: 事件信息
            scenario_id: 要优化的情景ID
            new_information: 新获得的信息

        Returns:
            更新后的情景
        """
        prompt = f"""基于新获得的信息，请更新情景"{scenario_id}"的预测：

事件：{event.get('title', 'N/A')}

新信息：
{new_information}

请分析这些新信息如何影响情景的发展概率和路径，并更新：
1. 情景概率（是否需要调整）
2. 时间线（是否有新的发展节点）
3. 关键因素（是否有新的影响因素）
4. 潜在结果（是否有新的可能结果）
"""

        try:
            response = await self.llm.generate(prompt)
            return {
                "scenario_id": scenario_id,
                "update": response,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Scenario refinement failed: {e}")
            return {"error": str(e)}


# 全局服务实例
scenario_service = ScenarioService()
