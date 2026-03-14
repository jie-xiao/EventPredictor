# EventPredictor 详细需求文档
# 版本：v4.0 (修订版)
# 日期：2026-03-13
# 状态：开发中

---

## 1. 项目概述

### 1.1 项目名称
EventPredictor - 全球态势推演大屏

### 1.2 项目目标
基于真实事件数据，通过多Agent角色扮演分析，模拟各方反应，自动推演并展示事态发展。

### 1.3 核心价值
- **数据独立**：不依赖外部服务，数据获取代码直接嵌入
- **自动分析**：多Agent并行分析各方反应
- **自动推演**：综合研判事态发展
- **大屏展示**：态势感知可视化大屏

### 1.4 重要说明
- 前端 = 只展示推演结果
- 不需要用户选择事件
- 不需要用户选择角色
- 全自动流程

---

## 2. 数据获取模块

### 2.1 数据来源类型

| 编号 | 类型 | 数据源 | 实现方式 |
|------|------|--------|----------|
| 1 | 内置数据 | 预置事件JSON | 直接加载 |
| 2 | RSS聚合 | 全球新闻RSS | httpx请求 |
| 3 | 预测市场 | Polymarket API | httpx请求 |
| 4 | 模拟数据 | 生成器 | 随机生成 |

### 2.2 预置事件数据格式

```json
{
  "events": [
    {
      "id": "evt-001",
      "title": "美军航母进入南海",
      "description": "美国海军尼米兹号航母战斗群进入南海海域",
      "category": "military",
      "severity": 5,
      "location": {
        "country": "中国",
        "region": "南海",
        "lat": 15.0,
        "lon": 115.0
      },
      "timestamp": "2026-03-12T10:00:00Z",
      "source": "军事观察",
      "entities": ["美国", "中国", "菲律宾"],
      "sentiment": "negative"
    }
  ]
}
```

### 2.3 RSS新闻源列表

| 编号 | 名称 | URL | 语言 |
|------|------|-----|------|
| 1 | 新华社 | https://www.xinhuanet.com/politics/news_politics.xml | 中文 |
| 2 | BBC | http://feeds.bbci.co.uk/news/world/rss.xml | 英文 |
| 3 | Reuters | https://www.reutersagency.com/feed/ | 英文 |
| 4 | Al Jazeera | https://www.aljazeera.com/xml/rss/all.xml | 英文 |

### 2.4 数据获取模块API

```python
class DataService:
    """数据获取服务"""
    
    def get_events(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        time_range: str = "24h"
    ) -> List[Event]:
        """获取事件列表"""
        pass
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """根据ID获取事件"""
        pass
    
    def refresh_data(self) -> bool:
        """刷新数据"""
        pass
```

### 2.5 事件类别定义

| 类别ID | 中文名 | 英文名 | 严重程度 | 颜色 |
|--------|--------|--------|----------|------|
| military | 军事 | military | 1-5 | 🔴红色 |
| conflict | 冲突 | conflict | 1-5 | 🔴红色 |
| economy | 经济 | economic | 1-5 | 🟡黄色 |
| trade | 贸易 | trade | 1-5 | 🟡黄色 |
| politics | 政治 | politics | 1-5 | 🟡黄色 |
| disaster | 灾害 | disaster | 1-5 | 🔴红色 |
| cyber | 网络安全 | cyber | 1-5 | 🟠橙色 |
| other | 其他 | other | 1-3 | 🟢绿色 |

---

## 3. 多Agent角色系统

### 3.1 角色定义

#### 3.1.1 角色属性

```python
class AgentRole:
    id: str           # 唯一标识
    name: str         # 显示名称
    category: str     # 类别
    icon: str         # 图标
    stance: str       # 立场描述
    decision_style: str  # 决策特点
    language_style: str # 语言风格
    focus_points: List[str]  # 关注点
    system_prompt: str   # 系统提示词
```

