# 多Agent协调器 - 管理多个专业Agent的协作
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.specialized import (
    BaseSpecializedAgent,
    AgentAnalysisResult,
    get_all_agents
)
from app.agents.specialized.base_specialized_agent import AgentMessage


class CoordinationMode(str, Enum):
    """协调模式"""
    PARALLEL = "parallel"  # 并行分析
    SEQUENTIAL = "sequential"  # 顺序分析
    ITERATIVE = "iterative"  # 迭代分析
    DEBATE = "debate"  # 辩论式分析


@dataclass
class CoordinationContext:
    """协调上下文"""
    event: Dict[str, Any]
    mode: CoordinationMode
    max_iterations: int = 3
    enable_communication: bool = True
    convergence_threshold: float = 0.85


@dataclass
class AgentCommunication:
    """Agent通信记录"""
    round_number: int
    sender_type: str
    receiver_type: Optional[str]  # None表示广播
    message_type: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class CoordinationResult:
    """协调结果"""
    event_id: str
    coordination_mode: str
    total_rounds: int

    # 各Agent分析结果
    agent_results: Dict[str, AgentAnalysisResult] = field(default_factory=dict)

    # 通信记录
    communications: List[AgentCommunication] = field(default_factory=list)

    # 综合报告
    synthesized_report: Dict[str, Any] = field(default_factory=dict)

    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "coordination_mode": self.coordination_mode,
            "total_rounds": self.total_rounds,
            "agent_results": {
                agent_type: result.to_dict()
                for agent_type, result in self.agent_results.items()
            },
            "communications": [
                {
                    "round": c.round_number,
                    "sender": c.sender_type,
                    "receiver": c.receiver_type,
                    "type": c.message_type,
                    "content": c.content,
                    "timestamp": c.timestamp
                }
                for c in self.communications
            ],
            "synthesized_report": self.synthesized_report,
            "timestamp": self.timestamp
        }


