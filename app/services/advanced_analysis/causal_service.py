# P2.2 因果推理服务
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from app.services.llm_service import llm_service
from app.services.response_cache_service import response_cache
from .models import (
    AdvancedAnalysisRequest,
    CausalFactor,
    CausalGraphLLMResponse,
    CausalLink,
    CausalResult,
)

logger = logging.getLogger(__name__)


class CausalService:
    """因果推理服务 — LLM 提取因果结构, 图算法计算直接/间接/总效应"""

    def __init__(self):
        pass

    async def analyze(self, event: AdvancedAnalysisRequest) -> CausalResult:
        """执行因果分析"""
        event_dict = event.model_dump()

        # 1. Check cache
        cached = await response_cache.get(event_dict, "causal")
        if cached:
            return CausalResult.model_validate(cached)

        # 2. LLM extracts causal structure
        graph = await self._get_graph_from_llm(event)

        # 3. Build and analyze graph
        result = self._analyze_graph(graph)

        # 4. Cache
        await response_cache.set(event_dict, result.model_dump(), "causal")
        return result

    async def _get_graph_from_llm(
        self, event: AdvancedAnalysisRequest
    ) -> CausalGraphLLMResponse:
        """调用 LLM 获取因果图"""
        prompt = f"""你是一个因果推理专家。请为以下事件构建因果图模型。

事件标题：{event.title}
事件描述：{event.description}
分类：{event.category}
重要性：{event.importance}/5

请提取 5-8 个因果因素和它们之间的因果关系：
- factors: 因果因素列表，每个因素有:
  - id: 因素ID (简短英文)
  - name: 因素名称
  - description: 描述
  - factor_type: 类型 (cause/effect/mediator/confounder)
  - direction: 影响方向 (-1到+1)
  - strength: 影响强度 (0-1)
- links: 因果链接列表，每个链接有:
  - source_id: 源因素ID
  - target_id: 目标因素ID
  - mechanism: 因果机制描述
  - strength: 因果强度 (0-1)
  - lag_time: 滞后时间 (immediate/short/medium/long)
- confounders: 混杂因素ID列表
- main_effect: 主要效应描述
- reasoning: 因果分析理由

确保因果图是有向的，包含至少1个主要结果因素。"""

        try:
            return await llm_service.generate_structured(prompt, CausalGraphLLMResponse)
        except Exception as e:
            logger.warning(f"LLM causal graph generation failed: {e}, using defaults")
            return self._default_graph(event)

    def _default_graph(self, event: AdvancedAnalysisRequest) -> CausalGraphLLMResponse:
        """默认因果图"""
        imp = event.importance / 5.0
        return CausalGraphLLMResponse(
            factors=[
                CausalFactor(id="policy_change", name="政策变化", factor_type="cause", direction=0.7, strength=0.6 + 0.1 * imp),
                CausalFactor(id="market_reaction", name="市场反应", factor_type="effect", direction=0.5, strength=0.5),
                CausalFactor(id="public_sentiment", name="公众情绪", factor_type="mediator", direction=0.3, strength=0.4),
                CausalFactor(id="international_pressure", name="国际压力", factor_type="cause", direction=0.6, strength=0.5 + 0.05 * imp),
                CausalFactor(id="economic_impact", name="经济影响", factor_type="effect", direction=0.8, strength=0.7),
                CausalFactor(id="media_coverage", name="媒体报道", factor_type="confounder", direction=0.4, strength=0.3),
            ],
            links=[
                CausalLink(source_id="policy_change", target_id="market_reaction", mechanism="政策直接影响市场预期", strength=0.7, lag_time="immediate"),
                CausalLink(source_id="policy_change", target_id="public_sentiment", mechanism="政策引发公众关注", strength=0.5, lag_time="short"),
                CausalLink(source_id="international_pressure", target_id="policy_change", mechanism="国际压力影响政策制定", strength=0.4, lag_time="medium"),
                CausalLink(source_id="market_reaction", target_id="economic_impact", mechanism="市场变化传导至实体经济", strength=0.6, lag_time="short"),
                CausalLink(source_id="public_sentiment", target_id="economic_impact", mechanism="公众情绪影响消费信心", strength=0.3, lag_time="medium"),
                CausalLink(source_id="media_coverage", target_id="public_sentiment", mechanism="媒体影响公众认知", strength=0.5, lag_time="immediate"),
                CausalLink(source_id="media_coverage", target_id="market_reaction", mechanism="媒体报道影响市场情绪", strength=0.4, lag_time="immediate"),
            ],
            confounders=["media_coverage"],
            main_effect="policy_change → market_reaction → economic_impact",
            reasoning="基于事件特征构建的三层因果图：根因→中介→最终效应，媒体覆盖作为混杂因素同时影响多个节点。",
        )

    def _analyze_graph(self, graph: CausalGraphLLMResponse) -> CausalResult:
        """分析因果图：直接效应、间接效应、总效应、混杂因素、因果路径"""
        factors = {f.id: f for f in graph.factors}
        links = graph.links

        # Build adjacency list
        children: Dict[str, List[CausalLink]] = defaultdict(list)
        parents: Dict[str, List[CausalLink]] = defaultdict(list)
        for link in links:
            children[link.source_id].append(link)
            parents[link.target_id].append(link)

        # Find the main outcome (first 'effect' type factor, or last factor)
        outcome_id = None
        for f in graph.factors:
            if f.factor_type == "effect":
                outcome_id = f.id
                break
        if outcome_id is None and graph.factors:
            outcome_id = graph.factors[-1].id

        # Direct effects: strength * direction for each link pointing to outcome
        direct_effects: Dict[str, float] = {}
        for link in links:
            if link.target_id == outcome_id:
                factor = factors.get(link.source_id)
                direction = factor.direction if factor else 1.0
                direct_effects[link.source_id] = link.strength * direction

        # Indirect effects: DFS from each cause to outcome through mediators
        indirect_effects: Dict[str, float] = {}
        causal_paths: List[Dict[str, Any]] = []

        for f in graph.factors:
            if f.id == outcome_id:
                continue
            paths = self._find_all_paths(f.id, outcome_id, children, set())
            for path in paths:
                if len(path) <= 2:
                    continue  # Direct path, skip
                # Path effect = product of edge strengths * directions
                path_strength = 1.0
                path_detail = {"from": f.id, "to": outcome_id, "path": [], "strength": 0.0}
                for i in range(len(path) - 1):
                    link = self._find_link(path[i], path[i + 1], children)
                    if link:
                        path_strength *= link.strength
                        path_detail["path"].append({
                            "source": path[i],
                            "target": path[i + 1],
                            "strength": link.strength,
                        })
                factor = factors.get(f.id)
                direction = factor.direction if factor else 1.0
                path_detail["strength"] = path_strength * direction
                causal_paths.append(path_detail)

                # Accumulate indirect effects
                if f.id not in indirect_effects:
                    indirect_effects[f.id] = 0.0
                indirect_effects[f.id] += path_strength * direction

        # Total effects
        total_effects: Dict[str, float] = {}
        for fid in set(list(direct_effects.keys()) + list(indirect_effects.keys())):
            total_effects[fid] = direct_effects.get(fid, 0.0) + indirect_effects.get(fid, 0.0)

        # Identify confounders: factors that affect both a cause and the outcome
        confounder_ids = set(graph.confounders)
        # Also auto-detect: if a factor has paths to both outcome and a cause
        outcome_ancestors: Set[str] = set()
        self._find_ancestors(outcome_id, parents, outcome_ancestors)
        for f in graph.factors:
            if f.id == outcome_id:
                continue
            cause_ancestors: Set[str] = set()
            self._find_ancestors(f.id, parents, cause_ancestors)
            common = outcome_ancestors & cause_ancestors
            confounder_ids.update(common)

        # Build graph_data for visualization
        graph_nodes = []
        for f in graph.factors:
            graph_nodes.append({
                "id": f.id,
                "name": f.name,
                "type": f.factor_type,
                "direction": f.direction,
                "strength": f.strength,
                "is_confounder": f.id in confounder_ids,
            })
        graph_edges = []
        for link in links:
            graph_edges.append({
                "source": link.source_id,
                "target": link.target_id,
                "strength": link.strength,
                "mechanism": link.mechanism,
                "lag_time": link.lag_time,
            })

        return CausalResult(
            factors=graph.factors,
            links=links,
            direct_effects=direct_effects,
            indirect_effects=indirect_effects,
            total_effects=total_effects,
            confounders=list(confounder_ids),
            causal_paths=causal_paths,
            graph_data={"nodes": graph_nodes, "edges": graph_edges},
        )

    def _find_all_paths(
        self,
        start: str,
        end: str,
        children: Dict[str, List[CausalLink]],
        visited: Set[str],
        max_depth: int = 6,
    ) -> List[List[str]]:
        """DFS 查找所有从 start 到 end 的路径"""
        if start == end:
            return [[end]]
        if max_depth <= 0:
            return []

        results = []
        visited = visited | {start}
        for link in children.get(start, []):
            if link.target_id not in visited:
                sub_paths = self._find_all_paths(
                    link.target_id, end, children, visited, max_depth - 1
                )
                for sp in sub_paths:
                    results.append([start] + sp)
        return results

    def _find_link(
        self, source_id: str, target_id: str, children: Dict[str, List[CausalLink]]
    ) -> Optional[CausalLink]:
        """查找两节点间的边"""
        for link in children.get(source_id, []):
            if link.target_id == target_id:
                return link
        return None

    def _find_ancestors(
        self, node_id: str, parents: Dict[str, List[CausalLink]], ancestors: Set[str]
    ) -> None:
        """查找所有祖先节点"""
        for link in parents.get(node_id, []):
            if link.source_id not in ancestors:
                ancestors.add(link.source_id)
                self._find_ancestors(link.source_id, parents, ancestors)


# Global singleton
causal_service = CausalService()