#### 3.1.2 角色列表

**政府类 (4个)**

| ID | 名称 | 图标 | 立场 | 决策特点 |
|----|------|------|------|----------|
| cn_gov | 中国政府 | 🇨🇳 | 维护国家利益、政权稳定 | 集体决策、长远考虑 |
| us_gov | 美国政府 | 🇺🇸 | 维护霸权、美国优先 | 利益导向、选举考量 |
| eu_gov | 欧盟 | 🇪🇺 | 欧洲一体化、价值观 | 多国协商、程序繁琐 |
| ru_gov | 俄罗斯 | 🇷🇺 | 维护大国地位 | 现实主义、核威慑 |

**企业类 (3个)**

| ID | 名称 | 图标 | 立场 | 决策特点 |
|----|------|------|------|----------|
| tech_giant | 科技巨头 | 🏢 | 商业利益、技术领先 | 市场导向、创新驱动 |
| finance_company | 金融巨头 | 💰 | 投资回报、风险控制 | 数据驱动、利润最大化 |
| cn_company | 中国企业 | 🇨🇳🏢 | 国内市场、政策配合 | 政策敏感、规模扩张 |

**民众类 (3个)**

| ID | 名称 | 图标 | 立场 | 决策特点 |
|----|------|------|------|----------|
| public | 普通民众 | 👤 | 生活安全、经济状况 | 情绪化、信息不对称 |
| intellectual | 知识分子 | 🎓 | 社会批判、独立思考 | 理性分析、社会责任感 |
| netizen | 网民 | 💬 | 立场鲜明、情绪化 | 从众效应、极端化 |

**媒体类 (3个)**

| ID | 名称 | 图标 | 立场 | 决策特点 |
|----|------|------|------|----------|
| mainstream_media | 主流媒体 | 📰 | 客观报道、立场倾向 | 时效性、点击率 |
| social_media | 社交媒体 | 📱 | 流量、热点 | 速度优先、情绪放大 |
| official_media | 官方媒体 | 📢 | 政治正确、舆论引导 | 政策导向、安全优先 |

**投资者类 (3个)**

| ID | 名称 | 图标 | 立场 | 决策特点 |
|----|------|------|------|----------|
| institutional_investor | 机构投资者 | 📈 | 稳健回报、风险控制 | 基本面分析、长期投资 |
| retail_investor | 散户 | 💸 | 快速获利、跟风 | 情绪驱动、技术分析 |
| vc | 风险投资 | 🚀 | 高风险高回报 | 赛道投资、团队评估 |

### 3.2 系统提示词模板

```python
SYSTEM_PROMPT_TEMPLATE = """
你是{role_name}的决策者。

## 背景
{event_description}

## 你的立场
{stance}

## 决策特点
{decision_style}

## 语言风格
{language_style}

## 关注点
{', '.join(focus_points)}

请分析上述事件，从{role_name}的角度给出：
1. 立场和反应
2. 可能采取的行动
3. 对各方的影响
4. 置信度(0-100%)
"""
```

---

## 4. 后端架构

### 4.1 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | FastAPI | 0.104+ |
| 数据验证 | Pydantic | 2.0+ |
| HTTP客户端 | httpx | 0.24+ |
| LLM调用 | LangChain | 0.1.0+ |
| 数据存储 | JSON文件 | - |

### 4.2 模块划分

```
app/
├── api/
│   ├── routes/
│   │   ├── events.py      # 事件API
│   │   ├── analysis.py    # 分析API
│   │   └── health.py      # 健康检查
│   └── models/
│       ├── event.py       # 事件模型
│       └── analysis.py    # 分析模型
├── agents/
│   ├── roles/            # 角色定义
│   │   ├── __init__.py
│   │   └── registry.py   # 角色注册表
│   ├── pipeline.py       # 执行管道
│   └── analyzer.py       # 分析器
├── services/
│   ├── data_service.py    # 数据获取
│   ├── llm_service.py    # LLM调用
│   └── analysis_service.py # 分析服务
├── core/
│   ├── config.py         # 配置
│   └── logging.py        # 日志
└── storage/
    └── cache.py           # 缓存
```

