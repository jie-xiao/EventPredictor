# Agent辩论系统
"""
多Agent辩论系统 - 允许不同角色之间进行讨论和观点碰撞

辩论模式:
- quick: 1轮 (仅初始分析)
- standard: 2轮 (初始分析 + 交叉审视)
- deep: 3轮 (初始分析 + 交叉审视 + 反驳/支持)
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json

from app.agents.roles import ROLES, AgentRole
from app.services.llm_service import llm_service, RoleAnalysisResponse, DebateResponse, CrossAnalysisResponse
from app.services.multi_agent_service import RoleAnalysisResult


@dataclass
class DebateRound:
    """辩论轮次"""
    round_number: int
    round_type: str  # initial, cross_review, rebuttal, synthesis
    analyses: List[Dict[str, Any]]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DebateResult:
    """辩论结果"""
    event: Dict[str, Any]
    depth: str
    rounds: List[DebateRound]
    final_synthesis: Dict[str, Any]
    agreement_scores: Dict[str, float]
    key_conflicts: List[Dict[str, Any]]
    consensus_points: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DebateOrchestrator:
    """辩论协调器"""

    def __init__(self):
        self.llm = llm_service

    async def run_debate(
        self,
        event: Dict[str, Any],
        role_ids: List[str],
        depth: str = "standard"
    ) -> DebateResult:
        """
        运行多轮辩论

        Args:
            event: 事件信息
            role_ids: 参与辩论的角色ID列表
            depth: 辩论深度 (quick/standard/deep)

        Returns:
            DebateResult: 辩论结果
        """
        # 获取角色定义
        roles = [ROLES[rid] for rid in role_ids if rid in ROLES]

        if not roles:
            raise ValueError("No valid roles specified for debate")

        rounds = []

        # Round 1: 初始分析 (所有模式都有)
        initial_round = await self._run_initial_analysis(event, roles)
        rounds.append(initial_round)

        # 根据深度决定后续轮次
        if depth in ["standard", "deep"]:
            # Round 2: 交叉审视
            cross_review_round = await self._run_cross_review(
                event, roles, initial_round.analyses
            )
            rounds.append(cross_review_round)

        if depth == "deep":
            # Round 3: 反驳/支持
            rebuttal_round = await self._run_rebuttal(
                event, roles, initial_round.analyses, cross_review_round.analyses
            )
            rounds.append(rebuttal_round)

        # 最终综合
        final_synthesis = await self._synthesize_debate(event, rounds)

        # 计算一致性分数
        agreement_scores = self._calculate_agreement_scores(rounds[-1].analyses)

        # 提取关键冲突和共识
        key_conflicts = self._extract_key_conflicts(rounds)
        consensus_points = self._extract_consensus(rounds)

        return DebateResult(
            event=event,
            depth=depth,
            rounds=rounds,
            final_synthesis=final_synthesis,
            agreement_scores=agreement_scores,
            key_conflicts=key_conflicts,
            consensus_points=consensus_points
        )

    async def _run_initial_analysis(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole]
    ) -> DebateRound:
        """第一轮：初始分析 - 各角色独立分析"""
        tasks = [
            self._analyze_single_role(event, role)
            for role in roles
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analyses = []
        for role, result in zip(roles, results):
            if isinstance(result, Exception):
                print(f"Initial analysis failed for {role.id}: {result}")
                analyses.append(self._create_fallback_analysis(role, event))
            else:
                analyses.append(result)

        return DebateRound(
            round_number=1,
            round_type="initial",
            analyses=analyses
        )

    async def _run_cross_review(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        initial_analyses: List[Dict[str, Any]]
    ) -> DebateRound:
        """第二轮：交叉审视 - 角色看到其他角色的观点后调整"""
        # 为每个角色准备其他角色的观点摘要
        tasks = [
            self._cross_review_single_role(event, role, initial_analyses)
            for role in roles
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analyses = []
        for role, result in zip(roles, results):
            if isinstance(result, Exception):
                print(f"Cross review failed for {role.id}: {result}")
                analyses.append(self._create_fallback_analysis(role, event))
            else:
                analyses.append(result)

        return DebateRound(
            round_number=2,
            round_type="cross_review",
            analyses=analyses
        )

    async def _run_rebuttal(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        initial_analyses: List[Dict[str, Any]],
        cross_review_analyses: List[Dict[str, Any]]
    ) -> DebateRound:
        """第三轮：反驳/支持 - 角色明确支持或反对特定观点"""
        tasks = [
            self._rebuttal_single_role(event, role, initial_analyses, cross_review_analyses)
            for role in roles
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analyses = []
        for role, result in zip(roles, results):
            if isinstance(result, Exception):
                print(f"Rebuttal failed for {role.id}: {result}")
                analyses.append(self._create_fallback_analysis(role, event))
            else:
                analyses.append(result)

        return DebateRound(
            round_number=3,
            round_type="rebuttal",
            analyses=analyses
        )

    async def _analyze_single_role(
        self,
        event: Dict[str, Any],
        role: AgentRole
    ) -> Dict[str, Any]:
        """单个角色的初始分析"""
        prompt = self._build_initial_prompt(event, role)

        try:
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=RoleAnalysisResponse,
                system_prompt=role.system_prompt
            )

            return {
                "role_id": role.id,
                "role_name": role.name,
                "category": role.category.value,
                "stance": response.stance,
                "reaction": response.reaction,
                "impact": response.impact,
                "timeline": response.timeline,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "statement": response.reaction.get("statement", "")
            }

        except Exception as e:
            print(f"Analysis error for {role.id}: {e}")
            return self._create_fallback_analysis(role, event)

    async def _cross_review_single_role(
        self,
        event: Dict[str, Any],
        role: AgentRole,
        all_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """单个角色的交叉审视"""
        # 准备其他角色的观点摘要
        other_views = self._summarize_other_views(role.id, all_analyses)

        prompt = f"""作为{role.name}，你已经完成了对事件的初步分析。

