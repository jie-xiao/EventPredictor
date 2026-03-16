# 专业Agent模块
from .geopolitical_agent import GeopoliticalAgent
from .economic_agent import EconomicAgent
from .military_agent import MilitaryAgent
from .social_agent import SocialAgent
from .technology_agent import TechnologyAgent
from .base_specialized_agent import BaseSpecializedAgent, AgentAnalysisResult

# Agent注册表
SPECIALIZED_AGENTS = {
    "geopolitical": GeopoliticalAgent,
    "economic": EconomicAgent,
    "military": MilitaryAgent,
    "social": SocialAgent,
    "technology": TechnologyAgent,
}

def get_agent(agent_type: str) -> BaseSpecializedAgent:
    """获取指定类型的Agent实例"""
    agent_class = SPECIALIZED_AGENTS.get(agent_type)
    if agent_class:
        return agent_class()
    return None

def get_all_agents() -> dict:
    """获取所有Agent实例"""
    return {agent_type: agent_class() for agent_type, agent_class in SPECIALIZED_AGENTS.items()}

__all__ = [
    'BaseSpecializedAgent',
    'AgentAnalysisResult',
    'GeopoliticalAgent',
    'EconomicAgent',
    'MilitaryAgent',
    'SocialAgent',
    'TechnologyAgent',
    'SPECIALIZED_AGENTS',
    'get_agent',
    'get_all_agents',
]