### 4.3 API接口定义

#### 4.3.1 事件接口

```yaml
# GET /api/v1/events
获取事件列表

参数:
  - category: string (可选) 事件类别
  - limit: int (可选) 返回数量，默认20
  - time_range: string (可选) 时间范围，24h/7d/30d

响应:
  events: [
    {
      id: string,
      title: string,
      description: string,
      category: string,
      severity: int,
      location: {country, region, lat, lon},
      timestamp: string,
      source: string,
      entities: [string],
      sentiment: string
    }
  ]
```

#### 4.3.2 分析接口

```yaml
# POST /api/v1/analyze
发起分析

参数:
  - event_id: string (必填) 事件ID
  - roles: [string] (必填) 角色ID列表
  - depth: string (可选) 分析深度 simple/standard/detailed

响应:
  analysis_id: string,
  event: {...},
  role_analyses: [
    {
      role_id: string,
      role_name: string,
      stance: string,
      reaction: {emotion, action, statement},
      impact: {economic, political, social},
      confidence: float,
      reasoning: string
    }
  ],
  cross_analysis: {
    conflicts: [string],
    synergies: [string],
    consensus: [string]
  },
  synthesis: {
    overall_trend: string,
    summary: string,
    key_insights: [string],
    recommended_actions: [string],
    confidence: float
  }
```

#### 4.3.3 健康检查

```yaml
# GET /api/v1/health
健康检查

响应:
  status: "healthy",
  version: "1.0.0",
  timestamp: string
```

### 4.4 效率要求

| 指标 | 要求 | 说明 |
|------|------|------|
| 事件获取 | < 500ms | 从缓存或内置数据 |
| 单Agent分析 | < 3s | LLM调用时间 |
| 完整分析(5角色) | < 15s | 并行调用 |
| 综合推演 | < 10s | 交叉分析+生成 |
| 并发处理 | 50+ | 支持50并发请求 |
| 内存使用 | < 500MB | 正常运行 |
| CPU使用 | < 30% | 正常运行 |

---

## 5. 前端设计

### 5.1 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 框架 | React | 18+ |
| 构建 | Vite | 5+ |
| 语言 | TypeScript | 5+ |
| 地图 | react-globe.gl | 2+ |
| 地图 | Leaflet | 1.9+ |
| 图表 | Recharts | 2+ |
| 样式 | Tailwind CSS | 3+ |

### 5.2 页面布局

