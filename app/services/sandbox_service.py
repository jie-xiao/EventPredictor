# 增强沙盘推演服务 - P1阶段核心功能
"""
沙盘推演服务 - 实现多步推演、分支场景、决策点分析

核心功能：
1. 多步推演 - 从当前事件推演N个时间步
2. 分支场景 - 每步产生多个可能的分支
3. 决策点 - 识别关键决策点及其影响
4. 路径追踪 - 记录完整演化路径
"""
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field

from app.services.llm_service import llm_service


class DecisionType(str, Enum):
    """决策类型"""
    POLICY = "policy"          # 政策决策
    MILITARY = "military"      # 军事决策
    ECONOMIC = "economic"      # 经济决策
    DIPLOMATIC = "diplomatic"  # 外交决策
    SOCIAL = "social"          # 社会决策


class BranchType(str, Enum):
    """分支类型"""
    OPTIMISTIC = "optimistic"   # 乐观
    BASELINE = "baseline"       # 基准
    PESSIMISTIC = "pessimistic" # 悲观
    WILDCARD = "wildcard"       # 黑天鹅


@dataclass
class DecisionPoint:
    """决策点"""
    id: str
    time_step: int
    description: str
    decision_type: DecisionType
    options: List[Dict[str, Any]]  # 可选决策
    impact_weights: Dict[str, float]  # 对各分支的影响权重
    confidence: float = 0.7


@dataclass
class EvolutionBranch:
    """演化分支"""
    id: str
    branch_type: BranchType
    name: str
    description: str
    probability: float
    time_step: int
    state: Dict[str, Any]  # 当前状态
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    decision_points: List[DecisionPoint] = field(default_factory=list)


@dataclass
class EvolutionStep:
    """演化步骤"""
    step_number: int
    time_label: str  # 如 "第1天", "第1周"
    description: str
    key_events: List[str]
    branch_states: Dict[str, Dict[str, Any]]  # branch_id -> state
    active_decisions: List[DecisionPoint]


class SandboxEvolutionRequest(BaseModel):
    """沙盘推演请求"""
    event_id: str
    event_title: str
    event_description: str
    event_category: str = "other"
    importance: int = 3
    steps: int = Field(default=5, ge=1, le=10)
    branches_per_step: int = Field(default=3, ge=2, le=5)
    include_decisions: bool = True
    time_unit: str = "day"  # day, week, month


class DecisionImpact(BaseModel):
    """决策影响分析"""
    decision_id: str
    decision_description: str
    affected_branches: List[str]
    probability_changes: Dict[str, float]
    outcome_changes: Dict[str, Any]
    confidence: float


class SandboxEvolutionResponse(BaseModel):
    """沙盘推演响应"""
    evolution_id: str
    event_id: str
    initial_state: Dict[str, Any]
    steps: List[Dict[str, Any]]
    branches: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    final_projections: Dict[str, Any]
    recommended_path: Dict[str, Any]
    confidence: float
    generated_at: str


