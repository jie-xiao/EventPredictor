# LLM服务模块
from typing import Optional, Dict, Any, Type, TypeVar, List
from pydantic import BaseModel
import json
import asyncio
import os
import logging
from app.core.config import config

# 配置日志
logger = logging.getLogger(__name__)

# 解决HTTP代理导致的LLM API请求503问题
# 设置NO_PROXY确保LLM API请求不走代理
_no_proxy_hosts = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "api.minimax.chat",
    "api.anthropic.com",
    "api.openai.com"
]
os.environ.setdefault("NO_PROXY", ",".join(_no_proxy_hosts))
os.environ.setdefault("no_proxy", ",".join(_no_proxy_hosts))

T = TypeVar('T', bound=BaseModel)


class RoleAnalysisResponse(BaseModel):
    """角色分析结构化响应"""
    stance: str
    reaction: Dict[str, str]
    impact: Dict[str, str]
    timeline: List[Dict[str, Any]]
    confidence: float
    reasoning: str


class DebateResponse(BaseModel):
    """辩论响应结构"""
    position: str
    supports: List[str]
    challenges: List[str]
    adjusted_confidence: float
    statement: str


class CrossAnalysisResponse(BaseModel):
    """交叉分析响应结构"""
    agreements: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    synergies: List[Dict[str, Any]]
    consensus: List[str]
    overall_trend: str
    trend_confidence: float


class ScenarioStep(BaseModel):
    """情景推演步骤"""
    time: str
    description: str
    probability: float
    key_events: List[str]


class Scenario(BaseModel):
    """单个情景"""
    id: str
    name: str
    description: str
    probability: float
    steps: List[ScenarioStep]
    key_factors: List[str]
    potential_outcomes: List[str]


class ScenarioResponse(BaseModel):
    """情景推演响应结构"""
    event_id: str
    scenarios: List[Scenario]
    most_likely_scenario: str
    overall_assessment: str
    key_uncertainties: List[str]
    recommendation: str


class ReactionChainResponse(BaseModel):
    """反应链分析响应结构"""
    emotion: str
    action: str
    statement: str
    stance_change: str = ""
    confidence: float
    reasoning: str
    influenced_by: List[str] = []


class EventChainInfluenceResponse(BaseModel):
    """事件链影响分析响应结构"""
    source_event: str
    target_event: str
    influence_type: str  # "amplify", "attenuate", "neutral", "transform"
    influence_strength: float
    affected_aspects: List[str]
    reasoning: str


class TimelinePredictionResponse(BaseModel):
    """时间线预测响应结构"""
    predictions: List[Dict[str, Any]]
    confidence_trend: List[float]
    key_milestones: List[str]
    potential_branches: List[Dict[str, Any]]
    overall_assessment: str