```
┌────────────────────────────────────────────────────────────────────────┐
│  🌍 全球态势推演大屏                              更新: 21:24 | 🔄  │
├──────────────────────────────────────┬─────────────────────────────────┤
│                                      │                                  │
│                                      │  📊 趋势预测                    │
│                                      │  ┌────────────────────────┐    │
│           🌍 3D地球                   │  │ ↑ 上涨: 65%           │    │
│           (事件标记在地图上)           │  │ ↓ 下跌: 25%           │    │
│                                      │  │ → 平稳: 10%           │    │
│                                      │  └────────────────────────┘    │
│                                      │                                  │
│                                      │  🎯 置信度: 75%              │
│                                      │  ████████████████░░░          │
│                                      │                                  │
│                                      │  ⚠️ 风险: 高                  │
│                                      │  💡 机会: 科技/避险          │
│                                      │                                  │
├──────────────────────────────────────┴─────────────────────────────────┤
│ 📋 实时事件 (5)                                              [收起]   │
│ ───────────────────────────────────────────────────────────────────   │
│ 🔴 [军事] 美军航母进入南海    | 南海    | 2h前    | 紧急          │
│ 🟡 [经济] 美联储利率决议      | 美国    | 5h前    | 重要          │
│ 🟢 [贸易] 中美贸易谈判        | 北京    | 1d前    | 一般          │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.3 组件清单

| 组件名 | 功能 | 位置 |
|--------|------|------|
| GlobeMap | 3D地球显示 | 左侧主区域 |
| EventMarker | 地图事件标记 | GlobeMap内 |
| InfoPanel | 右侧信息面板 | 右侧 |
| TrendChart | 趋势图表 | InfoPanel内 |
| ConfidenceBar | 置信度条 | InfoPanel内 |
| EventList | 事件列表 | 底部 |
| EventCard | 事件卡片 | EventList内 |

### 5.4 交互设计

| 交互 | 行为 |
|------|------|
| 点击地图标记 | 显示事件详情弹窗 |
| 悬停事件卡片 | 地图定位到事件 |
| 点击事件卡片 | 展开详情 |
| 自动刷新 | 每5分钟刷新数据 |
| 地图旋转 | 鼠标拖动/触屏滑动 |

### 5.5 颜色规范

| 用途 | 颜色 | Hex |
|------|------|-----|
| 紧急 | 红色 | #EF4444 |
| 重要 | 黄色 | #F59E0B |
| 一般 | 绿色 | #22C55E |
| 信息 | 蓝色 | #3B82F6 |
| 背景 | 深色 | #0F172A |
| 文字 | 白色 | #F8FAFC |
| 次要文字 | 灰色 | #94A3B8 |

### 5.6 响应式断点

| 断点 | 宽度 | 布局 |
|------|------|------|
| 大屏 | ≥1920px | 完整3D地图+侧边栏 |
| 桌面 | ≥1280px | 简化地图+侧边栏 |
| 平板 | ≥768px | 2D地图+底部列表 |
| 移动 | <768px | 纯列表模式 |

---

## 6. 执行流程

### 6.1 全自动流程

```
┌──────────────┐
│ 1. 定时触发  │ ← 每5分钟/手动触发
└──────┬───────┘
       ▼
┌──────────────┐
│ 2. 获取事件  │ ← 从数据源获取
└──────┬───────┘
       ▼
┌──────────────┐
│ 3. 事件筛选  │ ← 按严重程度排序
└──────┬───────┘
       ▼
┌──────────────┐
│ 4. 多Agent   │ ← 并行分析
│    分析       │
└──────┬───────┘
       ▼
┌──────────────┐
│ 5. 交叉分析   │ ← 冲突/协同/共识
└──────┬───────┘
       ▼
┌──────────────┐
│ 6. 综合推演   │ ← 生成预测
└──────┬───────┘
       ▼
┌──────────────┐
│ 7. 前端展示   │ ← 大屏可视化
└──────────────┘
```

---

## 7. 验收标准

### 7.1 功能验收

| 序号 | 功能 | 验收条件 | 权重 |
|------|------|----------|------|
| 1 | 事件获取 | 能获取并展示事件列表 | 15% |
| 2 | 地图显示 | 3D地球正确显示，事件标记在正确位置 | 20% |
| 3 | 紧急程度 | 颜色正确区分紧急程度 | 10% |
| 4 | 多Agent分析 | 至少5个角色正确分析 | 20% |
| 5 | 交叉分析 | 显示冲突/协同/共识 | 10% |
| 6 | 综合推演 | 生成趋势预测 | 15% |
| 7 | 自动刷新 | 每5分钟自动刷新 | 10% |

### 7.2 性能验收

| 序号 | 指标 | 要求 | 权重 |
|------|------|------|------|
| 1 | 首次加载 | < 3秒 | 25% |
| 2 | 事件获取 | < 500ms | 25% |
| 3 | 分析响应 | < 15秒 | 25% |
| 4 | 内存使用 | < 500MB | 25% |

### 7.3 体验验收

| 序号 | 指标 | 要求 | 权重 |
|------|------|------|------|
| 1 | 界面美观 | 符合设计规范 | 33% |
| 2 | 交互流畅 | 无明显卡顿 | 33% |
| 3 | 响应式 | 适配不同屏幕 | 34% |

### 7.4 总分计算

```
总分 = 功能分 × 0.6 + 性能分 × 0.2 + 体验分 × 0.2
```

**通过标准：总分 ≥ 90%**

---

## 8. 测试用例

### 8.1 功能测试

```python
# test_events_api.py
def test_get_events():
    """测试获取事件列表"""
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) > 0

