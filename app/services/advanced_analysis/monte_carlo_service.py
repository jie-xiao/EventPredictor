# P2.2 蒙特卡洛模拟服务
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import numpy as np

from app.services.llm_service import llm_service
from app.services.response_cache_service import response_cache
from .models import (
    AdvancedAnalysisRequest,
    MonteCarloResult,
    MonteCarloScenarioLLMResponse,
    ScenarioVariable,
)

logger = logging.getLogger(__name__)


class MonteCarloService:
    """蒙特卡洛模拟服务 — LLM 生成情景变量, numpy 执行随机模拟"""

    def __init__(self):
        self._rng = np.random.default_rng(42)

    async def simulate(
        self,
        event: AdvancedAnalysisRequest,
        n_simulations: int = 1000,
    ) -> MonteCarloResult:
        """运行蒙特卡洛模拟"""
        event_dict = event.model_dump()

        # 1. Check cache
        cached = await response_cache.get(event_dict, "monte_carlo")
        if cached:
            return MonteCarloResult.model_validate(cached)

        # 2. LLM generates scenario variables
        scenario = await self._get_scenario_from_llm(event)

        # 3. Run simulations
        result = self._run_simulations(scenario, n_simulations)

        # 4. Cache result
        await response_cache.set(event_dict, result.model_dump(), "monte_carlo")
        return result

    async def _get_scenario_from_llm(
        self, event: AdvancedAnalysisRequest
    ) -> MonteCarloScenarioLLMResponse:
        """调用 LLM 获取情景变量"""
        prompt = f"""你是一个量化风险分析师。请为以下事件设计蒙特卡洛模拟的随机变量和参数。

事件标题：{event.title}
事件描述：{event.description}
分类：{event.category}
重要性：{event.importance}/5

请生成 4-6 个影响该事件结果的关键变量，每个变量包含：
- name: 变量名称（简短）
- description: 变量描述
- distribution_type: 分布类型 (normal/uniform/beta/triangular)
- params: 分布参数 (如 mean/std, low/high, alpha/beta 等)
- impact_direction: 对结果的影响方向 (-1 到 +1，正值=正面影响，负值=负面影响)
- weight: 该变量的权重 (0-1)

同时给出：
- base_probability: 基准概率 (0-1)
- trend_direction: 趋势方向 (UP/DOWN/SIDEWAYS)
- key_assumptions: 关键假设 (2-4条)
- confidence: 分析置信度 (0-1)"""

        try:
            response = await llm_service.generate_structured(
                prompt, MonteCarloScenarioLLMResponse
            )
            return response
        except Exception as e:
            logger.warning(f"LLM scenario generation failed: {e}, using defaults")
            return self._default_scenario(event)

    def _default_scenario(self, event: AdvancedAnalysisRequest) -> MonteCarloScenarioLLMResponse:
        """默认情景（LLM 不可用时的 fallback）"""
        importance = event.importance / 5.0
        return MonteCarloScenarioLLMResponse(
            variables=[
                ScenarioVariable(
                    name="政策影响",
                    description="政策变化对事件的影响程度",
                    distribution_type="normal",
                    params={"mean": 0.5 * importance, "std": 0.15},
                    impact_direction=0.7,
                    weight=0.3,
                ),
                ScenarioVariable(
                    name="市场反应",
                    description="市场对该事件的反应强度",
                    distribution_type="normal",
                    params={"mean": 0.4 * importance, "std": 0.2},
                    impact_direction=0.5,
                    weight=0.25,
                ),
                ScenarioVariable(
                    name="舆论影响",
                    description="社会舆论对事件的关注度",
                    distribution_type="beta",
                    params={"alpha": 2.0, "beta": 3.0},
                    impact_direction=0.3,
                    weight=0.2,
                ),
                ScenarioVariable(
                    name="国际因素",
                    description="国际环境对事件的影响",
                    distribution_type="uniform",
                    params={"low": -0.3, "high": 0.5},
                    impact_direction=0.6,
                    weight=0.15,
                ),
                ScenarioVariable(
                    name="时间因素",
                    description="事件发展的时间维度影响",
                    distribution_type="triangular",
                    params={"left": -0.2, "mode": 0.3, "right": 0.7},
                    impact_direction=0.4,
                    weight=0.1,
                ),
            ],
            base_probability=0.5 + 0.1 * importance,
            trend_direction="SIDEWAYS",
            key_assumptions=[
                "当前政策环境保持基本稳定",
                "市场反应在合理范围内",
                "无重大突发事件干扰",
            ],
            confidence=0.5 + 0.05 * importance,
        )

    def _run_simulations(
        self,
        scenario: MonteCarloScenarioLLMResponse,
        n_simulations: int,
    ) -> MonteCarloResult:
        """执行蒙特卡洛模拟"""
        variables = scenario.variables
        if not variables:
            variables = self._default_scenario(
                AdvancedAnalysisRequest(title="default", description="default")
            ).variables

        # Normalize weights
        total_weight = sum(v.weight for v in variables) or 1.0

        # Sample each variable
        n_vars = len(variables)
        samples_matrix = np.zeros((n_simulations, n_vars))
        weights = np.array([v.weight / total_weight for v in variables])
        impacts = np.array([v.impact_direction for v in variables])

        for i, var in enumerate(variables):
            samples_matrix[:, i] = self._sample_distribution(var, n_simulations)

        # Compute outcome: weighted sum of (sample * impact_direction)
        outcome_scores = samples_matrix @ (weights * impacts)

        # Classify outcomes
        up_ratio = float(np.mean(outcome_scores > 0.15))
        down_ratio = float(np.mean(outcome_scores < -0.15))
        sideways_ratio = 1.0 - up_ratio - down_ratio

        # Determine trend
        if up_ratio > down_ratio and up_ratio > sideways_ratio:
            trend = "UP"
        elif down_ratio > up_ratio and down_ratio > sideways_ratio:
            trend = "DOWN"
        else:
            trend = "SIDEWAYS"

        # Confidence based on dominant direction
        max_ratio = max(up_ratio, down_ratio, sideways_ratio)
        confidence = float(max_ratio)

        # Statistics
        mean_val = float(np.mean(outcome_scores))
        std_val = float(np.std(outcome_scores))
        sorted_scores = np.sort(outcome_scores)
        ci_95 = [float(sorted_scores[int(0.025 * n_simulations)]),
                  float(sorted_scores[int(0.975 * n_simulations)])]
        ci_80 = [float(sorted_scores[int(0.1 * n_simulations)]),
                  float(sorted_scores[int(0.9 * n_simulations)])]

        # Sensitivity analysis: correlation between each variable and outcome
        sensitivity = {}
        for i, var in enumerate(variables):
            corr = np.corrcoef(samples_matrix[:, i], outcome_scores)[0, 1]
            sensitivity[var.name] = float(corr) if not np.isnan(corr) else 0.0

        # Sample 20 simulation details
        indices = self._rng.choice(n_simulations, min(20, n_simulations), replace=False)
        details = []
        for idx in sorted(indices):
            detail = {"simulation_id": int(idx), "outcome_score": float(outcome_scores[idx])}
            for j, var in enumerate(variables):
                detail[var.name] = float(samples_matrix[idx, j])
            details.append(detail)

        # Probability distribution (binned)
        hist, bin_edges = np.histogram(outcome_scores, bins=10, density=False)
        prob_dist = {}
        bin_labels = ["very_low", "low", "low_mid", "mid_low", "mid",
                      "mid_high", "high_mid", "high", "very_high", "extreme"]
        for k in range(len(hist)):
            prob_dist[bin_labels[k]] = float(hist[k] / n_simulations)

        return MonteCarloResult(
            n_simulations=n_simulations,
            probability_distribution=prob_dist,
            mean=mean_val,
            std=std_val,
            CI_95=ci_95,
            CI_80=ci_80,
            sensitivity_analysis=sensitivity,
            trend=trend,
            confidence=confidence,
            simulation_details=details,
            variables_used=variables,
            assumptions=scenario.key_assumptions,
        )

    def _sample_distribution(self, var: ScenarioVariable, n: int) -> np.ndarray:
        """根据分布类型采样"""
        dt = var.distribution_type.lower()
        p = var.params

        if dt == "normal":
            mean = p.get("mean", 0.5)
            std = p.get("std", 0.15)
            return self._rng.normal(mean, std, n)
        elif dt == "uniform":
            low = p.get("low", 0.0)
            high = p.get("high", 1.0)
            return self._rng.uniform(low, high, n)
        elif dt == "beta":
            alpha = p.get("alpha", 2.0)
            beta = p.get("beta", 5.0)
            return self._rng.beta(alpha, beta, n)
        elif dt == "triangular":
            left = p.get("left", 0.0)
            mode = p.get("mode", 0.5)
            right = p.get("right", 1.0)
            return self._rng.triangular(left, mode, right, n)
        else:
            return self._rng.normal(0.5, 0.15, n)


# Global singleton
monte_carlo_service = MonteCarloService()
