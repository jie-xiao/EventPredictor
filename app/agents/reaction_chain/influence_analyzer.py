# 影响力分析器 - 分析各方反应之间的相互影响
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import math


@dataclass
class InfluenceRelation:
    """影响力关系"""
    source_role_id: str
    source_role_name: str
    target_role_id: str
    target_role_name: str
    influence_strength: float  # 0-1
    influence_type: str  # "support", "oppose", "neutral"
    reasoning: str
    round_number: int


@dataclass
class RoleInfluenceProfile:
    """角色影响力画像"""
    role_id: str
    role_name: str
    total_outgoing_influence: float = 0.0  # 该角色对其他人的总影响力
    total_incoming_influence: float = 0.0  # 其他人对该角色的总影响力
    influence_relations: List[InfluenceRelation] = field(default_factory=list)

    # 影响力指标
    opinion_leadership_score: float = 0.0  # 意见领袖指数
    influence_receptivity_score: float = 0.0  # 受影响程度指数

    def calculate_scores(self):
        """计算影响力指数"""
        # 意见领袖指数 = 输出影响力 / (输出影响力 + 输入影响力)
        total = self.total_outgoing_influence + self.total_incoming_influence
        if total > 0:
            self.opinion_leadership_score = self.total_outgoing_influence / total
            self.influence_receptivity_score = self.total_incoming_influence / total


