# 收敛检测器 - 检测反应链是否收敛
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import math


@dataclass
class ConvergenceResult:
    """收敛检测结果"""
    is_converged: bool
    convergence_score: float  # 0-1，越高表示越接近收敛
    role_convergence: Dict[str, float]  # 每个角色的收敛分数
    stable_aspects: List[str]  # 已稳定的方面
    changing_aspects: List[str]  # 仍在变化的方面
    recommendation: str  # 建议（继续迭代或停止）


class ConvergenceDetector:
    """
    收敛检测器

    检测反应链是否达到收敛状态，包括：
    1. 比较相邻轮次的反应变化
    2. 计算语义稳定性
    3. 检测意见一致性
    4. 判断是否可以提前终止迭代
    """

    def __init__(self, threshold: float = 0.85):
        """
        初始化收敛检测器

        Args:
            threshold: 收敛阈值，当收敛分数超过此值时认为已收敛
        """
        self.threshold = threshold
        self.history: List[Dict[str, Dict[str, Any]]] = []  # 历史反应记录

    def check_convergence(
        self,
        current_round: int,
        current_reactions: Dict[str, Dict[str, Any]],
        previous_reactions: Dict[str, Dict[str, Any]]
    ) -> ConvergenceResult:
        """
        检查是否收敛

        Args:
            current_round: 当前轮次
            current_reactions: 当前轮次反应
            previous_reactions: 上一轮次反应

        Returns:
            ConvergenceResult: 收敛检测结果
        """
        # 记录历史
        self.history.append(current_reactions)

        if current_round == 1:
            # 第一轮不可能收敛
            return ConvergenceResult(
                is_converged=False,
                convergence_score=0.0,
                role_convergence={},
                stable_aspects=[],
                changing_aspects=["所有方面的初始反应"],
                recommendation="继续迭代分析"
            )

        # 计算每个角色的收敛分数
        role_convergence = {}
        for role_id in current_reactions:
            current = current_reactions.get(role_id, {})
            previous = previous_reactions.get(role_id, {})

            if not previous:
                role_convergence[role_id] = 0.0
                continue

            # 计算反应相似度
            similarity = self._calculate_reaction_similarity(current, previous)
            role_convergence[role_id] = similarity

        # 计算总体收敛分数
        if role_convergence:
            overall_score = sum(role_convergence.values()) / len(role_convergence)
        else:
            overall_score = 0.0

        # 识别稳定和变化的方面
        stable_aspects = []
        changing_aspects = []

        for role_id, score in role_convergence.items():
            if score >= self.threshold:
                stable_aspects.append(role_id)
            else:
                changing_aspects.append(role_id)

        # 判断是否收敛
        is_converged = overall_score >= self.threshold and len(changing_aspects) <= len(role_convergence) * 0.2

        # 生成建议
        if is_converged:
            recommendation = "反应已趋于稳定，可以终止迭代"
        elif overall_score >= 0.7:
            recommendation = "接近收敛，建议再观察一轮"
        else:
            recommendation = "仍有较大变化，建议继续迭代"

        return ConvergenceResult(
            is_converged=is_converged,
            convergence_score=overall_score,
            role_convergence=role_convergence,
            stable_aspects=stable_aspects,
            changing_aspects=changing_aspects,
            recommendation=recommendation
        )

    def _calculate_reaction_similarity(
        self,
        reaction1: Dict[str, Any],
        reaction2: Dict[str, Any]
    ) -> float:
        """
        计算两个反应的相似度

        综合考虑：
        1. 情绪相似度
        2. 行动相似度
        3. 立场一致性
        4. 置信度变化
        """
        # 情绪相似度
        emotion1 = reaction1.get("emotion", "")
        emotion2 = reaction2.get("emotion", "")
        emotion_sim = self._text_similarity(emotion1, emotion2)

        # 行动相似度
        action1 = reaction1.get("action", "")
        action2 = reaction2.get("action", "")
        action_sim = self._text_similarity(action1, action2)

        # 置信度变化
        conf1 = reaction1.get("confidence", 0.5)
        conf2 = reaction2.get("confidence", 0.5)
        conf_diff = abs(conf1 - conf2)
        conf_sim = 1.0 - min(conf_diff, 1.0)

        # 立场变化检测
        stance_change = reaction2.get("stance_change", "")
        has_stance_change = 1.0 if stance_change else 0.0

        # 声明相似度
        stmt1 = reaction1.get("statement", "")
        stmt2 = reaction2.get("statement", "")
        stmt_sim = self._text_similarity(stmt1, stmt2)

        # 综合相似度（加权平均）
        weights = {
            "emotion": 0.25,
            "action": 0.25,
            "confidence": 0.15,
            "stance": 0.15,
            "statement": 0.20
        }

        overall_similarity = (
            emotion_sim * weights["emotion"] +
            action_sim * weights["action"] +
            conf_sim * weights["confidence"] +
            (1.0 - has_stance_change) * weights["stance"] +
            stmt_sim * weights["statement"]
        )

        return overall_similarity

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度（基于字符级别的Jaccard相似度）
        """
        if not text1 or not text2:
            return 0.0

        # 字符集合
        chars1 = set(text1)
        chars2 = set(text2)

        if not chars1 or not chars2:
            return 0.0

        # Jaccard相似度
        intersection = len(chars1 & chars2)
        union = len(chars1 | chars2)

        return intersection / union if union > 0 else 0.0

    def get_convergence_trend(self) -> List[float]:
        """
        获取收敛趋势（用于可视化）
        """
        if len(self.history) < 2:
            return []

        trends = []
        for i in range(1, len(self.history)):
            current = self.history[i]
            previous = self.history[i - 1]

            if not previous:
                trends.append(0.0)
                continue

            # 计算该轮的平均相似度
            similarities = []
            for role_id in current:
                if role_id in previous:
                    sim = self._calculate_reaction_similarity(
                        current[role_id],
                        previous[role_id]
                    )
                    similarities.append(sim)

            avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
            trends.append(avg_sim)

        return trends

    def predict_rounds_to_converge(self, current_score: float, trend: List[float]) -> int:
        """
        预测还需要多少轮达到收敛

        基于当前收敛分数和历史趋势进行预测
        """
        if current_score >= self.threshold:
            return 0

        if len(trend) < 2:
            # 数据不足，无法预测
            return -1

        # 计算平均改进率
        improvements = []
        for i in range(1, len(trend)):
            improvement = trend[i] - trend[i - 1]
            improvements.append(improvement)

        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.05

        if avg_improvement <= 0:
            # 没有改进，可能无法收敛
            return -1

        # 估算剩余轮次
        remaining_gap = self.threshold - current_score
        estimated_rounds = math.ceil(remaining_gap / avg_improvement)

        return min(estimated_rounds, 3)  # 最多预测3轮

    def reset(self):
        """重置检测器状态"""
        self.history = []