现在请考虑其他角色的观点：

{other_views}

基于这些信息，请重新评估你的立场和分析。你可以：
1. 坚持原有观点
2. 调整部分看法
3. 增加新的考量

事件信息：
- 标题：{event.get('title', 'N/A')}
- 描述：{event.get('description', 'N/A')}
- 类别：{event.get('category', 'N/A')}

请提供更新后的分析。"""

        try:
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=RoleAnalysisResponse,
                system_prompt=role.system_prompt
            )

            return {
                "role_id": role.id,
                "role_name": role.name,
                "category": role.category.value,
                "stance": response.stance,
                "reaction": response.reaction,
                "impact": response.impact,
                "timeline": response.timeline,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "statement": response.reaction.get("statement", ""),
                "round": "cross_review"
            }

        except Exception as e:
            print(f"Cross review error for {role.id}: {e}")
            return self._create_fallback_analysis(role, event)

    async def _rebuttal_single_role(
        self,
        event: Dict[str, Any],
        role: AgentRole,
        initial_analyses: List[Dict[str, Any]],
        cross_review_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """单个角色的反驳/支持"""
        # 准备所有观点的摘要
        all_views = self._prepare_all_views_for_rebuttal(initial_analyses, cross_review_analyses)

        prompt = f"""作为{role.name}，你已经看到了其他角色的观点。

请在以下方面明确表态：

1. 你支持哪些观点？（列出具体角色和观点）
2. 你反对哪些观点？（列出具体角色和观点）
3. 你认为最关键的问题是什么？
4. 调整后的置信度是多少？

其他角色的核心观点：
{all_views}

事件信息：
- 标题：{event.get('title', 'N/A')}
- 描述：{event.get('description', 'N/A')}

