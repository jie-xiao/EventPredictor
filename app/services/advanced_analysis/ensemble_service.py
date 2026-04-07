# P2.2 集成预测服务
import asyncio
import logging
import math
from typing import Any, Dict, List, Optional

from app.services.llm_service import llm_service
from app.services.response_cache_service import response_cache
from .models import (
    AdvancedAnalysisRequest,
    EnsembleResult,
    MethodResult,
)
from .monte_carlo_service import monte_carlo_service
from .bayesian_service import bayesian_service
from .causal_service import causal_service

logger = logging.getLogger(__name__)


class EnsembleService:
    """集成预测服务 — 并行运行多种方法, 加权投票整合结果"""

    def __init__(self):
        pass

    async def predict(self, event: AdvancedAnalysisRequest) -> EnsembleResult:
        """执行集成预测"""
        event_dict = event.model_dump()

        # 1. Check cache
        cached = await response_cache.get(event_dict, "ensemble")
        if cached:
            return EnsembleResult.model_validate(cached)

        # 2. Run all methods in parallel
        mc_result, bayes_result, causal_result = await asyncio.gather(
            self._safe_run("monte_carlo", monte_carlo_service.simulate, event),
            self._safe_run("bayesian", bayesian_service.analyze, event),
            self._safe_run("causal", causal_service.analyze, event),
        )

        # 3. Collect method results
        methods: List[MethodResult] = []

        if mc_result is not None:
            methods.append(MethodResult(
                method_name="monte_carlo",
                trend=mc_result.trend,
                confidence=mc_result.confidence,
                key_findings=[
                    f"模拟 {mc_result.n_simulations} 次，均值 {mc_result.mean:.3f}",
                    f"95% CI: [{mc_result.CI_95[0]:.3f}, {mc_result.CI_95[1]:.3f}]",
                    f"关键敏感因素: {', '.join(list(mc_result.sensitivity_analysis.keys())[:3])}",
                ],
            ))

        if bayes_result is not None:
            bayes_trend = self._posterior_to_trend(bayes_result.main_hypothesis_posterior)
            methods.append(MethodResult(
                method_name="bayesian",
                trend=bayes_trend,
                confidence=bayes_result.main_hypothesis_posterior,
                key_findings=[
                    f"假设后验概率: {bayes_result.main_hypothesis_posterior:.3f}",
                    f"证据节点数: {len(bayes_result.evidence_impact)}",
                    f"网络节点数: {len(bayes_result.nodes)}",
                ],
            ))

        if causal_result is not None:
            # Determine causal trend from total effects
            causal_trend = self._effects_to_trend(causal_result.total_effects)
            avg_strength = (
                sum(abs(v) for v in causal_result.total_effects.values()) /
                max(len(causal_result.total_effects), 1)
            )
            methods.append(MethodResult(
                method_name="causal",
                trend=causal_trend,
                confidence=min(avg_strength + 0.2, 0.95),
                key_findings=[
                    f"因果因素数: {len(causal_result.factors)}",
                    f"混杂因素: {', '.join(causal_result.confounders[:3]) or '无'}",
                    f"因果路径数: {len(causal_result.causal_paths)}",
                ],
            ))

        if not methods:
            methods.append(MethodResult(
                method_name="fallback",
                trend="SIDEWAYS",
                confidence=0.3,
                key_findings=["所有分析方法失败，使用默认结果"],
            ))

        # 4. Weighted voting
        result = self._aggregate(methods)

        # 5. LLM recommendation
        result.recommendation = await self._get_recommendation(event, result)

        # 6. Cache
        await response_cache.set(event_dict, result.model_dump(), "ensemble")
        return result

    async def _safe_run(self, name: str, func, event: AdvancedAnalysisRequest):
        """安全执行单个方法，失败时返回 None"""
        try:
            return await func(event)
        except Exception as e:
            logger.warning(f"Method {name} failed: {e}")
            return None

    def _posterior_to_trend(self, posterior: float) -> str:
        """将后验概率转换为趋势"""
        if posterior > 0.6:
            return "UP"
        elif posterior < 0.4:
            return "DOWN"
        return "SIDEWAYS"

    def _effects_to_trend(self, total_effects: Dict[str, float]) -> str:
        """将总效应转换为趋势"""
        if not total_effects:
            return "SIDEWAYS"
        avg = sum(total_effects.values()) / len(total_effects)
        if avg > 0.1:
            return "UP"
        elif avg < -0.1:
            return "DOWN"
        return "SIDEWAYS"

    def _aggregate(self, methods: List[MethodResult]) -> EnsembleResult:
        """加权聚合各方法结果"""
        # Base weights from confidence
        raw_weights = {m.method_name: m.confidence for m in methods}
        total_conf = sum(raw_weights.values()) or 1.0
        weights = {k: v / total_conf for k, v in raw_weights.items()}

        # Boost methods that agree with majority
        trend_counts: Dict[str, int] = {}
        for m in methods:
            trend_counts[m.trend] = trend_counts.get(m.trend, 0) + 1
        majority_trend = max(trend_counts, key=trend_counts.get)

        boosted_weights = {}
        for m in methods:
            w = weights[m.method_name]
            if m.trend == majority_trend:
                w *= 1.2  # 20% boost for agreement
            boosted_weights[m.method_name] = w

        # Re-normalize
        total_bw = sum(boosted_weights.values()) or 1.0
        final_weights = {k: v / total_bw for k, v in boosted_weights.items()}

        # Update method weights
        for m in methods:
            m.weight = final_weights[m.method_name]

        # Weighted probability voting
        trend_probs: Dict[str, float] = {"UP": 0.0, "DOWN": 0.0, "SIDEWAYS": 0.0}
        for m in methods:
            trend_probs[m.trend] = trend_probs.get(m.trend, 0.0) + m.weight * m.confidence

        total_prob = sum(trend_probs.values()) or 1.0
        weighted_probs = {k: v / total_prob for k, v in trend_probs.items()}

        unified_trend = max(weighted_probs, key=weighted_probs.get)
        unified_confidence = weighted_probs[unified_trend]

        # Agreement score
        agreement_count = sum(1 for m in methods if m.trend == unified_trend)
        agreement_score = agreement_count / len(methods) if methods else 0.0

        # Confidence interval
        confidences = [m.confidence for m in methods]
        mean_conf = sum(confidences) / len(confidences) if confidences else 0.5
        std_conf = math.sqrt(
            sum((c - mean_conf) ** 2 for c in confidences) / max(len(confidences), 1)
        )
        ci = [max(0, mean_conf - 1.96 * std_conf), min(1, mean_conf + 1.96 * std_conf)]

        # Uncertainty calibration
        uncertainty = {
            "cross_method_std": std_conf,
            "trend_entropy": self._entropy(list(weighted_probs.values())),
            "n_methods": len(methods),
            "agreement_ratio": agreement_score,
        }

        # Detailed results
        detailed = {}
        for m in methods:
            detailed[m.method_name] = {
                "trend": m.trend,
                "confidence": m.confidence,
                "weight": m.weight,
                "key_findings": m.key_findings,
            }

        return EnsembleResult(
            methods=methods,
            unified_trend=unified_trend,
            unified_confidence=unified_confidence,
            CI=ci,
            agreement_score=agreement_score,
            weighted_probabilities=weighted_probs,
            method_weights=final_weights,
            uncertainty_calibration=uncertainty,
            detailed_results=detailed,
        )

    def _entropy(self, probs: List[float]) -> float:
        """计算趋势概率分布的熵"""
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    async def _get_recommendation(
        self, event: AdvancedAnalysisRequest, result: EnsembleResult
    ) -> str:
        """调用 LLM 生成综合建议"""
        prompt = f"""基于多种量化分析方法的结果，请给出综合建议。

事件：{event.title}
描述：{event.description}

分析结果摘要：
- 统一趋势：{result.unified_trend}
- 统一置信度：{result.unified_confidence:.2%}
- 方法一致性：{result.agreement_score:.2%}
- 参与方法数：{len(result.methods)}

各方法结果：
{chr(10).join(f'- {m.method_name}: 趋势={m.trend}, 置信度={m.confidence:.2f}' for m in result.methods)}

请用2-3句话给出简洁的行动建议。"""

        try:
            response = await llm_service.generate(prompt)
            return response.strip() if isinstance(response, str) else str(response)
        except Exception:
            if result.unified_trend == "UP":
                return "多方法分析一致认为事件将产生正面影响，建议积极关注相关机会。"
            elif result.unified_trend == "DOWN":
                return "多方法分析显示事件可能产生负面影响，建议做好风险防范准备。"
            return "多方法分析显示事件发展趋势尚不明确，建议持续关注事态变化。"


# Global singleton
ensemble_service = EnsembleService()
