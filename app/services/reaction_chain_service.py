# 反应链服务 - 实现多方反应的迭代推演
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.agents.roles import ROLES, AgentRole
from app.services.llm_service import llm_service
from app.agents.reaction_chain import (
    InfluenceAnalyzer,
    ConvergenceDetector,
    TimelineBuilder,
    ChainReasoner
)


class ReactionRound:
    """单轮反应结果"""
    def __init__(
        self,
        round_number: int,
        role_id: str,
        role_name: str,
        reaction: Dict[str, Any],
        affected_by: List[str]  # 受哪些角色本轮反应影响
    ):
        self.round_number = round_number
        self.role_id = role_id
        self.role_name = role_name
        self.reaction = reaction
        self.affected_by = affected_by
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_number": self.round_number,
            "role_id": self.role_id,
            "role_name": self.role_name,
            "reaction": self.reaction,
            "affected_by": self.affected_by,
            "timestamp": self.timestamp
        }


class TimelineEvent:
    """时间线事件"""
    def __init__(
        self,
        time: str,
        event_type: str,  # initial_event, reaction, state_change
        description: str,
        involved_roles: List[str],
        details: Dict[str, Any] = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.time = time
        self.event_type = event_type
        self.description = description
        self.involved_roles = involved_roles
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "time": self.time,
            "event_type": self.event_type,
            "description": self.description,
            "involved_roles": self.involved_roles,
            "details": self.details,
            "timestamp": self.timestamp
        }


class ChainEvent:
    """事件链中的单个事件"""
    def __init__(
        self,
        event_id: str,
        title: str,
        description: str,
        category: str = "Other",
        importance: int = 3,
        timestamp: str = ""
    ):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.category = category
        self.importance = importance
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "importance": self.importance,
            "timestamp": self.timestamp
        }