请提供你的反驳或支持声明。"""

        try:
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=DebateResponse,
                system_prompt=role.system_prompt
            )

            # 获取对应角色的初始分析作为基础
            initial = next(
                (a for a in initial_analyses if a["role_id"] == role.id),
                {}
            )

            return {
                "role_id": role.id,
                "role_name": role.name,
                "category": role.category.value,
                "stance": response.position,
                "reaction": initial.get("reaction", {}),
                "impact": initial.get("impact", {}),
                "timeline": initial.get("timeline", []),
                "confidence": response.adjusted_confidence,
                "reasoning": f"支持: {', '.join(response.supports)}; 反对: {', '.join(response.challenges)}",
                "statement": response.statement,
                "supports": response.supports,
                "challenges": response.challenges,
                "round": "rebuttal"
            }

        except Exception as e:
            print(f"Rebuttal error for {role.id}: {e}")
            return self._create_fallback_analysis(role, event)

    async def _synthesize_debate(
        self,
        event: Dict[str, Any],
        rounds: List[DebateRound]
    ) -> Dict[str, Any]:
        """综合辩论结果"""
        # 收集所有分析
        all_analyses = []
        for round_obj in rounds:
            all_analyses.extend(round_obj.analyses)

        # 使用LLM进行语义综合
        prompt = self._build_synthesis_prompt(event, all_analyses)

        try:
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=CrossAnalysisResponse,
                system_prompt="你是一位专业的分析师，负责综合多方观点并得出结论。"
            )

            return {
                "overall_trend": response.overall_trend,
                "trend_confidence": response.trend_confidence,
                "agreements": response.agreements,
                "conflicts": response.conflicts,
                "synergies": response.synergies,
                "consensus": response.consensus,
                "summary": self._generate_summary(event, all_analyses, response),
                "timeline": self._merge_timelines(all_analyses),
                "recommended_actions": self._generate_recommendations(response)
            }

        except Exception as e:
            print(f"Synthesis error: {e}")
            return self._create_fallback_synthesis(event, all_analyses)

    def _build_initial_prompt(self, event: Dict[str, Any], role: AgentRole) -> str:
        """构建初始分析提示词"""
        return f"""请分析以下事件，从{role.name}的角度进行反应分析：

事件标题：{event.get('title', 'N/A')}
事件描述：{event.get('description', 'N/A')}
事件类别：{event.get('category', 'N/A')}
严重程度：{event.get('importance', 3)}/5
时间：{event.get('timestamp', 'N/A')}

请提供：
1. 你的立场 (stance)
2. 反应 (reaction):
   - emotion: 情绪反应
   - action: 可能采取的行动
   - statement: 公开声明
3. 影响分析 (impact):
   - economic: 经济影响
   - political: 政治影响
   - social: 社会影响
4. 时间线 (timeline): 未来可能的发展节点
5. 置信度 (confidence): 0-1之间的数值
6. 推理过程 (reasoning): 详细的推理过程

请确保分析符合你作为{role.name}的角色特点。"""

    def _summarize_other_views(
        self,
        current_role_id: str,
        analyses: List[Dict[str, Any]]
    ) -> str:
        """为角色准备其他角色的观点摘要"""
        summaries = []

        for analysis in analyses:
            if analysis.get("role_id") == current_role_id:
                continue

            summary = f"""
【{analysis.get('role_name', '未知')}】
- 立场: {analysis.get('stance', 'N/A')}
- 行动: {analysis.get('reaction', {}).get('action', 'N/A')}
- 置信度: {analysis.get('confidence', 0) * 100:.0f}%
"""
            summaries.append(summary)

        return "\n".join(summaries) if summaries else "暂无其他角色的观点"

    def _prepare_all_views_for_rebuttal(
        self,
        initial: List[Dict[str, Any]],
        cross_review: List[Dict[str, Any]]
    ) -> str:
        """准备所有观点用于反驳轮"""
        views = []

        # 使用最新的分析结果
        for analysis in cross_review:
            view = f"""
【{analysis.get('role_name', '未知')}】
- 立场: {analysis.get('stance', 'N/A')}
- 关键观点: {analysis.get('reasoning', 'N/A')[:200]}...
- 置信度: {analysis.get('confidence', 0) * 100:.0f}%
"""
            views.append(view)

        return "\n".join(views)

    def _build_synthesis_prompt(
        self,
        event: Dict[str, Any],
        analyses: List[Dict[str, Any]]
    ) -> str:
        """构建综合分析提示词"""
        views_summary = "\n".join([
            f"【{a.get('role_name')}】立场: {a.get('stance')}; 置信度: {a.get('confidence', 0) * 100:.0f}%"
            for a in analyses
        ])

        return f"""请综合以下各方观点，进行最终分析：

事件：{event.get('title', 'N/A')}
描述：{event.get('description', 'N/A')}

各方观点：
{views_summary}

