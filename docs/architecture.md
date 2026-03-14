# 全球局势推演决策系统 - 架构设计

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        EventPredictor                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   FastAPI    │    │   LangChain  │    │   Config     │      │
│  │   Server     │◄──►│   Agents     │◄──►│   Manager    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                                  │
│         ▼                    ▼                                  │
│  ┌──────────────┐    ┌──────────────┐                         │
│  │   REST API   │    │  Agent Core  │                         │
│  │   Layer      │    │              │                         │
│  └──────────────┘    └──────────────┘                         │
│         │                    │                                  │
│         ▼                    ▼                                  │
│  ┌──────────────────────────────────────────┐                  │
│  │              Agent Pipeline               │                  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐     │                  │
│  │  │ Info    │ │Analysis │ │Predict │     │                  │
│  │  │ Collector│ │ Agent   │ │ Agent  │     │                  │
│  │  └─────────┘ └─────────┘ └─────────┘     │                  │
│  └──────────────────────────────────────────┘                  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────┐                  │
│  │           Data Sources (WorldMonitor)     │                  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐        │                  │
│  │  │  RSS   │ │Polymar-│ │Telegram│        │                  │
│  │  │ Feed   │ │ ket    │ │ Feed   │        │                  │
│  │  └────────┘ └────────┘ └────────┘        │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 核心模块设计

### 2.1 API层 (api/)

```
api/
├── routes/
│   ├── events.py      # 事件管理接口
│   ├── predict.py     # 预测接口
│   └── health.py      # 健康检查
├── models/
│   ├── request.py     # 请求模型
│   └── response.py   # 响应模型
└── dependencies.py    # 依赖注入
```

### 2.2 Agent层 (agents/)

```
agents/
├── base.py            # Agent基类
├── info_collector.py  # 信息收集Agent
├── analyzer.py        # 深度分析Agent
├── predictor.py       # 趋势预测Agent
└── pipeline.py        # Agent编排
```

### 2.3 服务层 (services/)

```
services/
├── llm_service.py     # LLM调用服务
├── worldmonitor.py    # WorldMonitor数据接入
└── prediction_service.py  # 预测业务逻辑
```

## 3. 数据模型

### 3.1 Event (事件)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | str | 事件唯一标识 |
| title | str | 事件标题 |
| description | str | 事件描述 |
| source | str | 来源 |
| timestamp | datetime | 时间戳 |
| category | str | 分类 |
| importance | int | 重要性 1-5 |

### 3.2 Prediction (预测结果)

| 字段 | 类型 | 描述 |
|------|------|------|
| trend | Enum | UP/DOWN/SIDEWAYS/UNCERTAIN |
| confidence | float | 置信度 0-1 |
| reasoning | str | 推理过程 |
| time_horizon | str | 时间范围 |
| factors | List[str] | 影响因素 |

### 3.3 CollectedInfo (收集信息)

| 字段 | 类型 | 描述 |
|------|------|------|
| basic_info | Dict | 基本信息 |
| related_events | List | 相关事件 |
| market_data | Dict | 市场数据 |

### 3.4 Analysis (分析结果)

| 字段 | 类型 | 描述 |
|------|------|------|
| impact_scope | str | 影响范围 |
| duration | str | 持续时间 |
| key_factors | List[str] | 关键因素 |
| sentiment | str | 市场情绪 |

## 4. Agent Pipeline设计

```python
def run_pipeline(event: Event) -> Prediction:
    # Step 1: 信息收集
    collected = info_collector.run(event)
    
    # Step 2: 深度分析
    analysis = analyzer.run(collected)
    
    # Step 3: 趋势预测
    prediction = predictor.run(analysis)
    
    return prediction
```

## 5. API接口设计

### 5.1 预测接口

**POST /api/v1/predict**

Request:
```json
{
  "title": "Fed cuts rates",
  "description": "Federal Reserve announced 50bp rate cut",
  "source": "WorldMonitor",
  "category": "Monetary Policy",
  "importance": 5
}
```

Response:
```json
{
  "prediction_id": "pred-xxx",
  "trend": "UP",
  "confidence": 0.75,
  "reasoning": "Based on analysis...",
  "time_horizon": "Short-term (1-7 days)",
  "factors": ["positive_event", "market_sentiment"]
}
```

### 5.2 事件列表

**GET /api/v1/events**

Response:
```json
{
  "events": [...],
  "total": 100,
  "page": 1
}
```

## 6. 配置管理

```yaml
# config.yaml
llm:
  provider: anthropic  # or openai
  model: claude-sonnet-4-20250514
  temperature: 0.7
  max_tokens: 2000

worldmonitor:
  rss_endpoint: "https://worldmonitor/api/rss-proxy"
  polymarket_endpoint: "https://worldmonitor/api/polymarket"

api:
  host: "0.0.0.0"
  port: 8000
  debug: false
```

---

*架构版本：1.0*
*设计日期：2026-03-12*
