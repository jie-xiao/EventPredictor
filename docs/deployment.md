# 部署文档 - EventPredictor

## 部署要求

- Python 3.11+
- Docker (可选)
- 4GB+ RAM

## 本地部署

### 方式1：直接运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

服务将在 http://localhost:8000 启动

### 方式2：Docker部署

```bash
# 构建镜像
docker build -f docker/Dockerfile -t eventpredictor .

# 运行容器
docker run -p 8000:8000 eventpredictor
```

### 方式3：Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Claude API密钥 | - |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |
| `WM_RSS_ENDPOINT` | WorldMonitor RSS端点 | http://worldmonitor:3000/api/rss-proxy |
| `WM_POLYMARKET_ENDPOINT` | WorldMonitor Polymarket端点 | http://worldmonitor:3000/api/polymarket |

## API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/docs` | GET | Swagger文档 |
| `/redoc` | GET | ReDoc文档 |
| `/health` | GET | 健康检查 |
| `/api/v1/predict` | POST | 提交预测 |
| `/api/v1/events` | GET | 事件列表 |
| `/api/v1/predictions` | GET | 预测列表 |

## 生产部署建议

1. **使用gunicorn替代uvicorn**
2. **配置HTTPS/TLS**
3. **添加数据库（PostgreSQL）**
4. **配置日志系统**
5. **添加监控告警**

---

*版本：1.0.0*
*日期：2026-03-12*