def test_event_fields():
    """测试事件字段完整性"""
    response = client.get("/api/v1/events?limit=1")
    event = response.json()["events"][0]
    required_fields = ["id", "title", "description", "category", 
                      "severity", "location", "timestamp"]
    for field in required_fields:
        assert field in event
```

### 8.2 前端测试

```typescript
// test_globe.spec.tsx
test('3D地图渲染', () => {
  render(<GlobeMap events={events} />);
  const canvas = screen.getByRole('img');
  expect(canvas).toBeInTheDocument();
});

test('事件标记显示', () => {
  render(<EventMarker event={event} />);
  expect(screen.getByText(event.title)).toBeInTheDocument();
});
```

---

## 9. 部署配置

### 9.1 环境变量

```bash
# .env
LLM_PROVIDER=mock  # mock/anthropic/openai/minimax
LLM_MODEL=gpt-4
DATA_REFRESH_INTERVAL=300  # 秒
PORT=8000
FRONTEND_PORT=3000
```

### 9.2 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端API | 8000 | FastAPI服务 |
| 前端 | 3000 | Vite开发/静态服务 |
| 健康检查 | 8000/health | 健康检查端点 |

---

## 10. 后续规划

### Phase 2
- [ ] 接入真实RSS数据源
- [ ] 接入预测市场API
- [ ] 增加更多角色

### Phase 3
- [ ] 实时数据推送
- [ ] 历史推演验证
- [ ] 偏差分析

### Phase 4
- [ ] API开放
- [ ] 多语言支持
- [ ] 社区共建

---

## 11. 分析深度定义

### 11.1 depth参数说明

| 深度级别 | 响应时间 | 输出内容 | 适用场景 |
|----------|----------|----------|----------|
| **simple** | < 3s | 立场+行动+影响（各50字内） | 快速概览、实时大屏 |
| **standard** | < 10s | 详细分析+推理过程（各200字内） | 常规分析、报告生成 |
| **detailed** | < 30s | 深度研判+多角度分析+证据支持 | 重要决策、深度研究 |

### 11.2 各深度输出格式

```yaml
# simple输出
role_analysis:
  stance: "简短立场描述"
  action: "可能行动"
  impact: "影响简述"

# standard输出
role_analysis:
  stance: "详细立场"
  action: "具体行动"
  impact:
    economic: "经济影响"
    political: "政治影响"
    social: "社会影响"
  reasoning: "推理过程"

# detailed输出
role_analysis:
  stance: "深度立场分析"
  action: "多方案行动建议"
  impact: {...}
  reasoning: "完整推理链"
  evidence: ["支持证据1", "支持证据2"]
  alternatives: ["备选方案"]
```

---

## 12. 置信度计算规则

### 12.1 置信度定义

- **范围**：0-100%
- **含义**：分析结论的可信程度

### 12.2 计算因素

| 因素 | 权重 | 说明 |
|------|------|------|
| LLM原始置信度 | 50% | 模型自身输出的置信度 |
| 信息完整性 | 20% | 事件信息是否完整 |
| 角色匹配度 | 15% | 角色立场与事件相关性 |
| 时效性 | 15% | 事件发生时间 |

### 12.3 计算公式

```
final_confidence = 
  llm_confidence × 0.5 +
  info_completeness × 0.2 +
  role_relevance × 0.15 +
  timeliness × 0.15