class SandboxService:
    """增强沙盘推演服务"""

    def __init__(self):
        self.llm = llm_service

    async def evolve(
        self,
        request: SandboxEvolutionRequest
    ) -> SandboxEvolutionResponse:
        """
        执行沙盘推演

        Args:
            request: 推演请求

        Returns:
            完整的推演结果
        """
        evolution_id = f"evo-{uuid.uuid4().hex[:8]}"

        # 初始化分支
        initial_branches = await self._initialize_branches(request)

        # 执行多步推演
        steps = []
        current_branches = initial_branches

        for step_num in range(1, request.steps + 1):
            time_label = self._get_time_label(step_num, request.time_unit)

            # 推演当前步骤
            step_result = await self._evolve_step(
                step_num=step_num,
                time_label=time_label,
                branches=current_branches,
                request=request
            )
            steps.append(step_result)

            # 如果不是最后一步，生成下一轮分支
            if step_num < request.steps:
                current_branches = await self._generate_next_branches(
                    step_result,
                    request
                )

        # 识别关键决策点
        decision_points = await self._identify_decision_points(
            request,
            steps,
            initial_branches
        )

        # 生成最终预测
        final_projections = self._generate_final_projections(steps)

        # 计算推荐路径
        recommended_path = self._calculate_recommended_path(
            steps,
            initial_branches,
            decision_points
        )

        # 计算整体置信度
        confidence = self._calculate_overall_confidence(steps)

        return SandboxEvolutionResponse(
            evolution_id=evolution_id,
            event_id=request.event_id,
            initial_state={
                "title": request.event_title,
                "description": request.event_description,
                "category": request.event_category,
                "importance": request.importance
            },
            steps=steps,
            branches=[self._branch_to_dict(b) for b in initial_branches],
            decision_points=[self._decision_to_dict(d) for d in decision_points],
            final_projections=final_projections,
            recommended_path=recommended_path,
            confidence=confidence,
            generated_at=datetime.utcnow().isoformat()
        )

    async def _initialize_branches(
        self,
        request: SandboxEvolutionRequest
    ) -> List[EvolutionBranch]:
        """初始化推演分支"""

        prompt = f"""针对以下事件，请生成{request.branches_per_step}个可能的演化分支：

事件：{request.event_title}
描述：{request.event_description}
类别：{request.event_category}
严重程度：{request.importance}/5

请生成以下类型的分支：
1. 乐观分支 - 事件向积极方向发展
2. 基准分支 - 最可能的发展路径
3. 悲观分支 - 事态可能恶化的情况
{"4. 黑天鹅分支 - 低概率高影响的事件" if request.branches_per_step >= 4 else ""}

对于每个分支，请提供：
- 分支名称
- 分支描述
- 发生概率 (0-1)
- 初始状态描述

请以JSON格式输出，格式如下：
{{
  "branches": [
    {{
      "branch_type": "baseline",
      "name": "分支名称",
      "description": "分支描述",
      "probability": 0.5,
      "initial_state": {{"key": "value"}}
    }}
  ]
}}"""

        try:
            response = await self.llm.generate(prompt)

            # 解析响应
            import json
            import re

            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")

            branches = []
            for i, branch_data in enumerate(data.get("branches", [])):
                branch_type_str = branch_data.get("branch_type", "baseline")
                try:
                    branch_type = BranchType(branch_type_str)
                except ValueError:
                    branch_type = BranchType.BASELINE

                branch = EvolutionBranch(
                    id=f"branch-{i}",
                    branch_type=branch_type,
                    name=branch_data.get("name", f"分支{i+1}"),
                    description=branch_data.get("description", ""),
                    probability=branch_data.get("probability", 0.33),
                    time_step=0,
                    state=branch_data.get("initial_state", {})
                )
                branches.append(branch)

            # 如果解析失败，使用默认分支
            if not branches:
                branches = self._get_default_branches(request)

            return branches

        except Exception as e:
            print(f"Branch initialization failed: {e}")
            return self._get_default_branches(request)

    def _get_default_branches(
        self,
        request: SandboxEvolutionRequest
    ) -> List[EvolutionBranch]:
        """获取默认分支"""
        return [
            EvolutionBranch(
                id="branch-0",
                branch_type=BranchType.OPTIMISTIC,
                name="乐观分支",
                description="事件得到妥善处理，影响逐步减弱",
                probability=0.25,
                time_step=0,
                state={"trend": "positive", "tension": "decreasing"}
            ),
            EvolutionBranch(
                id="branch-1",
                branch_type=BranchType.BASELINE,
                name="基准分支",
                description="事件按当前趋势发展",
                probability=0.50,
                time_step=0,
                state={"trend": "neutral", "tension": "stable"}
            ),
            EvolutionBranch(
                id="branch-2",
                branch_type=BranchType.PESSIMISTIC,
                name="悲观分支",
                description="事态可能升级",
                probability=0.25,
                time_step=0,
                state={"trend": "negative", "tension": "increasing"}
            )
        ]

    async def _evolve_step(
        self,
        step_num: int,
        time_label: str,
        branches: List[EvolutionBranch],
        request: SandboxEvolutionRequest
    ) -> Dict[str, Any]:
        """推演单个步骤"""

        # 构建当前状态描述
        branch_states = "\n".join([
            f"- {b.name}: {b.description} (概率: {b.probability:.0%})"
            for b in branches
        ])

        prompt = f"""请推演以下事件在第{step_num}步（{time_label}）的发展：

事件：{request.event_title}

当前各分支状态：
{branch_states}

请为每个分支提供：
1. 该步可能发生的关键事件（2-3个）
2. 状态变化描述
3. 概率调整（如有）

请以JSON格式输出：
{{
  "step_number": {step_num},
  "time_label": "{time_label}",
  "description": "该步整体描述",
  "branch_updates": [
    {{
      "branch_id": "branch-0",
      "events": ["事件1", "事件2"],
      "state_change": "状态变化描述",
      "probability_adjustment": 0.05
    }}
  ],
  "key_events": ["整体关键事件"]
}}"""

        try:
            response = await self.llm.generate(prompt)

            # 解析响应
            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")

            # 更新分支状态
            branch_updates = {}
            for update in data.get("branch_updates", []):
                branch_id = update.get("branch_id")
                if branch_id:
                    branch_updates[branch_id] = {
                        "events": update.get("events", []),
                        "state_change": update.get("state_change", ""),
                        "probability_adjustment": update.get("probability_adjustment", 0)
                    }

            return {
                "step_number": step_num,
                "time_label": time_label,
                "description": data.get("description", f"第{step_num}步推演"),
                "branch_states": branch_updates,
                "key_events": data.get("key_events", [])
            }

        except Exception as e:
            print(f"Step evolution failed: {e}")
            return {
                "step_number": step_num,
                "time_label": time_label,
                "description": f"第{step_num}步推演",
                "branch_states": {},
                "key_events": [f"事件继续发展"]
            }

    async def _generate_next_branches(
        self,
        step_result: Dict[str, Any],
        request: SandboxEvolutionRequest
    ) -> List[EvolutionBranch]:
        """生成下一轮分支（简化版：保持当前分支）"""
        # 简化实现：保持3个主分支，更新概率
        return [
            EvolutionBranch(
                id=f"branch-{i}",
                branch_type=[BranchType.OPTIMISTIC, BranchType.BASELINE, BranchType.PESSIMISTIC][i],
                name=["乐观分支", "基准分支", "悲观分支"][i],
                description=step_result.get("branch_states", {}).get(f"branch-{i}", {}).get("state_change", "继续发展"),
                probability=[0.25, 0.50, 0.25][i],
                time_step=step_result["step_number"],
                state={}
            )
            for i in range(min(3, request.branches_per_step))
        ]

    async def _identify_decision_points(
        self,
        request: SandboxEvolutionRequest,
        steps: List[Dict[str, Any]],
        branches: List[EvolutionBranch]
    ) -> List[DecisionPoint]:
        """识别关键决策点"""

        if not request.include_decisions:
            return []

        # 构建推演摘要
        steps_summary = "\n".join([
            f"第{s['step_number']}步({s['time_label']}): {s.get('description', '')}"
            for s in steps[:3]  # 只取前3步
        ])

        prompt = f"""请分析以下事件推演中的关键决策点：

事件：{request.event_title}

推演过程：
{steps_summary}

请识别3-5个关键决策点，每个决策点包含：
1. 时间步骤
2. 决策描述
3. 决策类型（policy/military/economic/diplomatic/social）
4. 可选方案（2-3个）
5. 对各分支的影响

请以JSON格式输出：
{{
  "decision_points": [
    {{
      "time_step": 1,
      "description": "决策描述",
      "decision_type": "policy",
      "options": [
        {{"name": "方案A", "description": "方案描述", "branch_impacts": {{"乐观": 0.1, "基准": 0.05, "悲观": -0.1}}}}
      ],
      "confidence": 0.8
    }}
  ]
}}"""

        try:
            response = await self.llm.generate(prompt)

            import json
            import re

            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return []

            decision_points = []
            for i, dp_data in enumerate(data.get("decision_points", [])[:5]):
                try:
                    decision_type = DecisionType(dp_data.get("decision_type", "policy"))
                except ValueError:
                    decision_type = DecisionType.POLICY

                dp = DecisionPoint(
                    id=f"decision-{i}",
                    time_step=dp_data.get("time_step", 1),
                    description=dp_data.get("description", ""),
                    decision_type=decision_type,
                    options=dp_data.get("options", []),
                    impact_weights=dp_data.get("branch_impacts", {}),
                    confidence=dp_data.get("confidence", 0.7)
                )
                decision_points.append(dp)

            return decision_points

        except Exception as e:
            print(f"Decision point identification failed: {e}")
            return []

    def _generate_final_projections(
        self,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成最终预测"""

        if not steps:
            return {
                "most_likely_outcome": "不确定",
                "probability_distribution": {},
                "key_factors": []
            }

        # 分析最后一步的状态
        last_step = steps[-1]
        branch_states = last_step.get("branch_states", {})

        # 计算概率分布
        total_prob = 0
        outcomes = {}

        for branch_id, state in branch_states.items():
            prob_change = state.get("probability_adjustment", 0)
            outcomes[branch_id] = {
                "probability_change": prob_change,
                "key_events": state.get("events", [])
            }

        return {
            "most_likely_outcome": "基准情景",
            "probability_distribution": {
                "optimistic": 0.25,
                "baseline": 0.50,
                "pessimistic": 0.25
            },
            "key_factors": ["政策响应", "外部因素", "市场反应"],
            "steps_analyzed": len(steps)
        }

    def _calculate_recommended_path(
        self,
        steps: List[Dict[str, Any]],
        branches: List[EvolutionBranch],
        decision_points: List[DecisionPoint]
    ) -> Dict[str, Any]:
        """计算推荐路径"""

        # 简化实现：选择概率最高的分支路径
        best_branch = max(branches, key=lambda b: b.probability) if branches else None

        path_steps = []
        for step in steps:
            path_steps.append({
                "step": step["step_number"],
                "time": step["time_label"],
                "action": step.get("key_events", ["继续观察"])[0] if step.get("key_events") else "继续观察"
            })

        return {
            "recommended_branch": best_branch.name if best_branch else "基准分支",
            "reason": f"概率最高({best_branch.probability:.0%})的发展路径" if best_branch else "默认推荐",
            "path": path_steps,
            "key_decisions": [
                {
                    "step": dp.time_step,
                    "decision": dp.description,
                    "recommended_option": dp.options[0] if dp.options else None
                }
                for dp in decision_points[:3]
            ]
        }

    def _calculate_overall_confidence(
        self,
        steps: List[Dict[str, Any]]
    ) -> float:
        """计算整体置信度"""

        if not steps:
            return 0.5

        # 基础置信度
        base_confidence = 0.7

        # 每步推演降低置信度
        step_penalty = len(steps) * 0.03

        return max(0.3, min(0.95, base_confidence - step_penalty))

    def _get_time_label(self, step: int, unit: str) -> str:
        """获取时间标签"""
        labels = {
            "day": ["当天", "第2天", "第3天", "第4天", "第5天", "第6天", "第7天", "第2周", "第3周", "第4周"],
            "week": ["第1周", "第2周", "第3周", "第4周", "第5周", "第6周", "第7周", "第2月", "第3月", "第4月"],
            "month": ["第1月", "第2月", "第3月", "第4月", "第5月", "第6月", "第7月", "第8月", "第9月", "第10月"]
        }

        unit_labels = labels.get(unit, labels["day"])
        if step <= len(unit_labels):
            return unit_labels[step - 1]
        return f"第{step}{unit}"

    def _branch_to_dict(self, branch: EvolutionBranch) -> Dict[str, Any]:
        """将分支转换为字典"""
        return {
            "id": branch.id,
            "branch_type": branch.branch_type.value,
            "name": branch.name,
            "description": branch.description,
            "probability": branch.probability,
            "time_step": branch.time_step,
            "state": branch.state
        }

    def _decision_to_dict(self, decision: DecisionPoint) -> Dict[str, Any]:
        """将决策点转换为字典"""
        return {
            "id": decision.id,
            "time_step": decision.time_step,
            "description": decision.description,
            "decision_type": decision.decision_type.value,
            "options": decision.options,
            "impact_weights": decision.impact_weights,
            "confidence": decision.confidence
        }

    async def analyze_decision_impact(
        self,
        evolution_id: str,
        decision_id: str,
        chosen_option: str
    ) -> DecisionImpact:
        """
        分析特定决策的影响

        Args:
            evolution_id: 推演ID
            decision_id: 决策点ID
            chosen_option: 选择的方案

        Returns:
            决策影响分析结果
        """
        # 简化实现
        return DecisionImpact(
            decision_id=decision_id,
            decision_description="决策描述",
            affected_branches=["branch-0", "branch-1"],
            probability_changes={"optimistic": 0.1, "baseline": 0.0, "pessimistic": -0.1},
            outcome_changes={"trend": "positive"},
            confidence=0.7
        )


# 全局服务实例
sandbox_service = SandboxService()