class ReactionChainService:
    """反应链服务 - 实现多方反应的迭代推演"""

    def __init__(self):
        self.llm = llm_service
        # 初始化Agent模块
        self.influence_analyzer = InfluenceAnalyzer()
        self.convergence_detector = ConvergenceDetector(threshold=0.85)
        self.timeline_builder = TimelineBuilder()
        self.chain_reasoner = ChainReasoner()

    async def run_reaction_chain(
        self,
        event: Dict[str, Any],
        role_ids: List[str],
        max_rounds: int = 3,
        convergence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        运行反应链分析

        Args:
            event: 初始事件
            role_ids: 参与分析的角色ID列表
            max_rounds: 最大轮次
            convergence_threshold: 收敛阈值

        Returns:
            包含所有轮次反应的时间线
        """
        # 获取角色定义
        roles = [ROLES[rid] for rid in role_ids if rid in ROLES]
        role_map = {r.id: r for r in roles}

        if not roles:
            return {"error": "No valid roles specified"}

        # 重置所有分析器
        self.influence_analyzer.reset()
        self.convergence_detector = ConvergenceDetector(threshold=convergence_threshold)
        self.timeline_builder.reset()

        # 初始化
        all_rounds: List[ReactionRound] = []

        # 添加初始事件到时间线
        self.timeline_builder.add_initial_event(event)

        # 记录每轮各角色的反应
        previous_round_reactions: Dict[str, Dict[str, Any]] = {}

        # ============ 第一轮：初始反应 ============
        first_round_reactions = await self._run_first_round(
            event=event,
            roles=roles,
            role_map=role_map
        )
        all_rounds.extend(first_round_reactions)

        # 记录第一轮反应
        for r in first_round_reactions:
            previous_round_reactions[r.role_id] = r.reaction

        # 添加到时间线并捕获状态快照
        self.timeline_builder.add_reaction_round(1, previous_round_reactions)
        self.timeline_builder.capture_state_snapshot("T+1", previous_round_reactions)

        # ============ 后续轮次：迭代分析 ============
        converged = False
        for round_num in range(2, max_rounds + 1):
            # 检查收敛
            convergence_result = self.convergence_detector.check_convergence(
                current_round=round_num - 1,
                current_reactions=previous_round_reactions,
                previous_reactions=previous_round_reactions
            )

            if convergence_result.is_converged:
                self.timeline_builder.add_convergence_event(
                    time=f"T+{round_num-1}",
                    convergence_score=convergence_result.convergence_score,
                    converged_roles=convergence_result.stable_aspects
                )
                converged = True
                break

            # 分析上一轮的影响力关系
            influence_relations = self.influence_analyzer.analyze_round_influence(
                round_number=round_num,
                current_reactions=previous_round_reactions,
                previous_reactions=previous_round_reactions,
                role_map=role_map
            )

            # 为每个影响力关系添加时间线事件
            for rel in influence_relations:
                self.timeline_builder.add_influence_event(
                    time=f"T+{round_num-1}",
                    source_role=rel.source_role_name,
                    target_role=rel.target_role_name,
                    influence_type=rel.influence_type,
                    influence_strength=rel.influence_strength,
                    reasoning=rel.reasoning
                )

            # 执行本轮分析
            current_round_reactions = await self._run_iteration_round(
                event=event,
                roles=roles,
                role_map=role_map,
                round_number=round_num,
                previous_reactions=previous_round_reactions,
                influence_relations=influence_relations,
                convergence_hints={
                    "convergence_score": convergence_result.convergence_score,
                    "recommendation": convergence_result.recommendation
                }
            )
            all_rounds.extend(current_round_reactions)

            # 更新记录
            new_reactions = {}
            for r in current_round_reactions:
                new_reactions[r.role_id] = r.reaction
                previous_round_reactions[r.role_id] = r.reaction

            # 添加到时间线
            self.timeline_builder.add_reaction_round(round_num, new_reactions)
            self.timeline_builder.capture_state_snapshot(f"T+{round_num}", new_reactions)

        # ============ 分析结果 ============
        # 分析反应演变
        evolution = self._analyze_evolution(all_rounds, roles)

        # 获取影响力网络
        influence_network = self.influence_analyzer.get_influence_network()

        # 获取意见领袖
        opinion_leaders = self.influence_analyzer.get_opinion_leaders()

        # 获取易受影响者
        most_influenced = self.influence_analyzer.get_most_influenced()

        # 生成最终推演结论
        conclusion = self._generate_conclusion(
            event=event,
            all_rounds=all_rounds,
            evolution=evolution,
            influence_network=influence_network,
            opinion_leaders=opinion_leaders,
            converged=converged
        )

        return {
            "event": event,
            "roles_analyzed": [r.id for r in roles],
            "total_rounds": len(set(r.round_number for r in all_rounds)),
            "converged": converged,
            "all_reactions": [r.to_dict() for r in all_rounds],
            "timeline": self.timeline_builder.get_timeline(),
            "timeline_tree": self.timeline_builder.get_timeline_tree(),
            "state_evolution": self.timeline_builder.get_state_evolution(),
            "evolution": evolution,
            "influence_network": influence_network,
            "opinion_leaders": opinion_leaders,
            "most_influenced": most_influenced,
            "convergence_trend": self.convergence_detector.get_convergence_trend(),
            "conclusion": conclusion,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def run_event_chain(
        self,
        events: List[Dict[str, Any]],
        role_ids: List[str],
        max_rounds_per_event: int = 2
    ) -> Dict[str, Any]:
        """
        运行事件链分析 - 多个相关事件的串联分析

        Args:
            events: 事件列表（按时间顺序）
            role_ids: 参与分析的角色ID列表
            max_rounds_per_event: 每个事件的反应轮次

        Returns:
            事件链分析结果
        """
        if not events:
            return {"error": "No events provided"}

        # 获取角色定义
        roles = [ROLES[rid] for rid in role_ids if rid in ROLES]
        role_map = {r.id: r for r in roles}

        if not roles:
            return {"error": "No valid roles specified"}

        # 重置分析器
        self.influence_analyzer.reset()
        self.convergence_detector = ConvergenceDetector()
        self.timeline_builder.reset()

        chain_results = []
        accumulated_context: Dict[str, Dict[str, Any]] = {}
        all_event_influences: List[Dict[str, Any]] = []

        # 按顺序分析每个事件
        for idx, event in enumerate(events):
            # 构建包含前面事件影响的上下文
            previous_events_context = self._build_event_chain_context(
                events[:idx],
                accumulated_context
            )

            # 运行该事件的反应链
            event_result = await self._run_single_event_analysis(
                event=event,
                roles=roles,
                role_map=role_map,
                event_index=idx,
                max_rounds=max_rounds_per_event,
                previous_events_context=previous_events_context,
                accumulated_reactions=accumulated_context
            )

            chain_results.append(event_result)

            # 分析事件间影响
            if idx > 0:
                inter_influence = await self._analyze_inter_event_influence(
                    previous_event=events[idx - 1],
                    current_event=event,
                    previous_reactions=chain_results[idx - 1].get("final_reactions", {}),
                    current_reactions=event_result.get("final_reactions", {})
                )
                all_event_influences.append(inter_influence)

            # 更新累积上下文
            for r in event_result.get("final_reactions", {}).values():
                role_id = r.get("role_id")
                if role_id:
                    accumulated_context[role_id] = r.get("reaction", {})

        # 分析事件间的关联
        inter_event_analysis = self._analyze_inter_event_relations(
            chain_results,
            all_event_influences
        )

        # 生成事件链推演结论
        chain_conclusion = self._generate_event_chain_conclusion(
            events,
            chain_results,
            inter_event_analysis
        )

        return {
            "events": [e.get("title", "Unknown") for e in events],
            "event_count": len(events),
            "chain_results": chain_results,
            "inter_event_analysis": inter_event_analysis,
            "event_influences": all_event_influences,
            "timeline": self.timeline_builder.get_timeline(),
            "conclusion": chain_conclusion,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _run_first_round(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        role_map: Dict[str, AgentRole]
    ) -> List[ReactionRound]:
        """运行第一轮分析（独立分析）"""
        from app.agents.reaction_chain.chain_reasoner import ReasoningContext

        contexts = []
        for role in roles:
            context = ReasoningContext(
                event=event,
                round_number=1,
                role_id=role.id,
                role_name=role.name,
                previous_reactions={},
                influence_hints=[]
            )
            contexts.append(context)

        role_prompts = {r.id: r.system_prompt for r in roles}
        results = await self.chain_reasoner.batch_reason(contexts, role_prompts)

        rounds = []
        for result in results:
            r = ReactionRound(
                round_number=1,
                role_id=result["role_id"],
                role_name=result["role_name"],
                reaction=result,
                affected_by=[]
            )
            rounds.append(r)

        return rounds

    async def _run_iteration_round(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        role_map: Dict[str, AgentRole],
        round_number: int,
        previous_reactions: Dict[str, Dict[str, Any]],
        influence_relations: List[Any],
        convergence_hints: Dict[str, Any]
    ) -> List[ReactionRound]:
        """运行迭代轮次分析"""
        from app.agents.reaction_chain.chain_reasoner import ReasoningContext

        # 为每个角色构建影响提示
        role_influence_hints = {}
        for rel in influence_relations:
            if rel.target_role_id not in role_influence_hints:
                role_influence_hints[rel.target_role_id] = []
            role_influence_hints[rel.target_role_id].append({
                "source": rel.source_role_name,
                "type": rel.influence_type,
                "strength": rel.influence_strength
            })

        contexts = []
        for role in roles:
            context = ReasoningContext(
                event=event,
                round_number=round_number,
                role_id=role.id,
                role_name=role.name,
                previous_reactions=previous_reactions,
                influence_hints=role_influence_hints.get(role.id, []),
                convergence_hints=convergence_hints
            )
            contexts.append(context)

        role_prompts = {r.id: r.system_prompt for r in roles}
        results = await self.chain_reasoner.batch_reason(contexts, role_prompts)

        rounds = []
        for result in results:
            # 确定受哪些角色影响
            influenced_by = result.get("influenced_by", [])
            if not influenced_by:
                influenced_by = [
                    rid for rid in previous_reactions.keys()
                    if rid != result["role_id"]
                ]

            r = ReactionRound(
                round_number=round_number,
                role_id=result["role_id"],
                role_name=result["role_name"],
                reaction=result,
                affected_by=influenced_by
            )
            rounds.append(r)

        return rounds

    async def _run_single_event_analysis(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        role_map: Dict[str, AgentRole],
        event_index: int,
        max_rounds: int,
        previous_events_context: Dict[str, Any],
        accumulated_reactions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """运行单个事件的分析（带事件链上下文）"""

        # 添加事件到时间线
        if event_index == 0:
            self.timeline_builder.add_initial_event(event)
        else:
            # 后续事件作为状态变化节点
            self.timeline_builder.add_state_change(
                time=f"T+E{event_index}",
                role_id="system",
                change_description=f"新事件：{event.get('title', '')}",
                old_state={},
                new_state=event
            )

        # 运行反应链
        all_rounds = []
        current_reactions = {}

        for round_num in range(1, max_rounds + 1):
            if round_num == 1:
                rounds = await self._run_first_round_with_context(
                    event=event,
                    roles=roles,
                    role_map=role_map,
                    round_number=round_num,
                    previous_events_context=previous_events_context,
                    accumulated_reactions=accumulated_reactions
                )
            else:
                rounds = await self._run_iteration_round(
                    event=event,
                    roles=roles,
                    role_map=role_map,
                    round_number=round_num,
                    previous_reactions=current_reactions,
                    influence_relations=[],
                    convergence_hints={}
                )

            all_rounds.extend(rounds)

            for r in rounds:
                current_reactions[r.role_id] = r.reaction

        # 构建最终反应
        final_reactions = {}
        for role_id, reaction in current_reactions.items():
            role = role_map.get(role_id)
            final_reactions[role_id] = {
                "role_id": role_id,
                "role_name": role.name if role else role_id,
                "reaction": reaction
            }

        return {
            "event_index": event_index,
            "event": event,
            "all_rounds": [r.to_dict() for r in all_rounds],
            "final_reactions": final_reactions,
            "rounds_executed": max_rounds
        }

    async def _run_first_round_with_context(
        self,
        event: Dict[str, Any],
        roles: List[AgentRole],
        role_map: Dict[str, AgentRole],
        round_number: int,
        previous_events_context: Dict[str, Any],
        accumulated_reactions: Dict[str, Dict[str, Any]]
    ) -> List[ReactionRound]:
        """运行带上下文的第一轮分析"""
        from app.agents.reaction_chain.chain_reasoner import ReasoningContext

        # 构建影响提示（来自之前事件的累积影响）
        influence_hints_map = {}
        if previous_events_context and accumulated_reactions:
            for role_id, prev_reaction in accumulated_reactions.items():
                if role_id not in influence_hints_map:
                    influence_hints_map[role_id] = []
                influence_hints_map[role_id].append({
                    "source": f"之前事件中该角色的立场",
                    "type": "continuity",
                    "strength": 0.7
                })

        contexts = []
        for role in roles:
            context = ReasoningContext(
                event=event,
                round_number=round_number,
                role_id=role.id,
                role_name=role.name,
                previous_reactions=accumulated_reactions,  # 包含之前事件的影响
                influence_hints=influence_hints_map.get(role.id, [])
            )
            contexts.append(context)

        role_prompts = {r.id: r.system_prompt for r in roles}
        results = await self.chain_reasoner.batch_reason(contexts, role_prompts)

        rounds = []
        for result in results:
            r = ReactionRound(
                round_number=round_number,
                role_id=result["role_id"],
                role_name=result["role_name"],
                reaction=result,
                affected_by=list(accumulated_reactions.keys()) if accumulated_reactions else []
            )
            rounds.append(r)

        return rounds

    async def _analyze_inter_event_influence(
        self,
        previous_event: Dict[str, Any],
        current_event: Dict[str, Any],
        previous_reactions: Dict[str, Any],
        current_reactions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析事件间的影响"""
        # 简化实现 - 可以后续使用LLM增强
        influence_types = {
            "amplify": 0,
            "attenuate": 0,
            "neutral": 0,
            "transform": 0
        }

        # 分析各角色反应的变化
        stance_shifts = []
        for role_id in current_reactions:
            prev = previous_reactions.get(role_id, {}).get("reaction", {})
            curr = current_reactions.get(role_id, {}).get("reaction", {})

            prev_conf = prev.get("confidence", 0.5)
            curr_conf = curr.get("confidence", 0.5)

            if curr_conf > prev_conf + 0.1:
                influence_types["amplify"] += 1
            elif curr_conf < prev_conf - 0.1:
                influence_types["attenuate"] += 1
            else:
                influence_types["neutral"] += 1

            if prev.get("emotion") != curr.get("emotion"):
                stance_shifts.append(role_id)

        if len(stance_shifts) > len(current_reactions) * 0.5:
            influence_types["transform"] = 1

        dominant_type = max(influence_types, key=influence_types.get)

        return {
            "previous_event": previous_event.get("title", ""),
            "current_event": current_event.get("title", ""),
            "dominant_influence": dominant_type,
            "influence_distribution": influence_types,
            "stance_shifts": stance_shifts,
            "affected_roles": list(set(
                list(previous_reactions.keys()) + list(current_reactions.keys())
            ))
        }

    def _analyze_evolution(
        self,
        all_rounds: List[ReactionRound],
        roles: List[AgentRole]
    ) -> Dict[str, Any]:
        """分析反应演变"""

        evolution = {}

        for role in roles:
            role_id = role.id
            role_rounds = [r for r in all_rounds if r.role_id == role_id]

            if len(role_rounds) < 2:
                continue

            # 收集反应变化
            emotions = [r.reaction.get("emotion", "") for r in role_rounds]
            actions = [r.reaction.get("action", "") for r in role_rounds]
            confidences = [r.reaction.get("confidence", 0.5) for r in role_rounds]
            stance_changes = [r.reaction.get("stance_change", "") for r in role_rounds]

            # 计算变化趋势
            confidence_trend = "stable"
            if len(confidences) >= 2:
                if confidences[-1] > confidences[0] + 0.1:
                    confidence_trend = "increasing"
                elif confidences[-1] < confidences[0] - 0.1:
                    confidence_trend = "decreasing"

            evolution[role_id] = {
                "role_name": role.name,
                "rounds": len(role_rounds),
                "emotion_evolution": emotions,
                "action_evolution": actions,
                "confidence_evolution": confidences,
                "confidence_trend": confidence_trend,
                "stance_changes": [s for s in stance_changes if s],
                "summary": self._summarize_evolution(emotions, actions, confidence_trend)
            }

        return evolution

    def _summarize_evolution(
        self,
        emotions: List[str],
        actions: List[str],
        confidence_trend: str
    ) -> str:
        """总结演变趋势"""

        if len(emotions) < 2:
            return "反应趋于稳定"

        first = emotions[0] if emotions else ""
        last = emotions[-1] if emotions else ""

        trend_desc = {
            "increasing": "置信度提升",
            "decreasing": "置信度下降",
            "stable": "保持稳定"
        }

        if first != last:
            return f"从{first}演变为{last}，{trend_desc.get(confidence_trend, '')}"
        else:
            return f"情绪保持{first}，{trend_desc.get(confidence_trend, '')}"

    def _generate_conclusion(
        self,
        event: Dict[str, Any],
        all_rounds: List[ReactionRound],
        evolution: Dict[str, Any],
        influence_network: Dict[str, Any],
        opinion_leaders: List[Dict[str, Any]],
        converged: bool
    ) -> Dict[str, Any]:
        """生成推演结论"""

        # 统计各轮参与角色
        round_counts = {}
        for r in all_rounds:
            round_num = r.round_number
            round_counts[round_num] = round_counts.get(round_num, 0) + 1

        # 收集最终反应
        final_reactions = {}
        last_round = max(r.round_number for r in all_rounds) if all_rounds else 1
        for r in all_rounds:
            if r.round_number == last_round:
                final_reactions[r.role_id] = {
                    "role_name": r.role_name,
                    "reaction": r.reaction
                }

        # 识别关键张力
        key_tensions = self._identify_key_tensions(all_rounds, final_reactions)

        # 识别共识
        consensus = self._identify_consensus(all_rounds, final_reactions)

        # 整体趋势评估
        trend_assessment = self._assess_overall_trend(
            all_rounds,
            evolution,
            influence_network,
            converged
        )

        return {
            "total_reactions": len(all_rounds),
            "rounds_executed": last_round,
            "converged": converged,
            "final_reactions": final_reactions,
            "key_tensions": key_tensions,
            "consensus": consensus,
            "evolution_summary": evolution,
            "opinion_leaders": opinion_leaders,
            "influence_summary": {
                "total_nodes": influence_network.get("total_relations", 0),
                "network_density": self._calculate_network_density(influence_network)
            },
            "trend_assessment": trend_assessment
        }

    def _identify_key_tensions(
        self,
        all_rounds: List[ReactionRound],
        final_reactions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别关键张力"""

        tensions = []

        # 基于最终反应检测对立
        reactions_by_role = {}
        for role_id, data in final_reactions.items():
            reactions_by_role[role_id] = data["reaction"]

        # 检测情绪对立
        positive_roles = []
        negative_roles = []

        for role_id, reaction in reactions_by_role.items():
            emotion = reaction.get("emotion", "").lower()
            if any(w in emotion for w in ["积极", "支持", "乐观", "欢迎"]):
                positive_roles.append(role_id)
            elif any(w in emotion for w in ["担忧", "反对", "不满", "谨慎"]):
                negative_roles.append(role_id)

        if positive_roles and negative_roles:
            tensions.append({
                "type": "立场对立",
                "description": f"支持方({len(positive_roles)}个)与担忧方({len(negative_roles)}个)存在潜在张力",
                "severity": "中等" if len(positive_roles) + len(negative_roles) > 4 else "轻度",
                "involved_roles": positive_roles + negative_roles
            })

        return tensions

    def _identify_consensus(
        self,
        all_rounds: List[ReactionRound],
        final_reactions: Dict[str, Any]
    ) -> List[str]:
        """识别共识"""

        consensus = []

        # 检测共同关注点
        all_actions = []
        for data in final_reactions.values():
            action = data["reaction"].get("action", "")
            all_actions.append(action)

        # 简单检测共同主题
        common_themes = ["关注", "评估", "观察"]
        for theme in common_themes:
            count = sum(1 for a in all_actions if theme in a)
            if count >= len(all_actions) * 0.6:
                consensus.append(f"各方普遍{theme}事态发展")

        return consensus

    def _assess_overall_trend(
        self,
        all_rounds: List[ReactionRound],
        evolution: Dict[str, Any],
        influence_network: Dict[str, Any],
        converged: bool
    ) -> str:
        """评估整体趋势"""

        if converged:
            return "各方反应已趋于稳定，事态发展进入平稳期"

        # 分析演变趋势
        increasing_count = sum(
            1 for e in evolution.values()
            if e.get("confidence_trend") == "increasing"
        )
        decreasing_count = sum(
            1 for e in evolution.values()
            if e.get("confidence_trend") == "decreasing"
        )

        if increasing_count > decreasing_count:
            return "各方置信度整体上升，事态发展方向趋于明确"
        elif decreasing_count > increasing_count:
            return "各方置信度整体下降，事态发展存在不确定性"
        else:
            return "各方反应保持稳定，事态发展方向尚不明朗"

    def _calculate_network_density(self, influence_network: Dict[str, Any]) -> float:
        """计算网络密度"""
        nodes = influence_network.get("nodes", [])
        edges = influence_network.get("edges", [])

        if len(nodes) < 2:
            return 0.0

        max_edges = len(nodes) * (len(nodes) - 1)
        actual_edges = len(edges)

        return round(actual_edges / max_edges, 3) if max_edges > 0 else 0.0

    def _build_event_chain_context(
        self,
        previous_events: List[Dict[str, Any]],
        accumulated_reactions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """构建事件链上下文"""

        if not previous_events:
            return {}

        # 总结之前的事件和反应
        event_summary = []
        for idx, ev in enumerate(previous_events):
            event_summary.append(f"事件{idx+1}: {ev.get('title', 'N/A')}")

        reaction_summary = {}
        for role_id, reaction in accumulated_reactions.items():
            role = ROLES.get(role_id)
            name = role.name if role else role_id
            reaction_summary[name] = reaction

        return {
            "previous_events": event_summary,
            "accumulated_reactions": reaction_summary,
            "context": "后续事件需要考虑之前事件的发展和各方反应"
        }

    def _analyze_inter_event_relations(
        self,
        chain_results: List[Dict[str, Any]],
        event_influences: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析事件间的关系"""

        # 分析影响类型分布
        influence_distribution = {
            "amplify": 0,
            "attenuate": 0,
            "neutral": 0,
            "transform": 0
        }

        for influence in event_influences:
            dominant = influence.get("dominant_influence", "neutral")
            influence_distribution[dominant] = influence_distribution.get(dominant, 0) + 1

        # 识别级联效应
        cascading_effects = []
        for i, result in enumerate(chain_results):
            if i > 0:
                prev_result = chain_results[i - 1]
                # 检测置信度变化是否呈现级联
                cascading_effects.append({
                    "from_event": prev_result.get("event", {}).get("title", ""),
                    "to_event": result.get("event", {}).get("title", ""),
                    "effect": "态度传递"
                })

        return {
            "influence_distribution": influence_distribution,
            "cascading_effects": cascading_effects,
            "key_insights": [
                f"事件链共{len(chain_results)}个事件",
                f"检测到{len(cascading_effects)}个级联效应",
                f"主要影响类型: {max(influence_distribution, key=influence_distribution.get)}"
            ]
        }

    def _generate_event_chain_conclusion(
        self,
        events: List[Dict[str, Any]],
        chain_results: List[Dict[str, Any]],
        inter_event_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成事件链结论"""

        return {
            "event_sequence": [e.get("title", "Unknown") for e in events],
            "total_events": len(events),
            "overall_trend": inter_event_analysis.get("key_insights", ["分析中"])[0] if inter_event_analysis.get("key_insights") else "需要综合分析",
            "key_observations": inter_event_analysis.get("key_insights", []),
            "recommendation": self._generate_chain_recommendation(events, chain_results)
        }

    def _generate_chain_recommendation(
        self,
        events: List[Dict[str, Any]],
        chain_results: List[Dict[str, Any]]
    ) -> str:
        """生成事件链建议"""

        if not events:
            return "无事件可分析"

        importance_sum = sum(e.get("importance", 3) for e in events)
        avg_importance = importance_sum / len(events)

        if avg_importance >= 4:
            return "事件链整体重要性高，建议持续关注后续发展并做好应对准备"
        elif avg_importance >= 3:
            return "事件链重要性中等，建议定期跟踪各方反应变化"
        else:
            return "事件链重要性较低，可保持一般性关注"


# 全局服务实例
reaction_chain_service = ReactionChainService()