```

### 12.4 置信度等级

| 等级 | 范围 | 颜色 | 含义 |
|------|------|------|------|
| 高 | ≥75% | 🟢绿色 | 置信度高，可参考 |
| 中 | 50-74% | 🟡黄色 | 置信度中等，谨慎参考 |
| 低 | <50% | 🔴红色 | 置信度低，仅供娱乐 |

---

## 13. 交叉分析逻辑

### 13.1 冲突检测

**定义**：不同角色的反应存在矛盾或对立

| 冲突类型 | 检测规则 | 示例 |
|----------|----------|------|
| 立场冲突 | 立场描述关键词相反 | "支持" vs "反对" |
| 行动冲突 | 建议行动互相抵消 | "增兵" vs "撤军" |
| 利益冲突 | 获益方与受损方对立 | 甲方收益 = 乙方损失 |

### 13.2 协同检测

**定义**：不同角色的行动或立场相互配合

| 协同类型 | 检测规则 | 示例 |
|----------|----------|------|
| 行动协同 | 行动方向一致 | "制裁" + "谴责" |
| 立场协同 | 立场倾向一致 | "担忧" + "警告" |
| 目标协同 | 最终目标相似 | 都指向"和平" |

### 13.3 共识检测

**定义**：多数角色对某一问题达成一致意见

| 共识类型 | 检测规则 | 示例 |
|----------|----------|------|
| 全面共识 | ≥80%角色立场相同 | 8/10角色"反对" |
| 多数共识 | ≥60%角色立场相同 | 6/10角色"担忧" |
| 分类共识 | 同类别角色立场相同 | 全部政府类"谴责" |

---

## 14. 综合推演规则

### 14.1 趋势预测

| 趋势 | 条件 | 输出 |
|------|------|------|
| **上涨** | 多方投资类角色看多 | "↑ 上涨: XX%" |
| **下跌** | 多方投资类角色看空 | "↓ 下跌: XX%" |
| **平稳** | 共识中性和解 | "→ 平稳: XX%" |
| **震荡** | 冲突大于协同 | "↔ 震荡: XX%" |

### 14.2 风险评估

| 风险等级 | 条件 |
|----------|------|
| 🔴 **高** | severity≥4 + 冲突≥2 |
| 🟠 **中** | severity≥3 + 冲突≥1 |
| 🟡 **低** | 其他 |

### 14.3 机会识别

从以下角色分析中提取：
- 科技巨头 → 技术机会
- 金融巨头 → 投资机会
- 机构投资者 → 避险机会

---

## 15. 错误处理

### 15.1 错误码定义

| 错误码 | 含义 | HTTP状态码 | 说明 |
|--------|------|------------|------|
| 1001 | 事件不存在 | 404 | 传入的event_id无效 |
| 1002 | 角色不存在 | 400 | 传入的role_id无效 |
| 1003 | LLM调用超时 | 504 | LLM服务响应超时 |
| 1004 | 数据源不可用 | 503 | 外部数据源连接失败 |
| 1005 | 分析进行中 | 409 | 同一事件分析正在进行 |
| 1006 | 参数验证失败 | 400 | 请求参数格式错误 |
| 1007 | 服务内部错误 | 500 | 服务器内部异常 |

### 15.2 错误响应格式

```json
{
  "error": {
    "code": 1001,
    "message": "事件不存在",
    "detail": "evt-999 不存在于数据库中"
  }
}
```

### 15.3 熔断机制

| 状态 | 条件 | 动作 |
|------|------|------|
| 正常 | 连续成功 | 计数器归零 |
| 警告 | 连续失败3次 | 熔断30秒 |
| 熔断 | 连续失败5次 | 熔断5分钟 |
| 恢复 | 熔断后成功 | 恢复正常 |

### 15.4 重试策略

| 场景 | 重试次数 | 间隔 |
|------|----------|------|
| 网络超时 | 3次 | 1s, 2s, 3s |
| LLM限流 | 3次 | 5s, 10s, 15s |
| 外部服务 | 2次 | 1s, 2s |

---

## 16. 安全认证

### 16.1 认证方式

| 环境 | 认证方式 | 说明 |
|------|----------|------|
| 开发环境 | 无 | 跳过认证 |
| 生产环境 | API Key | Header中传递 |

### 16.2 API Key配置

```bash
# 请求头
Header: X-API-Key: your-api-key-here

