# EventPredictor 核心配置模块
import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    """LLM配置"""
    provider: str = Field(default="minimax", description="LLM提供商: anthropic | openai | minimax | mock")
    model: str = Field(default="minimax-cn/MiniMax-M2.1", description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")
    
    class Config:
        env_prefix = ""


class WorldMonitorConfig(BaseSettings):
    """WorldMonitor数据源配置"""
    # 旧配置（保留兼容）
    rss_endpoint: str = "https://worldmonitor/api/rss-proxy"
    polymarket_endpoint: str = "https://worldmonitor/api/polymarket"
    telegram_endpoint: str = "https://worldmonitor/api/telegram-feed"
    # 新配置 - 本地API
    local_api_url: str = "http://localhost:46123"
    api_token: Optional[str] = None
    timeout: int = 30
    
    class Config:
        env_prefix = "WM_"


class APIConfig(BaseSettings):
    """API服务配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    title: str = "EventPredictor API"
    version: str = "1.0.0"
    description: str = "全球局势推演决策系统"
    
    class Config:
        env_prefix = "API_"


class AgentConfig(BaseSettings):
    """Agent配置"""
    info_collector_prompt: str = "你是一个信息收集专家。根据给定的事件，收集相关的背景信息、来源可靠性分析、以及可能影响预测的关键信息。"
    analyzer_prompt: str = "你是一个深度分析专家。根据收集的信息，分析事件的影响范围、持续时间、关键因素和市场情绪。"
    predictor_prompt: str = "你是一个趋势预测专家。根据分析结果，给出未来走势预测，包含趋势方向、置信度和影响因素。"
    
    class Config:
        extra = "allow"  # 允许额外字段


class PredictionConfig(BaseSettings):
    """预测配置"""
    default_time_horizon: str = "Short-term (1-7 days)"
    min_confidence: float = 0.5
    cache_ttl: int = 3600


class Config(BaseSettings):
    """全局配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    worldmonitor: WorldMonitorConfig = Field(default_factory=WorldMonitorConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    prediction: PredictionConfig = Field(default_factory=PredictionConfig)
    
    @classmethod
    def load_from_yaml(cls, config_path: Optional[str] = None) -> "Config":
        """从YAML文件加载配置"""
        if config_path is None:
            # 项目根目录是 config.yaml 所在的目录
            # __file__ = app/core/config.py, parent.parent.parent = 项目根目录
            config_path = os.path.join(
                Path(__file__).parent.parent.parent,
                "config.yaml"
            )
        
        if not os.path.exists(config_path):
            return cls()
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # 使用 model_construct 绕过 pydantic 验证，避免环境变量覆盖问题
        return cls.model_construct(
            llm=LLMConfig(**data.get("llm", {})),
            worldmonitor=WorldMonitorConfig(**data.get("worldmonitor", {})),
            api=APIConfig(**data.get("api", {})),
            agents=AgentConfig(**data.get("agents", {})),
            prediction=PredictionConfig(**data.get("prediction", {}))
        )


# 全局配置实例
config = Config.load_from_yaml()
