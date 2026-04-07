# P2.2 贝叶斯网络推理服务
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.llm_service import llm_service
from app.services.response_cache_service import response_cache
from .models import (
    AdvancedAnalysisRequest,
    BayesianEdge,
    BayesianNetworkLLMResponse,
    BayesianNode,
    BayesianResult,
)

logger = logging.getLogger(__name__)


class BayesianService:
    """贝叶斯网络推理服务 — LLM 生成网络结构和先验, 前向传播计算后验"""

    def __init__(self):
        pass

    async def analyze(self, event: AdvancedAnalysisRequest) -> BayesianResult:
        """执行贝叶斯网络分析"""
        event_dict = event.model_dump()

        # 1. Check cache
        cached = await response_cache.get(event_dict, "bayesian")
        if cached:
            return BayesianResult.model_validate(cached)

        # 2. LLM generates network structure
        network = await self._get_network_from_llm(event)

        # 3. Build and run inference
        result = self._run_inference(network)

        # 4. Cache
        await response_cache.set(event_dict, result.model_dump(), "bayesian")
        return result

    async def _get_network_from_llm(
        self, event: AdvancedAnalysisRequest
    ) -> BayesianNetworkLLMResponse:
        """调用 LLM 生成贝叶斯网络结构"""
        prompt = f"""你是一个贝叶斯网络专家。请为以下事件构建一个贝叶斯网络模型。

事件标题：{event.title}
事件描述：{event.description}
分类：{event.category}
重要性：{event.importance}/5

请设计 5-8 个节点，包含：
- nodes: 网络节点列表，每个节点有:
  - id: 节点ID (简短英文)
  - name: 节点名称
  - description: 描述
  - node_type: 节点类型 (factor/evidence/hypothesis)
  - prior_probability: 先验概率 (0-1)
- edges: 边列表，每条边有:
  - source_id: 源节点ID
  - target_id: 目标节点ID
  - conditional_probability: 条件概率 (0-1)
  - relationship_type: 关系类型 (influence/cause/correlate)
- evidence_nodes: 已知证据节点ID列表
- hypothesis_node: 假设节点ID (主要预测目标)
- reasoning: 建模理由

请确保网络有向无环，evidence节点至少2个，hypothesis节点1个。"""

        try:
            return await llm_service.generate_structured(prompt, BayesianNetworkLLMResponse)
        except Exception as e:
            logger.warning(f"LLM network generation failed: {e}, using defaults")
            return self._default_network(event)

    def _default_network(self, event: AdvancedAnalysisRequest) -> BayesianNetworkLLMResponse:
        """默认贝叶斯网络"""
        imp = event.importance / 5.0
        return BayesianNetworkLLMResponse(
            nodes=[
                BayesianNode(id="policy", name="政策因素", description="政策变化的影响", node_type="evidence", prior_probability=0.4 + 0.1 * imp),
                BayesianNode(id="market", name="市场状况", description="市场环境状态", node_type="evidence", prior_probability=0.5),
                BayesianNode(id="sentiment", name="社会情绪", description="公众情绪倾向", node_type="factor", prior_probability=0.45),
                BayesianNode(id="international", name="国际环境", description="国际关系影响", node_type="evidence", prior_probability=0.5 + 0.05 * imp),
                BayesianNode(id="economic", name="经济影响", description="经济层面的影响", node_type="factor", prior_probability=0.4),
                BayesianNode(id="outcome", name="最终结果", description="事件发展趋势", node_type="hypothesis", prior_probability=0.5),
            ],
            edges=[
                BayesianEdge(source_id="policy", target_id="economic", conditional_probability=0.7, relationship_type="cause"),
                BayesianEdge(source_id="market", target_id="economic", conditional_probability=0.6, relationship_type="influence"),
                BayesianEdge(source_id="sentiment", target_id="outcome", conditional_probability=0.5, relationship_type="influence"),
                BayesianEdge(source_id="international", target_id="outcome", conditional_probability=0.6, relationship_type="cause"),
                BayesianEdge(source_id="economic", target_id="outcome", conditional_probability=0.75, relationship_type="cause"),
                BayesianEdge(source_id="policy", target_id="sentiment", conditional_probability=0.4, relationship_type="influence"),
            ],
            evidence_nodes=["policy", "market", "international"],
            hypothesis_node="outcome",
            reasoning="基于事件特征构建的三层贝叶斯网络：证据层→中间因素层→假设层",
        )

    def _run_inference(self, network: BayesianNetworkLLMResponse) -> BayesianResult:
        """前向传播贝叶斯推理"""
        nodes = {n.id: n for n in network.nodes}
        edges = network.edges

        # Build adjacency: parent -> children
        children: Dict[str, List[str]] = {n.id: [] for n in network.nodes}
        edge_map: Dict[str, Dict[str, BayesianEdge]] = {}
        for edge in edges:
            if edge.source_id not in edge_map:
                edge_map[edge.source_id] = {}
            edge_map[edge.source_id][edge.target_id] = edge
            children[edge.source_id].append(edge.target_id)

        # Topological sort (Kahn's algorithm)
        in_degree: Dict[str, int] = {n.id: 0 for n in network.nodes}
        for edge in edges:
            in_degree[edge.target_id] = in_degree.get(edge.target_id, 0) + 1
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        topo_order: List[str] = []
        while queue:
            nid = queue.pop(0)
            topo_order.append(nid)
            for child in children.get(nid, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        # Forward pass: compute posteriors
        posteriors: Dict[str, float] = {}
        evidence_set = set(network.evidence_nodes)

        for nid in topo_order:
            node = nodes.get(nid)
            if node is None:
                continue
            prior = node.prior_probability

            # Get parent contributions
            parent_contribution = 0.0
            parent_count = 0
            for edge in edges:
                if edge.target_id == nid and edge.source_id in posteriors:
                    parent_posterior = posteriors[edge.source_id]
                    cp = edge.conditional_probability
                    # Weighted influence: parent posterior * conditional probability
                    parent_contribution += parent_posterior * cp
                    parent_count += 1

            if parent_count > 0:
                # Combine prior with parent evidence
                avg_parent = parent_contribution / parent_count
                posterior = 0.4 * prior + 0.6 * avg_parent
            else:
                posterior = prior

            # Clamp to [0.01, 0.99]
            posteriors[nid] = max(0.01, min(0.99, posterior))

        # Compute evidence impact on hypothesis
        hypothesis_posterior = posteriors.get(network.hypothesis_node, 0.5)
        evidence_impact: Dict[str, float] = {}
        for eid in network.evidence_nodes:
            if eid in nodes:
                original_prior = nodes[eid].prior_probability
                evidence_impact[eid] = abs(original_prior - posteriors.get(eid, original_prior))

        # Build influence diagram
        diagram_nodes = []
        for n in network.nodes:
            diagram_nodes.append({
                "id": n.id,
                "name": n.name,
                "type": n.node_type,
                "prior": n.prior_probability,
                "posterior": posteriors.get(n.id, n.prior_probability),
            })
        diagram_edges = []
        for e in edges:
            diagram_edges.append({
                "source": e.source_id,
                "target": e.target_id,
                "strength": e.conditional_probability,
                "type": e.relationship_type,
            })

        return BayesianResult(
            nodes=diagram_nodes,
            edges=edges,
            posteriors=posteriors,
            main_hypothesis_posterior=hypothesis_posterior,
            evidence_impact=evidence_impact,
            influence_diagram={"nodes": diagram_nodes, "edges": diagram_edges},
            reasoning=network.reasoning,
        )


# Global singleton
bayesian_service = BayesianService()
