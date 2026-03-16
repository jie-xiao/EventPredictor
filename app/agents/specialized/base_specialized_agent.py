# 专业Agent基类
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class AgentAnalysisResult:
    """Agent分析结果"""
    agent_id: str
    agent_type: str
    agent_name: str

    # 核心分析
    key_findings: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)

    # 预测
    short_term_forecast: str = ""
    medium_term_forecast: str = ""
    long_term_forecast: str = ""

    # 建议
    recommendations: List[str] = field(default_factory=list)

    # 置信度和重要性
    confidence: float = 0.7
    importance_score: float = 0.5

    # 依赖的上下文
    context_used: List[str] = field(default_factory=list)

    # 与其他Agent的关系
    related_insights: Dict[str, str] = field(default_factory=dict)  # {agent_type: insight}

    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "key_findings": self.key_findings,
            "risk_assessment": self.risk_assessment,
            "opportunities": self.opportunities,
            "threats": self.threats,
            "short_term_forecast": self.short_term_forecast,
            "medium_term_forecast": self.medium_term_forecast,
            "long_term_forecast": self.long_term_forecast,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "importance_score": self.importance_score,
            "context_used": self.context_used,
            "related_insights": self.related_insights,
            "timestamp": self.timestamp
        }


@dataclass
class AgentMessage:
    """Agent间通信消息"""
    sender_id: str
    sender_type: str
    receiver_id: Optional[str]  # None表示广播
    message_type: str  # "insight", "question", "request", "response"
    content: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseSpecializedAgent(ABC):
    """
    专业Agent基类

    所有专业Agent都继承此类，实现特定的分析逻辑
    """

    def __init__(self, agent_type: str, agent_name: str, description: str):
        self.agent_id = f"{agent_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.description = description

        # 分析上下文
        self.context: Dict[str, Any] = {}

        # 收到的消息
        self.inbox: List[AgentMessage] = []

        # 其他Agent的分析结果
        self.other_agent_insights: Dict[str, AgentAnalysisResult] = {}

        # LLM服务
        from app.services.llm_service import llm_service
        self.llm = llm_service

    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取Agent的系统提示词"""
        pass

    @abstractmethod
    def get_analysis_framework(self) -> Dict[str, Any]:
        """获取分析框架"""
        pass

    @abstractmethod
    async def analyze(self, event: Dict[str, Any]) -> AgentAnalysisResult:
        """
        执行分析

        Args:
            event: 事件数据

        Returns:
            分析结果
        """
        pass

    def set_context(self, context: Dict[str, Any]):
        """设置分析上下文"""
        self.context = context

    def receive_insight(self, from_agent: str, result: AgentAnalysisResult):
        """接收其他Agent的洞察"""
        self.other_agent_insights[from_agent] = result

    def receive_message(self, message: AgentMessage):
        """接收消息"""
        self.inbox.append(message)

    def send_message(
        self,
        receiver_id: Optional[str],
        message_type: str,
        content: str,
        details: Dict[str, Any] = None
    ) -> AgentMessage:
        """发送消息"""
        message = AgentMessage(
            sender_id=self.agent_id,
            sender_type=self.agent_type,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            details=details or {}
        )
        return message

    def build_analysis_prompt(self, event: Dict[str, Any]) -> str:
        """构建分析提示词"""
        framework = self.get_analysis_framework()

        prompt = f"""作为{self.agent_name}，分析以下事件：

## 事件信息
- 标题：{event.get('title', 'N/A')}
- 描述：{event.get('description', 'N/A')}
- 类别：{event.get('category', 'N/A')}
- 重要性：{event.get('importance', 3)}/5

## 分析框架
"""
        for key, value in framework.items():
            prompt += f"- {key}: {value}\n"

        # 添加其他Agent的洞察
        if self.other_agent_insights:
            prompt += "\n## 其他分析师的洞察\n"
            for agent_type, result in self.other_agent_insights.items():
                prompt += f"- {result.agent_name}: {', '.join(result.key_findings[:3])}\n"

        prompt += f"""
## 请提供以下分析（JSON格式）：
{{
    "key_findings": ["关键发现1", "关键发现2", ...],
    "risk_assessment": {{
        "overall_risk": "高/中/低",
        "key_risks": ["风险1", "风险2"],
        "risk_level": 0.0-1.0
    }},
    "opportunities": ["机会1", "机会2"],
    "threats": ["威胁1", "威胁2"],
    "short_term_forecast": "短期预测（1-7天）",
    "medium_term_forecast": "中期预测（1-4周）",
    "long_term_forecast": "长期预测（1-6月）",
    "recommendations": ["建议1", "建议2"],
    "confidence": 0.0-1.0
}}

只输出JSON，不要其他内容。"""

        return prompt

    async def llm_analyze(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM进行分析"""
        import json
        import re

        prompt = self.build_analysis_prompt(event)
        system_prompt = self.get_system_prompt()

        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt
            )

            # 解析JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            print(f"LLM analysis failed for {self.agent_type}: {e}")

        # 返回默认结果
        return self._get_default_analysis(event)

    def _get_default_analysis(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认分析结果"""
        importance = event.get("importance", 3)

        return {
            "key_findings": [
                f"事件重要性评级为{importance}/5",
                f"需要从{self.agent_name}角度深入分析"
            ],
            "risk_assessment": {
                "overall_risk": "中等" if importance >= 3 else "低",
                "key_risks": ["需要进一步评估"],
                "risk_level": 0.4 + importance * 0.1
            },
            "opportunities": ["待分析"],
            "threats": ["待评估"],
            "short_term_forecast": "需要更多信息进行预测",
            "medium_term_forecast": "持续关注事态发展",
            "long_term_forecast": "取决于多方因素演变",
            "recommendations": [
                f"建议从{self.agent_name}专业角度持续跟踪"
            ],
            "confidence": 0.6
        }