class AgentCoordinator:
    """
    多Agent协调器

    负责：
    1. 管理多个专业Agent
    2. 协调Agent间的通信
    3. 控制分析流程
    4. 综合分析结果
    """

    def __init__(self):
        # 初始化所有专业Agent
        self.agents: Dict[str, BaseSpecializedAgent] = get_all_agents()

        # 通信记录
        self.communications: List[AgentCommunication] = []

        # 当前协调上下文
        self.context: Optional[CoordinationContext] = None

        # LLM服务
        from app.services.llm_service import llm_service
        self.llm = llm_service

    def get_available_agents(self) -> List[Dict[str, str]]:
        """获取可用的Agent列表"""
        return [
            {
                "type": agent_type,
                "name": agent.agent_name,
                "description": agent.description
            }
            for agent_type, agent in self.agents.items()
        ]

    async def coordinate_analysis(
        self,
        event: Dict[str, Any],
        agent_types: List[str] = None,
        mode: CoordinationMode = CoordinationMode.PARALLEL,
        max_iterations: int = 2
    ) -> CoordinationResult:
        """
        执行多Agent协调分析

        Args:
            event: 事件数据
            agent_types: 要使用的Agent类型列表（None表示使用所有）
            mode: 协调模式
            max_iterations: 最大迭代次数

        Returns:
            协调结果
        """
        # 初始化上下文
        self.context = CoordinationContext(
            event=event,
            mode=mode,
            max_iterations=max_iterations
        )
        self.communications = []

        # 确定使用的Agent
        if agent_types:
            active_agents = {
                at: self.agents[at]
                for at in agent_types
                if at in self.agents
            }
        else:
            active_agents = self.agents

        if not active_agents:
            return CoordinationResult(
                event_id=event.get("id", "unknown"),
                coordination_mode=mode.value,
                total_rounds=0
            )

        # 根据模式执行分析
        if mode == CoordinationMode.PARALLEL:
            agent_results = await self._parallel_analysis(event, active_agents)
        elif mode == CoordinationMode.SEQUENTIAL:
            agent_results = await self._sequential_analysis(event, active_agents)
        elif mode == CoordinationMode.ITERATIVE:
            agent_results = await self._iterative_analysis(event, active_agents)
        else:
            agent_results = await self._parallel_analysis(event, active_agents)

        # 综合分析结果
        synthesized_report = await self._synthesize_results(event, agent_results)

        return CoordinationResult(
            event_id=event.get("id", "unknown"),
            coordination_mode=mode.value,
            total_rounds=max_iterations,
            agent_results=agent_results,
            communications=self.communications,
            synthesized_report=synthesized_report
        )

    async def _parallel_analysis(
        self,
        event: Dict[str, Any],
        agents: Dict[str, BaseSpecializedAgent]
    ) -> Dict[str, AgentAnalysisResult]:
        """并行分析模式 - 所有Agent同时独立分析"""
        tasks = [
            agent.analyze(event)
            for agent in agents.values()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        agent_results = {}
        for agent_type, result in zip(agents.keys(), results):
            if isinstance(result, AgentAnalysisResult):
                agent_results[agent_type] = result
            elif isinstance(result, Exception):
                print(f"Agent {agent_type} failed: {result}")

        return agent_results

    async def _sequential_analysis(
        self,
        event: Dict[str, Any],
        agents: Dict[str, BaseSpecializedAgent]
    ) -> Dict[str, AgentAnalysisResult]:
        """顺序分析模式 - Agent依次分析，后者参考前者结果"""
        agent_results = {}

        for agent_type, agent in agents.items():
            # 让当前Agent接收之前Agent的洞察
            for prev_type, prev_result in agent_results.items():
                agent.receive_insight(prev_type, prev_result)

            # 执行分析
            result = await agent.analyze(event)
            agent_results[agent_type] = result

            # 记录通信
            self.communications.append(AgentCommunication(
                round_number=1,
                sender_type=agent_type,
                receiver_type=None,
                message_type="insight_broadcast",
                content=f"{agent.agent_name}完成分析: {', '.join(result.key_findings[:2])}"
            ))

        return agent_results

    async def _iterative_analysis(
        self,
        event: Dict[str, Any],
        agents: Dict[str, BaseSpecializedAgent]
    ) -> Dict[str, AgentAnalysisResult]:
        """迭代分析模式 - 多轮分析，每轮参考其他Agent结果"""
        agent_results = {}

        for iteration in range(1, self.context.max_iterations + 1):
            round_results = {}

            for agent_type, agent in agents.items():
                # 接收其他Agent的洞察
                if iteration > 1:
                    for other_type, other_result in agent_results.items():
                        if other_type != agent_type:
                            agent.receive_insight(other_type, other_result)

                # 执行分析
                result = await agent.analyze(event)
                round_results[agent_type] = result

                # 发送洞察
                self.communications.append(AgentCommunication(
                    round_number=iteration,
                    sender_type=agent_type,
                    receiver_type=None,
                    message_type="insight_share",
                    content=f"第{iteration}轮分析: {result.key_findings[0] if result.key_findings else '无'}"
                ))

            # 更新结果
            agent_results = round_results

            # 检查收敛（简化版）
            if iteration >= 2:
                converged = self._check_convergence(agent_results)
                if converged:
                    break

        return agent_results

    def _check_convergence(self, agent_results: Dict[str, AgentAnalysisResult]) -> bool:
        """检查是否收敛"""
        # 简化版收敛检测 - 检查置信度是否稳定
        confidences = [r.confidence for r in agent_results.values()]
        if not confidences:
            return False

        avg_confidence = sum(confidences) / len(confidences)
        return avg_confidence >= self.context.convergence_threshold

    async def _synthesize_results(
        self,
        event: Dict[str, Any],
        agent_results: Dict[str, AgentAnalysisResult]
    ) -> Dict[str, Any]:
        """综合所有Agent的分析结果"""
        if not agent_results:
            return {}

        # 收集所有关键发现
        all_findings = []
        for result in agent_results.values():
            all_findings.extend(result.key_findings)

        # 收集所有建议
        all_recommendations = []
        for result in agent_results.values():
            all_recommendations.extend(result.recommendations)

        # 识别共识和分歧
        consensus, conflicts = self._identify_consensus_and_conflicts(agent_results)

        # 综合风险评估
        overall_risk = self._aggregate_risks(agent_results)

        # 生成时间线预测
        timeline_prediction = self._merge_timeline_predictions(agent_results)

        # 生成综合报告
        synthesized = {
            "event_summary": {
                "title": event.get("title", ""),
                "description": event.get("description", "")
            },
            "executive_summary": await self._generate_executive_summary(event, agent_results),
            "key_findings": list(set(all_findings))[:10],
            "consensus": consensus,
            "conflicts": conflicts,
            "risk_assessment": overall_risk,
            "timeline_prediction": timeline_prediction,
            "recommendations": list(set(all_recommendations))[:8],
            "agent_contributions": {
                agent_type: {
                    "name": result.agent_name,
                    "confidence": result.confidence,
                    "importance": result.importance_score,
                    "key_insight": result.key_findings[0] if result.key_findings else ""
                }
                for agent_type, result in agent_results.items()
            },
            "analysis_metadata": {
                "total_agents": len(agent_results),
                "analysis_mode": self.context.mode.value if self.context else "unknown",
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        return synthesized

    def _identify_consensus_and_conflicts(
        self,
        agent_results: Dict[str, AgentAnalysisResult]
    ) -> tuple:
        """识别共识和分歧"""
        consensus = []
        conflicts = []

        # 收集所有短期预测
        short_term_views = {}
        for agent_type, result in agent_results.items():
            short_term_views[agent_type] = result.short_term_forecast

        # 简化共识检测 - 寻找相似表述
        # 实际应该用NLP进行语义分析
        all_forecasts = list(short_term_views.values())
        if len(all_forecasts) > 1:
            # 检查是否有共同关键词
            common_keywords = self._find_common_keywords(all_forecasts)
            if common_keywords:
                consensus.append(f"多分析师对{', '.join(common_keywords)}持相似观点")

        # 检测潜在冲突
        risk_levels = [
            (agent_type, result.risk_assessment.get("overall_risk", "未知"))
            for agent_type, result in agent_results.items()
        ]

        high_risk = [r[0] for r in risk_levels if r[1] in ["高", "high"]]
        low_risk = [r[0] for r in risk_levels if r[1] in ["低", "low"]]

        if high_risk and low_risk:
            conflicts.append({
                "type": "风险评估分歧",
                "description": f"{'与'.join(high_risk)}认为风险较高，而{'与'.join(low_risk)}认为风险较低",
                "severity": "中等"
            })

        return consensus, conflicts

    def _find_common_keywords(self, texts: List[str]) -> List[str]:
        """查找共同关键词"""
        keywords = [
            "稳定", "增长", "下降", "上升", "影响",
            "持续", "变化", "关注", "风险", "机会"
        ]

        common = []
        for kw in keywords:
            if all(kw in text for text in texts):
                common.append(kw)

        return common

    def _aggregate_risks(
        self,
        agent_results: Dict[str, AgentAnalysisResult]
    ) -> Dict[str, Any]:
        """综合风险评估"""
        risk_assessments = [
            result.risk_assessment
            for result in agent_results.values()
            if result.risk_assessment
        ]

        if not risk_assessments:
            return {"overall_risk": "未知", "risk_level": 0.5}

        # 计算平均风险等级
        risk_levels = [
            ra.get("risk_level", 0.5)
            for ra in risk_assessments
        ]
        avg_risk = sum(risk_levels) / len(risk_levels)

        # 收集所有风险
        all_risks = []
        for ra in risk_assessments:
            all_risks.extend(ra.get("key_risks", []))

        return {
            "overall_risk": "高" if avg_risk > 0.7 else "中" if avg_risk > 0.4 else "低",
            "risk_level": round(avg_risk, 2),
            "key_risks": list(set(all_risks))[:5],
            "risk_by_domain": {
                agent_type: result.risk_assessment.get("overall_risk", "未知")
                for agent_type, result in agent_results.items()
            }
        }

    def _merge_timeline_predictions(
        self,
        agent_results: Dict[str, AgentAnalysisResult]
    ) -> Dict[str, Any]:
        """合并时间线预测"""
        return {
            "short_term": {
                "period": "1-7天",
                "predictions": [
                    {
                        "agent": result.agent_name,
                        "forecast": result.short_term_forecast,
                        "confidence": result.confidence
                    }
                    for result in agent_results.values()
                ]
            },
            "medium_term": {
                "period": "1-4周",
                "predictions": [
                    {
                        "agent": result.agent_name,
                        "forecast": result.medium_term_forecast,
                        "confidence": result.confidence
                    }
                    for result in agent_results.values()
                ]
            },
            "long_term": {
                "period": "1-6月",
                "predictions": [
                    {
                        "agent": result.agent_name,
                        "forecast": result.long_term_forecast,
                        "confidence": result.confidence * 0.8  # 长期预测置信度降低
                    }
                    for result in agent_results.values()
                ]
            }
        }

    async def _generate_executive_summary(
        self,
        event: Dict[str, Any],
        agent_results: Dict[str, AgentAnalysisResult]
    ) -> str:
        """生成执行摘要"""
        # 收集关键信息
        total_agents = len(agent_results)
        avg_confidence = sum(r.confidence for r in agent_results.values()) / total_agents if total_agents > 0 else 0

        # 收集最重要的发现
        top_findings = []
        sorted_results = sorted(
            agent_results.items(),
            key=lambda x: x[1].importance_score,
            reverse=True
        )

        for agent_type, result in sorted_results[:3]:
            if result.key_findings:
                top_findings.append(f"{result.agent_name}: {result.key_findings[0]}")

        summary = f"""本报告由{total_agents}个专业分析师协作完成，平均置信度{avg_confidence:.0%}。

核心发现：
{chr(10).join('- ' + f for f in top_findings)}

事件"{event.get('title', '该事件')}"需要从多个维度综合评估，各分析师观点详见分项报告。"""

        return summary


# 全局协调器实例
agent_coordinator = AgentCoordinator()
