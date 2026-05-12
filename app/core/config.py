# EventPredictor 核心配置模块
import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """LLM配置"""
    model_config = SettingsConfigDict(env_prefix="")
    provider: str = Field(default="minimax", description="LLM提供商: anthropic | openai | minimax | mock")
    model: str = Field(default="minimax-cn/MiniMax-M2.1", description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")


class WorldMonitorConfig(BaseSettings):
    """WorldMonitor数据源配置"""
    model_config = SettingsConfigDict(env_prefix="WM_")
    # 旧配置（保留兼容）
    rss_endpoint: str = "https://worldmonitor/api/rss-proxy"
    polymarket_endpoint: str = "https://worldmonitor/api/polymarket"
    telegram_endpoint: str = "https://worldmonitor/api/telegram-feed"
    # 新配置 - 本地API
    local_api_url: str = "http://localhost:46123"
    api_token: Optional[str] = None
    timeout: int = 30


class APIConfig(BaseSettings):
    """API服务配置"""
    model_config = SettingsConfigDict(env_prefix="API_")
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    title: str = "EventPredictor API"
    version: str = "1.0.0"
    description: str = "全球局势推演决策系统"


class AgentConfig(BaseSettings):
    """Agent配置"""
    model_config = SettingsConfigDict(extra="allow")
    info_collector_prompt: str = "你是一个信息收集专家。根据给定的事件，收集相关的背景信息、来源可靠性分析、以及可能影响预测的关键信息。"
    analyzer_prompt: str = "你是一个深度分析专家。根据收集的信息，分析事件的影响范围、持续时间、关键因素和市场情绪。"
    predictor_prompt: str = "你是一个趋势预测专家。根据分析结果，给出未来走势预测，包含趋势方向、置信度和影响因素。"


class PredictionConfig(BaseSettings):
    """预测配置"""
    default_time_horizon: str = "Short-term (1-7 days)"
    min_confidence: float = 0.5
    cache_ttl: int = 3600


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    model_config = SettingsConfigDict(env_prefix="DB_")
    path: str = "data/eventpredictor.db"
    echo: bool = False


class AuthConfig(BaseSettings):
    """认证配置"""
    model_config = SettingsConfigDict(env_prefix="AUTH_")
    secret_key: str = "change-me-in-production-use-a-strong-random-key"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12


class RealtimeConfig(BaseSettings):
    """实时数据配置"""
    model_config = SettingsConfigDict(env_prefix="REALTIME_")
    # NOTE: Attribute names differ from YAML keys intentionally.
    # YAML key `realtime.news_fetcher.enabled` is mapped manually
    # in load_from_yaml() to this attribute. See that method for details.
    news_fetcher_enabled: bool = True
    rss_interval: int = 300
    worldmonitor_interval: int = 600
    max_seen_events: int = 10000
    sse_heartbeat: int = 30
    sse_max_connections: int = 50


class BacktestConfig(BaseSettings):
    """回测配置"""
    enabled: bool = True
    historical_data_path: str = "data/historical_events.json"
    auto_resolve_interval: int = 3600


class OptionalSourcesConfig(BaseSettings):
    """可选数据源配置"""
    class GdeltConfig(BaseSettings):
        enabled: bool = False
        timeout: int = 30
    class AcledConfig(BaseSettings):
        enabled: bool = False
        api_key: Optional[str] = None
        timeout: int = 30
    gdelt: GdeltConfig = Field(default_factory=GdeltConfig)
    acled: AcledConfig = Field(default_factory=AcledConfig)


class Config(BaseSettings):
    """全局配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    worldmonitor: WorldMonitorConfig = Field(default_factory=WorldMonitorConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    prediction: PredictionConfig = Field(default_factory=PredictionConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    realtime: RealtimeConfig = Field(default_factory=RealtimeConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    optional_sources: OptionalSourcesConfig = Field(default_factory=OptionalSourcesConfig)

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

        # 解析 realtime 配置节
        rt_data = data.get("realtime", {})
        nf_data = rt_data.get("news_fetcher", {})
        sse_data = rt_data.get("sse", {})

        # 解析 backtest 配置
        bt_data = data.get("backtest", {})

        # 解析 optional_sources 配置
        os_data = data.get("optional_sources", {})
        gdelt_data = os_data.get("gdelt", {})
        acled_data = os_data.get("acled", {})

        # 使用 model_construct 绕过 pydantic 验证，避免环境变量覆盖问题
        return cls.model_construct(
            llm=LLMConfig(**data.get("llm", {})),
            worldmonitor=WorldMonitorConfig(**data.get("worldmonitor", {})),
            api=APIConfig(**data.get("api", {})),
            agents=AgentConfig(**data.get("agents", {})),
            prediction=PredictionConfig(**data.get("prediction", {})),
            database=DatabaseConfig(**data.get("database", {})),
            auth=AuthConfig(**data.get("auth", {})),
            realtime=RealtimeConfig(
                news_fetcher_enabled=nf_data.get("enabled", True),
                rss_interval=nf_data.get("rss_interval", 300),
                worldmonitor_interval=nf_data.get("worldmonitor_interval", 600),
                max_seen_events=nf_data.get("max_seen_events", 10000),
                sse_heartbeat=sse_data.get("heartbeat_interval", 30),
                sse_max_connections=sse_data.get("max_connections", 50),
            ),
            backtest=BacktestConfig(
                enabled=bt_data.get("enabled", True),
                historical_data_path=bt_data.get("historical_data_path", "data/historical_events.json"),
                auto_resolve_interval=bt_data.get("auto_resolve_interval", 3600),
            ),
            optional_sources=OptionalSourcesConfig(
                gdelt=OptionalSourcesConfig.GdeltConfig(
                    enabled=gdelt_data.get("enabled", False),
                    timeout=gdelt_data.get("timeout", 30),
                ),
                acled=OptionalSourcesConfig.AcledConfig(
                    enabled=acled_data.get("enabled", False),
                    api_key=acled_data.get("api_key"),
                    timeout=acled_data.get("timeout", 30),
                ),
            )
        )


# 全局配置实例
config = Config.load_from_yaml()