请提供：
1. agreements: 角色之间的共识点（每个包含 role1, role2, point, strength）
2. conflicts: 角色之间的冲突点（每个包含 role1, role2, point, severity）
3. synergies: 角色之间的协同效应
4. consensus: 所有关键共识的列表
5. overall_trend: 整体趋势（上涨/下跌/平稳/不确定）
6. trend_confidence: 趋势置信度 (0-1)"""

    def _calculate_agreement_scores(
        self,
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """计算角色之间的一致性分数"""
        scores = {}

        for i, a1 in enumerate(analyses):
            for j, a2 in enumerate(analyses):
                if i >= j:
                    continue

                # 基于置信度和立场相似度计算
                conf_diff = abs(a1.get("confidence", 0.5) - a2.get("confidence", 0.5))

                # 简化的一致性计算
                agreement = 1 - conf_diff

                key = f"{a1.get('role_id')}-{a2.get('role_id')}"
                scores[key] = round(agreement, 2)

        return scores

    def _extract_key_conflicts(self, rounds: List[DebateRound]) -> List[Dict[str, Any]]:
        """提取关键冲突"""
        conflicts = []

        # 从最后一轮分析中提取冲突
        if rounds:
            last_round = rounds[-1]
            for analysis in last_round.analyses:
                if "challenges" in analysis:
                    for challenge in analysis.get("challenges", []):
                        conflicts.append({
                            "from_role": analysis.get("role_name"),
                            "challenge": challenge
                        })

        return conflicts

    def _extract_consensus(self, rounds: List[DebateRound]) -> List[str]:
        """提取共识点"""
        consensus = []

        # 从最后一轮分析中提取支持
        if rounds:
            last_round = rounds[-1]
            for analysis in last_round.analyses:
                if "supports" in analysis:
                    for support in analysis.get("supports", []):
                        if support not in consensus:
                            consensus.append(f"{analysis.get('role_name')}: {support}")

        return consensus

    def _generate_summary(
        self,
        event: Dict[str, Any],
        analyses: List[Dict[str, Any]],
        synthesis: CrossAnalysisResponse
    ) -> str:
        """生成综合摘要"""
        return f"""经过多轮辩论分析，事件「{event.get('title', 'N/A')}」的综合评估如下：

整体趋势: {synthesis.overall_trend}
趋势置信度: {synthesis.trend_confidence * 100:.0f}%

关键共识:
{chr(10).join(['- ' + c for c in synthesis.consensus[:3]])}

主要冲突:
{chr(10).join(['- ' + c.get('point', '') for c in synthesis.conflicts[:2]])}

建议关注后续发展。"""

    def _merge_timelines(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并时间线"""
        all_timeline = []
        seen_times = set()

        for analysis in analyses:
            for item in analysis.get("timeline", []):
                time_key = item.get("time", "")
                if time_key and time_key not in seen_times:
                    seen_times.add(time_key)
                    all_timeline.append(item)

        # 按概率排序
        all_timeline.sort(key=lambda x: x.get("probability", 0), reverse=True)

        return all_timeline[:5]

    def _generate_recommendations(self, synthesis: CrossAnalysisResponse) -> List[str]:
        """生成建议"""
        recommendations = []

        for synergy in synthesis.synergies[:2]:
            if isinstance(synergy, dict):
                recommendations.append(f"利用协同: {synergy.get('description', synergy)}")
            else:
                recommendations.append(f"利用协同: {synergy}")

        for consensus in synthesis.consensus[:2]:
            recommendations.append(f"共识基础: {consensus}")

        return recommendations

    def _create_fallback_analysis(
        self,
        role: AgentRole,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建备用分析"""
        return {
            "role_id": role.id,
            "role_name": role.name,
            "category": role.category.value,
            "stance": role.stance,
            "reaction": {
                "emotion": "关注",
                "action": "评估影响",
                "statement": f"作为{role.name}，我们正在关注该事件的发展。"
            },
            "impact": {
                "economic": "需要评估",
                "political": "需要评估",
                "social": "需要评估"
            },
            "timeline": [
                {"time": "短期", "event": "观察评估", "probability": 0.6}
            ],
            "confidence": 0.5,
            "reasoning": f"基于{role.name}的角色特点进行的分析"
        }

    def _create_fallback_synthesis(
        self,
        event: Dict[str, Any],
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """创建备用综合分析"""
        avg_confidence = sum(a.get("confidence", 0.5) for a in analyses) / len(analyses) if analyses else 0.5

        return {
            "overall_trend": "平稳",
            "trend_confidence": avg_confidence,
            "agreements": [],
            "conflicts": [],
            "synergies": [],
            "consensus": ["各方都在关注事件发展"],
            "summary": f"综合分析完成，整体趋势相对平稳。",
            "timeline": [],
            "recommended_actions": ["持续关注事态发展"]
        }


# 全局辩论协调器实例
debate_orchestrator = DebateOrchestrator()
