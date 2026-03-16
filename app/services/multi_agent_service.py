# 多Agent角色分析服务
# P0阶段：集成历史模式匹配 + 响应缓存
import asyncio
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.agents.roles import ROLES, AgentRole, RoleCategory
from app.services.llm_service import llm_service, RoleAnalysisResponse, CrossAnalysisResponse
from app.services.pattern_matcher_service import pattern_matcher
from app.services.response_cache_service import response_cache


class RoleAnalysisResult:
    """单角色分析结果"""
    def __init__(
        self,
        role_id: str,
        role_name: str,
        category: str,
        stance: str,
        reaction: Dict[str, str],
        impact: Dict[str, str],
        timeline: List[Dict[str, Any]],
        confidence: float,
        reasoning: str,
        statement: str = ""
    ):
        self.role_id = role_id
        self.role_name = role_name
        self.category = category
        self.stance = stance
        self.reaction = reaction
        self.impact = impact
        self.timeline = timeline
        self.confidence = confidence
        self.reasoning = reasoning
        self.statement = statement

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "category": self.category,
            "stance": self.stance,
            "reaction": self.reaction,
            "impact": self.impact,
            "timeline": self.timeline,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "statement": self.statement
        }


class MultiAgentAnalysisService:
    """多Agent角色分析服务（P0阶段：集成缓存和模式匹配）"""

    def __init__(self):
        self.llm = llm_service
        # P0阶段：缓存和模式匹配服务
        self.cache = response_cache
        self.pattern_matcher = pattern_matcher

    async def analyze_with_roles(
        self,
        event: Dict[str, Any],
        role_ids: List[str],
        depth: str = "standard",
        use_cache: bool = True,
        find_similar: bool = True
    ) -> Dict[str, Any]:
        """
        使用指定角色进行多Agent分析（P0阶段：集成缓存和模式匹配）

        Args:
            event: 事件信息
            role_ids: 要分析的角色ID列表
            depth: 分析深度 (simple/standard/detailed)
            use_cache: 是否使用缓存（默认True）
            find_similar: 是否查找相似历史事件（默认True）

        Returns:
            包含各角色分析结果的字典
        """
        # P0阶段：尝试从缓存获取
        if use_cache:
            cache_key_data = {
                **event,
                "role_ids": sorted(role_ids),
                "depth": depth
            }
            cached_result = await self.cache.get(cache_key_data, "multi_agent")

            if cached_result is not None:
                # 缓存命中
                cached_result["_cache_hit"] = True
                return cached_result

        # P0阶段：查找相似历史事件
        similar_patterns = []
        if find_similar:
            similar_patterns = await self.pattern_matcher.find_similar_events(
                event,
                top_k=3,
                min_similarity=0.4
            )
        # 获取角色定义
        roles = [ROLES[rid] for rid in role_ids if rid in ROLES]

        if not roles:
            return {"error": "No valid roles specified"}

        # 并行执行各角色分析 - 使用结构化输出
        tasks = [self._analyze_single_role_structured(event, role, depth) for role in roles]
        role_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_results = []
        for r in role_results:
            if isinstance(r, Exception):
                print(f"Role analysis error: {r}")
            else:
                valid_results.append(r)

        # 按类别分组
        categorized = self._categorize_results(valid_results)

        # 使用LLM进行增强的交叉分析
        cross_analysis = await self._llm_cross_analysis(event, valid_results)

        # 综合推演
        synthesis = await self._synthesize(event, valid_results, cross_analysis)

        # 构建结果
        result = {
            "event": event,
            "role_analyses": [r.to_dict() for r in valid_results],
            "categorized": categorized,
            "cross_analysis": cross_analysis,
            "synthesis": synthesis,
            "timestamp": datetime.utcnow().isoformat(),
            "_cache_hit": False
        }

        # P0阶段：添加相似模式信息
        if similar_patterns:
            result["similar_patterns"] = [
                {
                    "title": p.get("title"),
                    "similarity": p.get("similarity_score"),
                    "trend": p.get("prediction", {}).get("trend"),
                    "confidence": p.get("prediction", {}).get("confidence")
                }
                for p in similar_patterns
            ]

        # P0阶段：缓存结果
        if use_cache:
            cache_key_data = {
                **event,
                "role_ids": sorted(role_ids),
                "depth": depth
            }
            await self.cache.set(cache_key_data, result, "multi_agent")

        return result

    async def _analyze_single_role_structured(
        self,
        event: Dict[str, Any],
        role: AgentRole,
        depth: str
    ) -> RoleAnalysisResult:
        """使用结构化输出分析单个角色"""
        prompt = self._build_analysis_prompt(event, role, depth)

        try:
            # 使用结构化输出
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=RoleAnalysisResponse,
                system_prompt=role.system_prompt
            )

            return RoleAnalysisResult(
                role_id=role.id,
                role_name=role.name,
                category=role.category.value,
                stance=response.stance,
                reaction=response.reaction,
                impact=response.impact,
                timeline=response.timeline,
                confidence=response.confidence,
                reasoning=response.reasoning,
                statement=response.reaction.get("statement", "")
            )

        except Exception as e:
            print(f"Structured analysis failed for role {role.id}: {e}")
            # 返回基于规则的备用分析
            return self._fallback_analysis(role, event)

    def _build_analysis_prompt(self, event: Dict[str, Any], role: AgentRole, depth: str) -> str:
        """构建分析提示词"""

        depth_instruction = {
            "simple": "提供简洁的分析要点",
            "standard": "提供全面的分析，包括影响和行动",
            "detailed": "提供深入的分析，包括详细推理、时间线和多情景"
        }.get(depth, "提供全面的分析")

        prompt = f"""请分析以下事件，从{role.name}的角度进行反应分析：

事件标题：{event.get('title', 'N/A')}
事件描述：{event.get('description', 'N/A')}
事件类别：{event.get('category', 'N/A')}
严重程度：{event.get('importance', 3)}/5
时间：{event.get('timestamp', 'N/A')}

{depth_instruction}。

请按照以下格式输出你的分析：

1. **立场 (stance)**: 简述你的立场
2. **反应 (reaction)**:
   - 情绪 (emotion): 可能的情绪反应
   - 行动 (action): 可能采取的行动
   - 声明 (statement): 可能发表的公开声明
3. **影响分析 (impact)**:
   - 经济影响 (economic)
   - 政治影响 (political)
   - 社会影响 (social)
4. **时间线 (timeline)**: 未来可能的发展节点（每个节点包含时间、事件、概率）
5. **置信度 (confidence)**: 你分析的置信度 (0-1)
6. **推理过程 (reasoning)**: 详细的推理过程

请确保分析符合你作为{role.name}的角色特点。"""

        return prompt

    def _parse_role_response(
        self,
        role: AgentRole,
        event: Dict[str, Any],
        response: str,
        depth: str
    ) -> RoleAnalysisResult:
        """解析LLM响应（保留用于向后兼容）"""

        # 简单的文本解析 - 实际可以用更复杂的解析逻辑
        lines = response.split("\n")

        stance = role.stance
        statement = ""
        emotion = "谨慎观察"
        action = "评估形势"

        # 提取声明
        for line in lines:
            if "声明" in line or "statement" in line.lower():
                statement = line.split(":")[-1].strip() if ":" in line else line
            if "情绪" in line or "emotion" in line.lower():
                emotion = line.split(":")[-1].strip() if ":" in line else line
            if "行动" in line or "action" in line.lower():
                action = line.split(":")[-1].strip() if ":" in line else line

        # 提取影响
        impact = {
            "economic": "需要进一步评估",
            "political": "需要进一步评估",
            "social": "需要进一步评估"
        }

        # 提取时间线
        timeline = []
        if depth == "detailed":
            timeline = [
                {"time": "短期(1-7天)", "event": "初步反应和评估", "probability": 0.8},
                {"time": "中期(1-3月)", "event": "制定应对策略", "probability": 0.6},
                {"time": "长期(3-12月)", "event": "策略效果显现", "probability": 0.5}
            ]

        confidence = 0.7

        return RoleAnalysisResult(
            role_id=role.id,
            role_name=role.name,
            category=role.category.value,
            stance=stance,
            reaction={
                "emotion": emotion,
                "action": action,
                "statement": statement or f"我们正在密切关注事态发展。"
            },
            impact=impact,
            timeline=timeline,
            confidence=confidence,
            reasoning=response[:500] if len(response) > 500 else response,
            statement=statement
        )

    def _fallback_analysis(self, role: AgentRole, event: Dict[str, Any]) -> RoleAnalysisResult:
        """备用分析 - 当LLM调用失败时使用"""

        # 基于规则的简单分析
        importance = event.get("importance", 3)

        return RoleAnalysisResult(
            role_id=role.id,
            role_name=role.name,
            category=role.category.value,
            stance=role.stance,
            reaction={
                "emotion": "关注" if importance < 4 else "高度关注",
                "action": "评估影响并准备应对",
                "statement": f"我们正在密切关注{event.get('title', '该事件')}的发展。"
            },
            impact={
                "economic": "需要评估",
                "political": "需要评估",
                "social": "需要评估"
            },
            timeline=[
                {"time": "短期", "event": "观察评估", "probability": 0.7}
            ],
            confidence=0.5,
            reasoning=f"基于{role.name}的角色特点进行分析",
            statement=""
        )

    def _categorize_results(self, results: List[RoleAnalysisResult]) -> Dict[str, List[Dict]]:
        """按类别分组分析结果"""
        categorized = {}

        for result in results:
            cat = result.category
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(result.to_dict())

        return categorized

    async def _llm_cross_analysis(
        self,
        event: Dict[str, Any],
        results: List[RoleAnalysisResult]
    ) -> Dict[str, Any]:
        """使用LLM进行增强的交叉分析"""

        # 准备角色观点摘要
        role_views = []
        for r in results:
            role_views.append(f"""
【{r.role_name}】({r.category})
- 立场: {r.stance}
- 行动: {r.reaction.get('action', 'N/A')}
- 情绪: {r.reaction.get('emotion', 'N/A')}
- 经济影响: {r.impact.get('economic', 'N/A')}
- 政治影响: {r.impact.get('political', 'N/A')}
- 社会影响: {r.impact.get('social', 'N/A')}
- 置信度: {r.confidence * 100:.0f}%
- 推理: {r.reasoning[:200]}...
""")

        prompt = f"""请对以下各方观点进行交叉分析：

事件：{event.get('title', 'N/A')}
描述：{event.get('description', 'N/A')}

各方观点：
{''.join(role_views)}

请分析：
1. agreements: 角色之间的共识点（每个包含 role1, role2, point, strength 0-1）
2. conflicts: 角色之间的冲突点（每个包含 role1, role2, point, severity: 高/中/低）
3. synergies: 角色之间的协同效应（每个包含 roles, description, potential）
4. consensus: 所有关键共识的简单描述列表
5. overall_trend: 整体趋势预测（上涨/下跌/平稳/不确定）
6. trend_confidence: 趋势置信度 (0-1)"""

        try:
            response = await self.llm.generate_structured(
                prompt=prompt,
                response_model=CrossAnalysisResponse,
                system_prompt="你是一位专业的政治经济分析师，擅长综合多方观点并发现潜在的协同与冲突。"
            )

            return {
                "conflicts": self._format_conflicts(response.conflicts),
                "synergies": self._format_synergies(response.synergies),
                "agreements": response.agreements,
                "consensus": response.consensus,
                "key_tensions": self._identify_key_tensions_from_llm(response),
                "overall_trend": response.overall_trend,
                "trend_confidence": response.trend_confidence
            }

        except Exception as e:
            print(f"LLM cross analysis failed: {e}")
            # 回退到基于规则的交叉分析
            return await self._rule_based_cross_analysis(event, results)

    def _format_conflicts(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化冲突信息"""
        formatted = []
        for c in conflicts:
            if isinstance(c, dict):
                formatted.append({
                    "type": f"{c.get('role1', 'A')}-{c.get('role2', 'B')}",
                    "description": c.get("point", "观点冲突"),
                    "severity": c.get("severity", "中")
                })
            else:
                formatted.append({
                    "type": "观点冲突",
                    "description": str(c),
                    "severity": "中"
                })
        return formatted

    def _format_synergies(self, synergies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化协同信息"""
        formatted = []
        for s in synergies:
            if isinstance(s, dict):
                formatted.append({
                    "type": "-".join(s.get("roles", [])) if isinstance(s.get("roles"), list) else "多方协同",
                    "description": s.get("description", "观点协同"),
                    "potential": s.get("potential", "正向")
                })
            else:
                formatted.append({
                    "type": "多方协同",
                    "description": str(s),
                    "potential": "正向"
                })
        return formatted

    def _identify_key_tensions_from_llm(self, response: CrossAnalysisResponse) -> List[Dict]:
        """从LLM响应中识别关键张力"""
        tensions = []

        for conflict in response.conflicts:
            if isinstance(conflict, dict):
                severity = conflict.get("severity", "中")
                if severity in ["高", "high"]:
                    tensions.append({
                        "title": f"{conflict.get('role1', 'A')} - {conflict.get('role2', 'B')}",
                        "description": conflict.get("point", ""),
                        "resolution": "需要进一步协调"
                    })

        return tensions

    async def _rule_based_cross_analysis(
        self,
        event: Dict[str, Any],
        results: List[RoleAnalysisResult]
    ) -> Dict[str, Any]:
        """基于规则的交叉分析（回退方案）"""

        # 按类别收集反应
        category_reactions = {}
        for r in results:
            if r.category not in category_reactions:
                category_reactions[r.category] = []
            category_reactions[r.category].append(r)

        # 分析潜在冲突
        conflicts = []

        # 政府 vs 民众
        if "government" in category_reactions and "public" in category_reactions:
            conflicts.append({
                "type": "政府-民众",
                "description": "政府决策可能与民众期望产生张力",
                "severity": "中等"
            })

        # 投资者 vs 政府
        if "investor" in category_reactions and "government" in category_reactions:
            conflicts.append({
                "type": "投资者-政府",
                "description": "政府政策可能与投资者利益产生冲突",
                "severity": "中等"
            })

        # 媒体 vs 政府
        if "media" in category_reactions and "government" in category_reactions:
            conflicts.append({
                "type": "媒体-政府",
                "description": "媒体报道可能影响政府决策或被政府管控",
                "severity": "低"
            })

        # 分析协同
        synergies = []

        # 企业与投资者
        if "corporation" in category_reactions and "investor" in category_reactions:
            synergies.append({
                "type": "企业-投资者",
                "description": "企业决策与投资者利益高度相关",
                "potential": "正向"
            })

        return {
            "conflicts": conflicts,
            "synergies": synergies,
            "agreements": [],
            "consensus": self._find_consensus(results),
            "key_tensions": self._identify_key_tensions(results),
            "overall_trend": "平稳",
            "trend_confidence": 0.5
        }

    def _identify_key_tensions(self, results: List[RoleAnalysisResult]) -> List[Dict]:
        """识别关键张力"""
        tensions = []

        # 检查是否有相反的反应
        categories = set(r.category for r in results)

        if RoleCategory.GOVERNMENT.value in categories and RoleCategory.PUBLIC.value in categories:
            tensions.append({
                "title": "治理张力",
                "description": "政府稳定导向 vs 民众诉求",
                "resolution": "需要政策平衡"
            })

        if RoleCategory.INVESTOR.value in categories and RoleCategory.GOVERNMENT.value in categories:
            tensions.append({
                "title": "政策张力",
                "description": "政府调控 vs 投资者利益",
                "resolution": "市场适应性调整"
            })

        return tensions

    def _find_consensus(self, results: List[RoleAnalysisResult]) -> List[str]:
        """寻找共识点"""
        consensus = []

        # 简单检查 - 实际可以更复杂
        all_reactions = [r.reaction.get("action", "") for r in results]

        if any("关注" in a for a in all_reactions):
            consensus.append("各方都在关注事件发展")

        if any("评估" in a for a in all_reactions):
            consensus.append("各方都需要时间评估影响")

        return consensus

    async def _synthesize(
        self,
        event: Dict[str, Any],
        results: List[RoleAnalysisResult],
        cross_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合推演 - 生成最终预测"""

        # 计算整体置信度
        confidences = [r.confidence for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # 确定主导趋势
        overall_trend = cross_analysis.get("overall_trend", "平稳")
        trend_confidence = cross_analysis.get("trend_confidence", avg_confidence)

        # 生成综合时间线
        all_timeline = []
        for r in results:
            all_timeline.extend(r.timeline)

        # 去重并排序
        timeline_by_time = {}
        for t in all_timeline:
            time_key = t.get("time", "未知")
            if time_key not in timeline_by_time:
                timeline_by_time[time_key] = t

        final_timeline = list(timeline_by_time.values())[:5]

        return {
            "overall_trend": overall_trend,
            "confidence": round(trend_confidence, 2),
            "summary": self._generate_summary(event, results, overall_trend),
            "key_insights": self._extract_key_insights(results, cross_analysis),
            "timeline": final_timeline,
            "recommended_actions": self._generate_recommendations(results, cross_analysis)
        }

    def _generate_summary(
        self,
        event: Dict[str, Any],
        results: List[RoleAnalysisResult],
        trend: str
    ) -> str:
        """生成综合摘要"""
        categories = set(r.category for r in results)
        category_names = {
            "government": "政府",
            "corporation": "企业",
            "public": "民众",
            "media": "媒体",
            "investor": "投资者"
        }

        involved = [category_names.get(c, c) for c in categories]

        return f"""综合{len(results)}个角色视角的分析：

事件「{event.get('title', 'N/A')}」引发了多方关注。

参与分析的角色类别包括：{', '.join(involved)}。

从各角色反应来看，预计整体趋势{trend}。各方的关注点主要集中在事件的影响和应对策略上。

详细的角色反应和交叉分析见下文。"""

    def _extract_key_insights(
        self,
        results: List[RoleAnalysisResult],
        cross_analysis: Dict[str, Any]
    ) -> List[str]:
        """提取关键洞察"""
        insights = []

        # 从张力中提取洞察
        for tension in cross_analysis.get("key_tensions", []):
            insights.append(f"关键张力: {tension.get('title')} - {tension.get('description')}")

        # 从共识中提取
        for consensus in cross_analysis.get("consensus", []):
            insights.append(f"共识点: {consensus}")

        return insights[:5]

    def _generate_recommendations(
        self,
        results: List[RoleAnalysisResult],
        cross_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成建议"""
        recommendations = []

        # 基于张力给出建议
        for tension in cross_analysis.get("key_tensions", []):
            recommendations.append(f"关注{tension.get('title')}，{tension.get('resolution')}")

        # 基于共识给出建议
        for consensus in cross_analysis.get("consensus", []):
            recommendations.append(f"利用共识: {consensus}")

        return recommendations[:3]

    # ============ P0阶段新增方法：缓存和模式匹配管理 ============

    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return await self.cache.get_stats()

    async def clear_cache(self, expired_only: bool = False) -> Dict[str, str]:
        """清空缓存"""
        await self.cache.clear(expired_only=expired_only)
        return {"status": "success", "message": f"缓存已{'清除过期条目' if expired_only else '全部清空'}"}

    async def get_pattern_stats(self) -> Dict[str, Any]:
        """获取模式匹配统计信息"""
        return await self.pattern_matcher.get_pattern_statistics()

    async def find_similar_patterns(
        self,
        event: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        查找相似的历史模式

        Args:
            event: 事件信息
            top_k: 返回最相似的K个结果
            min_similarity: 最小相似度阈值

        Returns:
            相似模式列表
        """
        return await self.pattern_matcher.find_similar_events(
            event,
            top_k=top_k,
            min_similarity=min_similarity
        )

    async def analyze_with_pattern_reference(
        self,
        event: Dict[str, Any],
        role_ids: List[str],
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """
        带历史模式参考的分析

        在分析时参考相似历史事件的预测结果，
        提供更全面的上下文。

        Args:
            event: 事件信息
            role_ids: 角色ID列表
            depth: 分析深度

        Returns:
            包含分析和历史参考的结果
        """
        # 查找相似事件
        similar_patterns = await self.pattern_matcher.find_similar_events(
            event,
            top_k=5,
            min_similarity=0.3
        )

        # 执行标准分析
        analysis_result = await self.analyze_with_roles(
            event,
            role_ids,
            depth,
            use_cache=True,
            find_similar=True
        )

        # 如果有高相似度的历史事件，提供参考建议
        historical_insights = []
        if similar_patterns:
            for pattern in similar_patterns[:3]:
                pred = pattern.get("prediction", {})
                if pred:
                    historical_insights.append({
                        "similar_event": pattern.get("title"),
                        "similarity": pattern.get("similarity_score"),
                        "historical_trend": pred.get("trend"),
                        "historical_confidence": pred.get("confidence"),
                        "insight": f"历史上相似事件趋势为{pred.get('trend')}，置信度{pred.get('confidence', 0)*100:.0f}%"
                    })

        analysis_result["historical_reference"] = {
            "similar_patterns_count": len(similar_patterns),
            "insights": historical_insights,
            "recommendation": self._generate_historical_recommendation(historical_insights) if historical_insights else None
        }

        return analysis_result

    def _generate_historical_recommendation(
        self,
        historical_insights: List[Dict[str, Any]]
    ) -> Optional[str]:
        """基于历史参考生成建议"""
        if not historical_insights:
            return None

        # 统计历史趋势
        trends = {}
        for insight in historical_insights:
            trend = insight.get("historical_trend", "N/A")
            similarity = insight.get("similarity", 0)
            # 加权统计
            trends[trend] = trends.get(trend, 0) + similarity

        if trends:
            dominant_trend = max(trends, key=trends.get)
            return f"基于{len(historical_insights)}个相似历史事件，主要趋势为{dominant_trend}"

        return None


# 全局服务实例
multi_agent_service = MultiAgentAnalysisService()