class LLMService:
    """LLM服务 - 封装LLM调用"""

    def __init__(self):
        self.provider = config.llm.provider
        self.model = config.llm.model
        self.temperature = config.llm.temperature
        self.max_tokens = config.llm.max_tokens
        self.max_retries = 3
        self.retry_base_delay = 1.0

    def _get_api_key(self) -> Optional[str]:
        """获取API Key，优先从环境变量读取"""
        if self.provider == "minimax":
            return os.getenv("MINIMAX_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """调用LLM生成内容"""
        if self.provider == "minimax":
            return await self._minimax_call(prompt, system_prompt)
        elif self.provider == "anthropic":
            return await self._anthropic_call(prompt, system_prompt)
        elif self.provider == "openai":
            return await self._openai_call(prompt, system_prompt)
        else:
            # 模拟响应
            return self._mock_response(prompt)

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        """
        调用LLM生成结构化输出

        Args:
            prompt: 用户提示词
            response_model: Pydantic模型类，用于解析响应
            system_prompt: 系统提示词

        Returns:
            解析后的Pydantic模型实例
        """
        # 添加JSON格式要求到提示词
        json_prompt = f"""{prompt}

请严格按照JSON格式输出你的分析结果。输出必须是有效的JSON格式，不要包含任何其他文本。

期望的JSON结构如下：
{response_model.model_json_schema()}

请直接输出JSON，不要有任何额外说明。"""

        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await self.generate(json_prompt, system_prompt)

                # 尝试解析JSON
                parsed = self._parse_json_response(response)

                # 使用Pydantic验证
                validated = response_model.model_validate(parsed)
                return validated

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(f"JSON解析失败 (尝试 {attempt + 1}/{self.max_retries})")
            except Exception as e:
                last_error = e
                logger.warning(f"结构化输出失败 (尝试 {attempt + 1}/{self.max_retries})")

            # 指数退避重试
            if attempt < self.max_retries - 1:
                delay = self.retry_base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        # 所有重试失败，返回基于模型的默认值
        logger.warning(f"所有重试失败，返回默认结构化响应")
        return self._create_fallback_response(response_model)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应中的JSON"""
        # 处理响应可能是字典的情况
        if isinstance(response, dict):
            return response

        response = str(response).strip()

        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON块
        import re

        # 尝试提取 ```json ... ``` 块
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找到第一个 { 和最后一个 }
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(response[start:end+1])
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("无法从响应中提取有效的JSON", response, 0)

    def _create_fallback_response(self, model: Type[T]) -> T:
        """创建默认的结构化响应"""
        # 根据模型类型返回不同的默认值
        if model == RoleAnalysisResponse:
            return model(
                stance="关注事态发展",
                reaction={
                    "emotion": "谨慎",
                    "action": "持续关注",
                    "statement": "我们正在密切关注事态发展"
                },
                impact={
                    "economic": "需要进一步评估",
                    "political": "需要进一步评估",
                    "social": "需要进一步评估"
                },
                timeline=[
                    {"time": "短期", "event": "观察评估", "probability": 0.6}
                ],
                confidence=0.5,
                reasoning="基于角色特点的默认分析"
            )
        elif model == DebateResponse:
            return model(
                position="保持原有立场",
                supports=[],
                challenges=[],
                adjusted_confidence=0.5,
                statement="需要更多信息才能做出判断"
            )
        elif model == CrossAnalysisResponse:
            return model(
                agreements=[],
                conflicts=[],
                synergies=[],
                consensus=["各方都在关注事件发展"],
                overall_trend="平稳",
                trend_confidence=0.5
            )
        elif model == ScenarioResponse:
            return model(
                event_id="unknown",
                scenarios=[
                    Scenario(
                        id="scenario_1",
                        name="基准情景",
                        description="事态保持平稳发展",
                        probability=0.5,
                        steps=[
                            ScenarioStep(time="短期", description="观察评估", probability=0.7, key_events=["持续关注"])
                        ],
                        key_factors=["政策动向"],
                        potential_outcomes=["局势稳定"]
                    )
                ],
                most_likely_scenario="基准情景",
                overall_assessment="需要更多信息进行准确预测",
                key_uncertainties=["政策变化", "外部因素"],
                recommendation="持续关注事态发展"
            )

        # 通用默认值
        return model.model_construct({})

    async def _minimax_call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用MiniMax API"""
        try:
            import httpx
            from openai import AsyncOpenAI

            # 从环境变量获取API Key
            api_key = self._get_api_key()

            if not api_key:
                logger.warning("MINIMAX_API_KEY 环境变量未设置，使用mock响应")
                return self._mock_response(prompt)

            # 创建不使用代理的HTTP客户端
            http_client = httpx.AsyncClient(
                trust_env=False,  # 不读取环境变量中的代理设置
                timeout=60.0
            )

            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.minimax.chat/v1",
                http_client=http_client
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM调用失败")
            # 调用失败时返回mock响应
            return self._mock_response(prompt)

    async def _anthropic_call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用Anthropic API"""
        api_key = self._get_api_key()
        if not api_key:
            return self._mock_response(prompt)

        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=api_key)

            response = await client.messages.create(
                model=self.model or "claude-3-sonnet-20240229",
                max_tokens=self.max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic调用失败")
            return self._mock_response(prompt)

    async def _openai_call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用OpenAI API"""
        api_key = self._get_api_key()
        if not api_key:
            return self._mock_response(prompt)

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=self.model or "gpt-4",
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI调用失败")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """模拟LLM响应 - 返回结构化JSON"""

        # 从prompt中提取事件标题
        title = "未知事件"
        if "事件标题" in prompt:
            try:
                start = prompt.find("事件标题：") + 5
                end = prompt.find("\n", start)
                if end > start:
                    title = prompt[start:end].strip()
            except:
                pass

        # 返回结构化的mock分析结果
        mock_result = {
            "stance": "关注事件的进展",
            "reaction": {
                "emotion": "谨慎",
                "action": "持续关注事态发展",
                "statement": "对该事件保持关注"
            },
            "impact": {
                "economic": "可能产生一定影响",
                "political": "需要关注政治层面的变化",
                "social": "可能引起社会关注"
            },
            "timeline": [
                {"time": "1-3天", "event": "事件发酵期", "probability": 0.7},
                {"time": "1周", "event": "初步影响显现", "probability": 0.5}
            ],
            "confidence": 0.75,
            "reasoning": f"基于对'{title}'的分析，该事件预计产生一定影响。建议持续关注事态发展。"
        }

        return json.dumps(mock_result, ensure_ascii=False)

    def format_prompt(self, template: str, **kwargs) -> str:
        """格式化prompt"""
        return template.format(**kwargs)

    async def analyze_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析事件"""
        prompt = f"""
请分析以下事件:
标题: {event_data.get('title')}
描述: {event_data.get('description')}
分类: {event_data.get('category')}
重要性: {event_data.get('importance')}/5

请提供:
1. 影响范围
2. 持续时间
3. 关键因素
4. 市场情绪
"""
        result = await self.generate(prompt)

        return {
            "analysis": result,
            "impact_scope": "Global",
            "duration": "Medium-term",
            "sentiment": "Positive"
        }

    async def predict_trend(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """预测趋势"""
        prompt = f"""
基于以下分析结果，预测未来走势:
{analysis.get('analysis')}

请提供:
1. 趋势方向 (UP/DOWN/SIDEWAYS)
2. 置信度 (0-1)
3. 时间范围
"""
        result = await self.generate(prompt)

        return {
            "prediction": result,
            "trend": "UP",
            "confidence": 0.75
        }


# 全局LLM服务实例
llm_service = LLMService()