# 环境变量
API_KEY=your-api-key-here
```

### 16.3 限流规则

| 级别 | 限制 | 窗口 |
|------|------|------|
| 免费版 | 100请求/分钟 | sliding window |
| 专业版 | 500请求/分钟 | sliding window |
| 企业版 | 无限 | - |

### 16.4 敏感数据处理

| 数据类型 | 处理方式 |
|----------|----------|
| 事件位置 | 模糊化（国家级别） |
| 实体名称 | 脱敏处理 |
| 分析结果 | 缓存30分钟 |

---

## 17. 数据字典

### 17.1 事件字段

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| id | string | 是 | 事件唯一标识 | "evt-001" |
| title | string | 是 | 事件标题 | "美军航母进入南海" |
| description | string | 是 | 事件描述 | "美国海军尼米兹号..." |
| category | string | 是 | 事件类别 | "military" |
| severity | integer | 是 | 严重程度1-5 | 5 |
| location | object | 是 | 地理位置 | {...} |
| timestamp | string | 是 | ISO8601时间 | "2026-03-12T10:00:00Z" |
| source | string | 否 | 数据来源 | "军事观察" |
| entities | array | 否 | 涉及实体 | ["美国","中国"] |
| sentiment | string | 否 | 情感倾向 | "negative" |

### 17.2 location对象

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| country | string | 是 | 国家 |
| region | string | 否 | 地区/海域 |
| lat | float | 是 | 纬度 |
| lon | float | 是 | 经度 |

### 17.3 分析结果字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| analysis_id | string | 分析唯一标识 |
| event | object | 原始事件 |
| role_analyses | array | 各角色分析结果 |
| cross_analysis | object | 交叉分析结果 |
| synthesis | object | 综合推演结果 |
| confidence | float | 综合置信度 |
| created_at | string | 创建时间 |

---

## 18. 运维监控

### 18.1 日志规范

| 级别 | 使用场景 |
|------|----------|
| DEBUG | 调试信息、变量值 |
| INFO | 正常业务流程 |
| WARNING | 性能警告、可恢复错误 |
| ERROR | 业务异常、需要关注 |
| CRITICAL | 系统级错误、熔断触发 |

### 18.2 健康检查端点

```yaml
# GET /api/v1/health

响应:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-13T06:00:00Z",
  "uptime_seconds": 3600,
  "components": {
    "data_service": "healthy",
    "llm_service": "healthy", 
    "cache": "healthy"
  }
}
```

### 18.3 告警规则

| 指标 | 阈值 | 动作 |
|------|------|------|
| 错误率 | >5% | 告警 |
| 响应时间 | >10s | 告警 |
| 内存使用 | >80% | 告警 |
| 磁盘使用 | >90% | 告警 |

---

## 19. 版本管理

### 19.1 API版本策略

- 当前版本：`v1`
- 版本格式：`/api/v1/*`
- 后续版本：`v2`, `v3`...

### 19.2 向后兼容

- 新增字段：可选，兼容旧版本
- 新增接口：独立路径，兼容旧版本
- 废弃字段：提前2个版本警告

### 19.3 版本迁移

| 阶段 | 时间 | 说明 |
|------|------|------|
| 公告 | 提前1个月 | 宣布废弃计划 |
| 警告 | 提前2周 | 返回警告头 |
| 废弃 | 到期 | 返回410 Gone |
| 移除 | 3个月后 | 完全移除 |
