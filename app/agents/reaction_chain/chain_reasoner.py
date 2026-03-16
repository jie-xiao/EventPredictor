# 链式推理器 - 执行反应链的推理逻辑
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

from app.services.llm_service import llm_service


@dataclass
class ReasoningContext:
    """推理上下文"""
    event: Dict[str, Any]
    round_number: int
    role_id: str
    role_name: str
    previous_reactions: Dict[str, Dict[str, Any]]
    influence_hints: List[Dict[str, Any]]  # 来自其他角色的影响提示
    convergence_hints: Optional[Dict[str, Any]] = None  # 收敛提示


class ChainReasoner:
    """
    链式推理器

    负责执行反应链的推理逻辑，包括：
    1. 构建推理提示
    2. 调用LLM进行推理
    3. 解析推理结果
    4. 生成推理链
    """

    def __init__(self):
        self.llm = llm_service

    async def reason(
        self,
        context: ReasoningContext,
        role_system_prompt: str
    ) -> Dict[str, Any]:
        """
        执行推理

        Args:
            context: 推理上下文
            role_system_prompt: 角色的系统提示词

        Returns:
            推理结果
        """
        # 构建推理提示
        prompt = self._build_reasoning_prompt(context)

        try:
            # 调用LLM进行推理
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=role_system_prompt
            )

            # 解析结果
            result = self._parse_reasoning_result(response, context)

            return result

        except Exception as e:
            print(f"Reasoning error for {context.role_id}: {e}")
            return self._fallback_reasoning(context)

    def _build_reasoning_prompt(self, context: ReasoningContext) -> str:
        """构建推理提示"""
        event = context.event

        # 基础信息
        prompt_parts = [
            f"""作为{context.role_name}，分析以下事件并给出你的反应。

## 事件信息
- 标题：{event.get('title', 'N/A')}
- 描述：{event.get('description', 'N/A')}
- 类别：{event.get('category', 'N/A')}
- 重要性：{event.get('importance', 3)}/5

## 当前轮次
这是第 {context.round_number} 轮分析。"""
        ]

        # 第一轮：独立分析
        if context.round_number == 1:
            prompt_parts.append("""
## 任务
请基于你的角色特点，对事件做出独立分析和反应。暂时不需要考虑其他方的看法。

请以JSON格式输出你的反应：
```json
{
    "emotion": "你的情绪反应",
    "action": "你计划采取的行动",
    "statement": "你发表的官方声明",
    "confidence": 0.0-1.0之间的置信度,
    "reasoning": "你的推理过程简述"
}
```

只输出JSON，不要其他内容。""")
        else:
            # 后续轮次：考虑其他方反应
            prompt_parts.append("""
## 其他相关方的反应
以下是上一轮其他相关方的反应：""")

            for role_id, reaction in context.previous_reactions.items():
                if role_id == context.role_id:
                    continue
                role_name = reaction.get("role_name", role_id)
                prompt_parts.append(f"""
### {role_name}
- 情绪：{reaction.get('emotion', 'N/A')}
- 行动：{reaction.get('action', 'N/A')}
- 声明：{reaction.get('statement', 'N/A')}
- 置信度：{reaction.get('confidence', 0.5):.1%}""")

            # 添加影响提示
            if context.influence_hints:
                prompt_parts.append("""
## 影响分析
以下是你可能受到的影响：""")
                for hint in context.influence_hints:
                    prompt_parts.append(
                        f"- {hint['source']}对你的影响：{hint['type']}性，强度{hint['strength']:.1%}"
                    )

            # 添加收敛提示
            if context.convergence_hints:
                prompt_parts.append(f"""
## 收敛状态
当前整体收敛分数：{context.convergence_hints.get('convergence_score', 0):.1%}
{context.convergence_hints.get('recommendation', '')}""")

            prompt_parts.append("""
## 任务
基于其他相关方的反应，调整你的立场和行动。请说明你是否被其他方影响，以及如何影响。

请以JSON格式输出你的反应：
```json
{
    "emotion": "你的情绪反应（可能有变化）",
    "action": "你调整后的行动",
    "statement": "你更新的声明",
    "stance_change": "相比上一轮的立场变化说明",
    "confidence": 0.0-1.0之间的置信度,
    "reasoning": "你调整立场的推理过程",
    "influenced_by": ["影响你的角色ID列表"]
}
```

只输出JSON，不要其他内容。""")

        return "\n".join(prompt_parts)

    def _parse_reasoning_result(
        self,
        response: str,
        context: ReasoningContext
    ) -> Dict[str, Any]:
        """解析推理结果"""
        import json
        import re

        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())

                # 确保必要字段存在
                return {
                    "emotion": result.get("emotion", "关注"),
                    "action": result.get("action", "评估形势"),
                    "statement": result.get("statement", ""),
                    "stance_change": result.get("stance_change", ""),
                    "confidence": min(max(float(result.get("confidence", 0.7)), 0.0), 1.0),
                    "reasoning": result.get("reasoning", ""),
                    "influenced_by": result.get("influenced_by", []),
                    "role_id": context.role_id,
                    "role_name": context.role_name,
                    "round_number": context.round_number
                }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")

        # 解析失败，使用fallback
        return self._fallback_reasoning(context)

    def _fallback_reasoning(self, context: ReasoningContext) -> Dict[str, Any]:
        """回退推理"""
        importance = context.event.get("importance", 3)

        base_emotions = {
            1: "轻微关注",
            2: "一般关注",
            3: "关注",
            4: "高度关注",
            5: "极度关注"
        }

        base_actions = {
            1: "留意事态发展",
            2: "关注并评估",
            3: "积极评估并准备应对",
            4: "紧急评估并制定应对方案",
            5: "立即采取行动"
        }

        emotion = base_emotions.get(importance, "关注")
        action = base_actions.get(importance, "评估形势")
        stance_change = ""

        if context.round_number > 1 and context.previous_reactions:
            # 后续轮次，考虑影响
            influenced_by = [
                rid for rid in context.previous_reactions.keys()
                if rid != context.role_id
            ]
            if influenced_by:
                stance_change = f"基于其他{len(influenced_by)}方的反应，调整了应对策略"
        else:
            influenced_by = []

        return {
            "emotion": emotion,
            "action": action,
            "statement": f"作为{context.role_name}，我们正在{action}。",
            "stance_change": stance_change,
            "confidence": 0.6 + (importance * 0.05),
            "reasoning": f"基于事件重要性({importance}/5)进行评估",
            "influenced_by": influenced_by,
            "role_id": context.role_id,
            "role_name": context.role_name,
            "round_number": context.round_number
        }

    async def batch_reason(
        self,
        contexts: List[ReasoningContext],
        role_prompts: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        批量推理（并行执行）
        """
        tasks = [
            self.reason(context, role_prompts.get(context.role_id, ""))
            for context in contexts
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤有效结果
        valid_results = []
        for r in results:
            if isinstance(r, dict):
                valid_results.append(r)
            elif isinstance(r, Exception):
                print(f"Batch reasoning error: {r}")

        return valid_results