class InfluenceAnalyzer:
    """
    影响力分析器

    分析各方反应之间的相互影响关系，包括：
    1. 识别哪些角色对其他角色有较大影响力
    2. 量化影响强度
    3. 分析影响类型（支持、反对、中性）
    4. 构建影响力网络
    """

    def __init__(self):
        self.influence_relations: List[InfluenceRelation] = []
        self.role_profiles: Dict[str, RoleInfluenceProfile] = {}

    def analyze_round_influence(
        self,
        round_number: int,
        current_reactions: Dict[str, Dict[str, Any]],
        previous_reactions: Dict[str, Dict[str, Any]],
        role_map: Dict[str, Any]
    ) -> List[InfluenceRelation]:
        """
        分析单轮反应中的影响力关系

        Args:
            round_number: 当前轮次
            current_reactions: 当前轮次各角色反应 {role_id: reaction}
            previous_reactions: 上一轮次各角色反应
            role_map: 角色映射 {role_id: AgentRole}

        Returns:
            影响力关系列表
        """
        round_relations = []

        if round_number == 1:
            # 第一轮没有前一轮的影响
            return round_relations

        for target_role_id, current_reaction in current_reactions.items():
            target_role = role_map.get(target_role_id)
            if not target_role:
                continue

            # 检查该角色是否受到其他角色的影响
            for source_role_id, prev_reaction in previous_reactions.items():
                if source_role_id == target_role_id:
                    continue

                source_role = role_map.get(source_role_id)
                if not source_role:
                    continue

                # 分析影响强度和类型
                influence_strength, influence_type, reasoning = self._calculate_influence(
                    target_role_id=target_role_id,
                    current_reaction=current_reaction,
                    source_role_id=source_role_id,
                    source_reaction=prev_reaction,
                    target_role=target_role,
                    source_role=source_role
                )

                if influence_strength > 0.1:  # 只记录有意义的影响
                    relation = InfluenceRelation(
                        source_role_id=source_role_id,
                        source_role_name=source_role.name,
                        target_role_id=target_role_id,
                        target_role_name=target_role.name,
                        influence_strength=influence_strength,
                        influence_type=influence_type,
                        reasoning=reasoning,
                        round_number=round_number
                    )
                    round_relations.append(relation)
                    self.influence_relations.append(relation)

        # 更新角色影响力画像
        self._update_role_profiles(round_relations)

        return round_relations

    def _calculate_influence(
        self,
        target_role_id: str,
        current_reaction: Dict[str, Any],
        source_role_id: str,
        source_reaction: Dict[str, Any],
        target_role: Any,
        source_role: Any
    ) -> Tuple[float, str, str]:
        """
        计算影响力强度和类型

        Returns:
            (influence_strength, influence_type, reasoning)
        """
        # 基于角色类别关系计算基础影响
        base_influence = self._get_category_influence(
            source_category=source_role.category.value if hasattr(source_role.category, 'value') else source_role.category,
            target_category=target_role.category.value if hasattr(target_role.category, 'value') else target_role.category
        )

        # 基于反应内容分析影响
        content_influence = self._analyze_content_influence(
            current_reaction=current_reaction,
            source_reaction=source_reaction
        )

        # 基于重要性加权
        importance_weight = current_reaction.get("confidence", 0.7)

        # 综合影响强度
        influence_strength = (base_influence * 0.4 + content_influence * 0.6) * importance_weight

        # 判断影响类型
        influence_type = self._determine_influence_type(
            current_reaction=current_reaction,
            source_reaction=source_reaction
        )

        # 生成推理说明
        reasoning = f"{source_role.name}的{source_reaction.get('action', '反应')}对{target_role.name}的决策产生了{influence_type}性影响"

        return influence_strength, influence_type, reasoning

    def _get_category_influence(self, source_category: str, target_category: str) -> float:
        """
        基于角色类别获取基础影响力

        不同类别的角色对其他类别有不同影响力的基础值
        """
        # 影响力矩阵
        influence_matrix = {
            # source -> target: influence
            ("government", "corporation"): 0.7,
            ("government", "public"): 0.6,
            ("government", "media"): 0.5,
            ("government", "investor"): 0.6,
            ("government", "government"): 0.4,

            ("corporation", "government"): 0.5,
            ("corporation", "public"): 0.4,
            ("corporation", "media"): 0.6,
            ("corporation", "investor"): 0.7,
            ("corporation", "corporation"): 0.5,

            ("public", "government"): 0.4,
            ("public", "corporation"): 0.3,
            ("public", "media"): 0.5,
            ("public", "investor"): 0.2,
            ("public", "public"): 0.6,

            ("media", "government"): 0.5,
            ("media", "corporation"): 0.6,
            ("media", "public"): 0.8,
            ("media", "investor"): 0.5,
            ("media", "media"): 0.3,

            ("investor", "government"): 0.3,
            ("investor", "corporation"): 0.6,
            ("investor", "public"): 0.2,
            ("investor", "media"): 0.4,
            ("investor", "investor"): 0.7,
        }

        return influence_matrix.get((source_category, target_category), 0.3)

    def _analyze_content_influence(
        self,
        current_reaction: Dict[str, Any],
        source_reaction: Dict[str, Any]
    ) -> float:
        """
        基于反应内容分析影响力
        """
        # 检查情绪变化
        current_emotion = current_reaction.get("emotion", "")
        source_emotion = source_reaction.get("emotion", "")

        emotion_similarity = self._text_similarity(current_emotion, source_emotion)

        # 检查行动相关性
        current_action = current_reaction.get("action", "")
        source_action = source_reaction.get("action", "")

        action_relevance = self._text_similarity(current_action, source_action)

        # 检查立场变化
        stance_change = current_reaction.get("stance_change", "")
        has_stance_change = 1.0 if stance_change else 0.0

        # 综合计算
        influence = (emotion_similarity * 0.3 + action_relevance * 0.4 + has_stance_change * 0.3)

        return min(influence, 1.0)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        简单的文本相似度计算
        """
        if not text1 or not text2:
            return 0.0

        # 分词
        words1 = set(text1)
        words2 = set(text2)

        if not words1 or not words2:
            return 0.0

        # Jaccard相似度
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _determine_influence_type(
        self,
        current_reaction: Dict[str, Any],
        source_reaction: Dict[str, Any]
    ) -> str:
        """
        判断影响类型
        """
        # 检查情绪一致性
        current_emotion = current_reaction.get("emotion", "").lower()
        source_emotion = source_reaction.get("emotion", "").lower()

        # 积极情绪词汇
        positive_words = ["支持", "赞同", "欢迎", "积极", "乐观", "高兴", "满意"]
        # 消极情绪词汇
        negative_words = ["反对", "不满", "担忧", "谨慎", "悲观", "担忧", "关注"]

        current_positive = any(w in current_emotion for w in positive_words)
        current_negative = any(w in current_emotion for w in negative_words)
        source_positive = any(w in source_emotion for w in positive_words)
        source_negative = any(w in source_emotion for w in negative_words)

        if (current_positive and source_positive) or (current_negative and source_negative):
            return "support"
        elif (current_positive and source_negative) or (current_negative and source_positive):
            return "oppose"
        else:
            return "neutral"

    def _update_role_profiles(self, relations: List[InfluenceRelation]):
        """更新角色影响力画像"""
        for relation in relations:
            # 更新目标角色的输入影响力
            if relation.target_role_id not in self.role_profiles:
                self.role_profiles[relation.target_role_id] = RoleInfluenceProfile(
                    role_id=relation.target_role_id,
                    role_name=relation.target_role_name
                )
            self.role_profiles[relation.target_role_id].total_incoming_influence += relation.influence_strength
            self.role_profiles[relation.target_role_id].influence_relations.append(relation)

            # 更新源角色的输出影响力
            if relation.source_role_id not in self.role_profiles:
                self.role_profiles[relation.source_role_id] = RoleInfluenceProfile(
                    role_id=relation.source_role_id,
                    role_name=relation.source_role_name
                )
            self.role_profiles[relation.source_role_id].total_outgoing_influence += relation.influence_strength

        # 重新计算所有角色的分数
        for profile in self.role_profiles.values():
            profile.calculate_scores()

    def get_influence_network(self) -> Dict[str, Any]:
        """
        获取影响力网络数据
        """
        nodes = []
        edges = []

        # 构建节点
        for role_id, profile in self.role_profiles.items():
            nodes.append({
                "id": role_id,
                "name": profile.role_name,
                "outgoing_influence": round(profile.total_outgoing_influence, 3),
                "incoming_influence": round(profile.total_incoming_influence, 3),
                "opinion_leadership": round(profile.opinion_leadership_score, 3),
                "receptivity": round(profile.influence_receptivity_score, 3)
            })

        # 构建边
        seen_edges = {}  # 聚合相同源和目标的边
        for relation in self.influence_relations:
            edge_key = (relation.source_role_id, relation.target_role_id)
            if edge_key in seen_edges:
                seen_edges[edge_key]["weight"] += relation.influence_strength
                seen_edges[edge_key]["count"] += 1
            else:
                seen_edges[edge_key] = {
                    "source": relation.source_role_id,
                    "target": relation.target_role_id,
                    "weight": relation.influence_strength,
                    "type": relation.influence_type,
                    "count": 1
                }

        for edge in seen_edges.values():
            edge["weight"] = round(edge["weight"] / edge["count"], 3)  # 平均权重
            edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "total_relations": len(self.influence_relations)
        }

    def get_opinion_leaders(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        获取意见领袖列表
        """
        sorted_profiles = sorted(
            self.role_profiles.values(),
            key=lambda p: p.opinion_leadership_score,
            reverse=True
        )

        return [
            {
                "role_id": p.role_id,
                "role_name": p.role_name,
                "leadership_score": round(p.opinion_leadership_score, 3),
                "outgoing_influence": round(p.total_outgoing_influence, 3)
            }
            for p in sorted_profiles[:top_n]
        ]

    def get_most_influenced(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        获取最易受影响的角色列表
        """
        sorted_profiles = sorted(
            self.role_profiles.values(),
            key=lambda p: p.influence_receptivity_score,
            reverse=True
        )

        return [
            {
                "role_id": p.role_id,
                "role_name": p.role_name,
                "receptivity_score": round(p.influence_receptivity_score, 3),
                "incoming_influence": round(p.total_incoming_influence, 3)
            }
            for p in sorted_profiles[:top_n]
        ]

    def reset(self):
        """重置分析器状态"""
        self.influence_relations = []
        self.role_profiles = {}
