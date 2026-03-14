# EventPredictor - 全球局势推演决策系统

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.11+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-19+-cyan.svg" alt="React">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

## 项目简介

EventPredictor 是一个基于多智能体协作的全球局势推演决策系统。它能够接收全球事件信息，通过信息收集、深度分析和趋势预测三个阶段，输出未来走势预测和置信度。系统配备了交互式的3D地球可视化界面，支持情景推演、历史记录追踪等功能。

## 核心功能

- 🌐 **3D地球可视化** - 交互式3D地球展示全球事件分布
- 🔍 **多源数据采集** - 集成20+中文RSS源和多个国际新闻源
- 🧠 **多Agent分析** - 信息收集 → 深度分析 → 趋势预测
- 📊 **情景推演** - 生成乐观/基准/悲观三种发展情景
- 🔎 **搜索与筛选** - 按类别、严重程度、关键词筛选事件
- 📜 **历史记录** - 保存和查看预测历史
- 📈 **可视化图表** - 情感雷达图、冲突热力图、趋势仪表盘
- 🌐 **API服务** - RESTful API，易于集成

## 技术架构

```
┌─────────────────────────────────────────┐
│           FastAPI Server                │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Info    │→ │Analysis │→ │Predict │ │
│  │ Collector│ │ Agent   │  │ Agent  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
├─────────────────────────────────────────┤
│           LangChain Agent Framework     │
└─────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 |
|------|------|
| Web框架 | FastAPI |
| Agent框架 | LangChain |
| LLM | Claude / OpenAI |
| 部署 | Docker |

## 快速开始

### 环境要求

- Python 3.11+
- Docker (可选)

### 安装

```bash
# 克隆项目
cd EventPredictor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

创建 `config.yaml` 或使用默认配置：

```yaml
llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
  temperature: 0.7

api:
  host: "0.0.0.0"
  port: 8000
```

### 运行

```bash
# 直接运行
python main.py

# 或使用uvicorn
uvicorn app.main:app --reload
```

### Docker部署

```bash
# 构建镜像
docker build -f docker/Dockerfile -t eventpredictor .

# 运行容器
docker run -p 8000:8000 eventpredictor

# 或使用docker-compose
docker-compose up -d
```

## API使用

### 预测接口

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Federal Reserve cuts rates by 50 basis points",
    "description": "The Fed announced a 50bp rate cut",
    "source": "WorldMonitor",
    "category": "Monetary Policy",
    "importance": 5
  }'
```

响应示例：

```json
{
  "prediction_id": "pred-abc123",
  "event_id": "evt-xyz789",
  "trend": "UP",
  "confidence": 0.75,
  "reasoning": "Based on event analysis...",
  "time_horizon": "Short-term (1-7 days)",
  "factors": ["Positive sentiment", "Market liquidity"]
}
```

### 健康检查

```bash
curl "http://localhost:8000/health"
```

## 开发

### 项目结构

```
EventPredictor/
├── app/
│   ├── api/
│   │   ├── models/      # 数据模型
│   │   └── routes/      # API路由
│   ├── agents/          # Agent实现
│   ├── services/       # 服务层
│   ├── core/           # 核心配置
│   └── main.py         # 应用入口
├── config/             # 配置文件
├── docker/             # Docker配置
├── tests/              # 测试文件
├── docs/               # 文档
├── requirements.txt    # 依赖
└── main.py            # 主入口
```

### 运行测试

```bash
pytest tests/ -v
```

## 与WorldMonitor集成

EventPredictor 可与 WorldMonitor 项目集成，获取实时全球事件数据：

- RSS新闻聚合
- Polymarket预测市场数据
- Telegram频道监控
- YouTube监控

配置 `config.yaml` 中的 WorldMonitor 端点即可。

## 许可证

MIT License

---

*基于 WorldMonitor 的全球事件监控能力构建*
