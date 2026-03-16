# 时间线构建器 - 构建推演时间线
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class TimelineNode:
    """时间线节点"""
    id: str
    time: str  # 时间标识 (T+0, T+1, T+1.1 等)
    node_type: str  # initial_event, reaction, state_change, influence, convergence
    title: str
    description: str
    involved_roles: List[str]
    details: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "time": self.time,
            "node_type": self.node_type,
            "title": self.title,
            "description": self.description,
            "involved_roles": self.involved_roles,
            "details": self.details,
            "parent_id": self.parent_id,
            "children": self.children,
            "timestamp": self.timestamp
        }


@dataclass
class StateSnapshot:
    """状态快照"""
    time: str
    role_states: Dict[str, Dict[str, Any]]  # {role_id: state}
    key_metrics: Dict[str, float]  # 关键指标
    notable_changes: List[str]  # 显著变化


class TimelineBuilder:
    """
    时间线构建器

    构建和管理推演时间线，包括：
    1. 记录事件节点
    2. 追踪状态变化
    3. 构建时间线树结构
    4. 生成时间线摘要
    """

    def __init__(self):
        self.nodes: Dict[str, TimelineNode] = {}
        self.root_id: Optional[str] = None
        self.state_snapshots: List[StateSnapshot] = []
        self.current_time = 0

    def add_initial_event(self, event: Dict[str, Any]) -> str:
        """
        添加初始事件节点
        """
        node = TimelineNode(
            id=str(uuid.uuid4())[:8],
            time="T+0",
            node_type="initial_event",
            title=event.get("title", "初始事件"),
            description=event.get("description", ""),
            involved_roles=[],
            details=event
        )

        self.nodes[node.id] = node
        self.root_id = node.id
        self.current_time = 0

        return node.id

    def add_reaction_round(
        self,
        round_number: int,
        reactions: Dict[str, Dict[str, Any]],
        parent_id: Optional[str] = None
    ) -> List[str]:
        """
        添加一轮反应节点
        """
        node_ids = []
        self.current_time = round_number

        # 如果没有指定父节点，使用最后一个节点
        if parent_id is None and self.nodes:
            parent_id = list(self.nodes.keys())[-1]

        for role_id, reaction in reactions.items():
            role_name = reaction.get("role_name", role_id)

            node = TimelineNode(
                id=str(uuid.uuid4())[:8],
                time=f"T+{round_number}",
                node_type="reaction",
                title=f"{role_name}的反应",
                description=f"{role_name}在第{round_number}轮的反应：{reaction.get('action', '采取行动')}",
                involved_roles=[role_id],
                details=reaction,
                parent_id=parent_id
            )

            self.nodes[node.id] = node
            node_ids.append(node.id)

            # 更新父节点的children
            if parent_id and parent_id in self.nodes:
                self.nodes[parent_id].children.append(node.id)

        return node_ids

    def add_state_change(
        self,
        time: str,
        role_id: str,
        change_description: str,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any]
    ) -> str:
        """
        添加状态变化节点
        """
        node = TimelineNode(
            id=str(uuid.uuid4())[:8],
            time=time,
            node_type="state_change",
            title=f"状态变化",
            description=change_description,
            involved_roles=[role_id],
            details={
                "old_state": old_state,
                "new_state": new_state,
                "change_type": self._classify_change(old_state, new_state)
            }
        )

        self.nodes[node.id] = node
        return node.id

    def add_influence_event(
        self,
        time: str,
        source_role: str,
        target_role: str,
        influence_type: str,
        influence_strength: float,
        reasoning: str
    ) -> str:
        """
        添加影响事件节点
        """
        node = TimelineNode(
            id=str(uuid.uuid4())[:8],
            time=time,
            node_type="influence",
            title=f"影响力传递",
            description=f"{source_role}对{target_role}产生{influence_type}性影响",
            involved_roles=[source_role, target_role],
            details={
                "source": source_role,
                "target": target_role,
                "type": influence_type,
                "strength": influence_strength,
                "reasoning": reasoning
            }
        )

        self.nodes[node.id] = node
        return node.id

    def add_convergence_event(
        self,
        time: str,
        convergence_score: float,
        converged_roles: List[str]
    ) -> str:
        """
        添加收敛事件节点
        """
        node = TimelineNode(
            id=str(uuid.uuid4())[:8],
            time=time,
            node_type="convergence",
            title=f"反应收敛",
            description=f"各方法反应趋于稳定，收敛分数：{convergence_score:.2f}",
            involved_roles=converged_roles,
            details={
                "convergence_score": convergence_score,
                "converged_roles": converged_roles
            }
        )

        self.nodes[node.id] = node
        return node.id

    def capture_state_snapshot(
        self,
        time: str,
        role_states: Dict[str, Dict[str, Any]]
    ) -> StateSnapshot:
        """
        捕获状态快照
        """
        # 计算关键指标
        key_metrics = self._calculate_metrics(role_states)

        # 识别显著变化
        notable_changes = []
        if self.state_snapshots:
            previous = self.state_snapshots[-1]
            notable_changes = self._detect_changes(
                previous.role_states,
                role_states
            )

        snapshot = StateSnapshot(
            time=time,
            role_states=role_states,
            key_metrics=key_metrics,
            notable_changes=notable_changes
        )

        self.state_snapshots.append(snapshot)
        return snapshot

    def _calculate_metrics(self, role_states: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """计算关键指标"""
        if not role_states:
            return {}

        # 平均置信度
        confidences = [
            s.get("confidence", 0.5)
            for s in role_states.values()
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # 情绪分布
        emotions = [s.get("emotion", "neutral") for s in role_states.values()]
        positive_count = sum(1 for e in emotions if any(
            w in e.lower() for w in ["积极", "支持", "乐观", "欢迎"]
        ))
        positive_ratio = positive_count / len(emotions) if emotions else 0.5

        # 行动一致性
        actions = [s.get("action", "") for s in role_states.values()]
        unique_actions = len(set(actions))
        action_diversity = unique_actions / len(actions) if actions else 0.5

        return {
            "average_confidence": round(avg_confidence, 3),
            "positive_emotion_ratio": round(positive_ratio, 3),
            "action_diversity": round(action_diversity, 3),
            "total_roles": len(role_states)
        }

    def _detect_changes(
        self,
        previous_states: Dict[str, Dict[str, Any]],
        current_states: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """检测显著变化"""
        changes = []

        for role_id in current_states:
            if role_id not in previous_states:
                changes.append(f"{role_id}首次参与")
                continue

            prev = previous_states[role_id]
            curr = current_states[role_id]

            # 情绪变化
            if prev.get("emotion") != curr.get("emotion"):
                changes.append(f"{role_id}情绪从'{prev.get('emotion')}'变为'{curr.get('emotion')}'")

            # 立场变化
            if curr.get("stance_change"):
                changes.append(f"{role_id}调整了立场：{curr.get('stance_change')}")

            # 置信度变化
            conf_diff = curr.get("confidence", 0) - prev.get("confidence", 0)
            if abs(conf_diff) >= 0.2:
                direction = "提高" if conf_diff > 0 else "降低"
                changes.append(f"{role_id}置信度{direction}了{abs(conf_diff):.1%}")

        return changes

    def _classify_change(
        self,
        old_state: Dict[str, Any],
        new_state: Dict[str, Any]
    ) -> str:
        """分类状态变化类型"""
        old_conf = old_state.get("confidence", 0.5)
        new_conf = new_state.get("confidence", 0.5)

        if new_conf > old_conf + 0.1:
            return "confidence_increase"
        elif new_conf < old_conf - 0.1:
            return "confidence_decrease"

        if old_state.get("emotion") != new_state.get("emotion"):
            return "emotion_shift"

        if new_state.get("stance_change"):
            return "stance_adjustment"

        return "minor_update"

    def get_timeline(self) -> List[Dict[str, Any]]:
        """获取完整时间线"""
        # 按时间排序
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: (n.time, n.node_type)
        )

        return [node.to_dict() for node in sorted_nodes]

    def get_timeline_tree(self) -> Dict[str, Any]:
        """获取时间线树结构"""
        if not self.root_id:
            return {}

        def build_tree(node_id: str) -> Dict[str, Any]:
            node = self.nodes.get(node_id)
            if not node:
                return {}

            tree_node = node.to_dict()
            tree_node["children"] = [
                build_tree(child_id)
                for child_id in node.children
                if child_id in self.nodes
            ]
            return tree_node

        return build_tree(self.root_id)

    def get_state_evolution(self) -> List[Dict[str, Any]]:
        """获取状态演变历史"""
        return [
            {
                "time": snapshot.time,
                "metrics": snapshot.key_metrics,
                "changes": snapshot.notable_changes
            }
            for snapshot in self.state_snapshots
        ]

    def get_summary(self) -> Dict[str, Any]:
        """获取时间线摘要"""
        return {
            "total_nodes": len(self.nodes),
            "total_snapshots": len(self.state_snapshots),
            "time_range": f"T+0 ~ T+{self.current_time}",
            "node_types": self._count_node_types(),
            "key_milestones": self._extract_milestones()
        }

    def _count_node_types(self) -> Dict[str, int]:
        """统计节点类型"""
        counts = {}
        for node in self.nodes.values():
            counts[node.node_type] = counts.get(node.node_type, 0) + 1
        return counts

    def _extract_milestones(self) -> List[Dict[str, Any]]:
        """提取关键里程碑"""
        milestones = []

        for node in self.nodes.values():
            if node.node_type in ["convergence", "state_change"]:
                milestones.append({
                    "time": node.time,
                    "type": node.node_type,
                    "title": node.title,
                    "description": node.description
                })

        return milestones

    def reset(self):
        """重置构建器状态"""
        self.nodes = {}
        self.root_id = None
        self.state_snapshots = []
        self.current_time = 0
