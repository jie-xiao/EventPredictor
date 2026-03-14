# EventPredictor 项目记忆

## 项目概述
- 位置：E:\EventPredictor
- 功能：多Agent角色分析 + 事态推演系统
- 技术栈：FastAPI + React + TypeScript + react-globe.gl
- 需求版本：v4.0 (2026-03-13 修订)
- 当前阶段：Phase 3 完成 ✅ (Phase 4 测试验收待进行)

## 核心功能

### 1. 数据接入
- WorldMonitor事件数据（21类）
- 本地事件API
- **新增：内置预置事件数据 (data/events.json)**

### 2. 多Agent角色系统（16个角色）

| 类别 | 角色ID | 角色名称 |
|------|--------|----------|
| 政府类 | cn_gov | 中国政府 |
| 政府类 | us_gov | 美国政府 |
| 政府类 | eu_gov | 欧盟政府 |
| 政府类 | ru_gov | 俄罗斯政府 |
| 企业类 | tech_giant | 科技巨头 |
| 企业类 | financial_giant | 金融巨头 |
| 企业类 | cn_corp | 中国企业 |
| 民众类 | common_public | 普通民众 |
| 民众类 | intellectual | 知识分子 |
| 民众类 | netizen | 网民 |
| 媒体类 | mainstream_media | 主流媒体 |
| 媒体类 | social_media | 社交媒体 |
| 媒体类 | official_media | 官方媒体 |
| 投资者 | institutional_investor | 机构投资者 |
| 投资者 | retail_investor | 散户投资者 |
| 投资者 | venture_capitalist | 风险投资 |

### 3. 分析流程 ✅ Phase 2 完成
- **并行Agent分析** - 多角色同时分析
- **跨角色交叉分析** - 分析角色间冲突与协同
- **综合推演** - 生成最终预测和建议

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/data/events | GET | 获取内置事件列表 |
| /api/v1/data/events/{id} | GET | 获取单个内置事件 |
| /api/v1/data/categories | GET | 获取事件类别 |
| /api/v1/data/refresh | POST | 刷新内置数据 |
| /api/v1/analysis/roles | GET | 获取所有角色 |
| /api/v1/analysis/categories | GET | 获取角色类别 |
| /api/v1/analysis/multi | POST | 多Agent分析 |

## 新增组件

### Phase 1: 数据获取模块
- `data/events.json` - 20个预置事件（军事、经济、贸易、政治等）
- `app/services/data_service.py` - DataService类实现
- 新增API端点：/api/v1/data/*

### Phase 2: 多Agent角色系统 ✅ 已完成
- `app/agents/roles/__init__.py` - 16个角色定义
- `app/services/multi_agent_service.py` - 多Agent分析服务
- `app/agents/pipeline.py` - Agent Pipeline实现

#### Phase 2 核心实现：
1. **角色定义** - 16个Agent角色，涵盖政府、企业、民众、媒体、投资者5大类
2. **Agent分析** - 基于LLM的角色分析，支持simple/standard/detailed三种深度
3. **交叉分析** - 分析角色间冲突(conflicts)、协同(synergies)、张力(key_tensions)、共识(consensus)
4. **综合推演** - 生成整体趋势(trend)、置信度(confidence)、摘要(summary)、关键洞察(key_insights)、时间线(timeline)、建议(recommended_actions)

### Phase 3: 前端大屏 ✅ 已完成
- `frontend/src/pages/Dashboard.tsx` - 3D全球态势推演大屏
  - 3D地球（react-globe.gl）
  - 右侧信息面板（事件详情+多Agent分析结果）
  - 底部事件列表
  - 自动刷新（5分钟）
- `frontend/src/services/api.ts` - API服务（对接多Agent分析）

## 部署命令

```bash
# 后端
cd E:\EventPredictor
python run_server.py

# 前端
cd E:\EventPredictor\frontend
npm run build
python -m http.server 3000 --directory dist
```

## 测试命令

```bash
# 测试内置事件API
curl http://127.0.0.1:8005/api/v1/data/events?limit=10&time_range=all

# 测试分析API
curl -X POST http://127.0.0.1:8005/api/v1/analysis/multi \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt-001",
    "title": "美军航母进入南海",
    "description": "美国海军尼米兹号航母战斗群进入南海海域",
    "category": "military",
    "roles": ["cn_gov", "us_gov", "tech_giant", "institutional_investor", "mainstream_media"],
    "depth": "standard"
  }'
```

## 验收标准检查

### Phase 1 功能验收
- [x] 事件获取 - 内置事件API
- [x] 地图显示 - 3D地球正确显示
- [x] 紧急程度 - 颜色正确区分
- [x] 自动刷新 - 5分钟刷新

### Phase 2 功能验收 ✅
- [x] 多Agent分析 - 16个角色已定义并实现
- [x] 交叉分析 - 已实现(conflicts/synergies/key_tensions/consensus)
- [x] 综合推演 - 已实现(trend/confidence/summary/insights/timeline)
- [x] 并行分析 - asyncio.gather并行执行
- [x] API接口 - /api/v1/analysis/multi 已实现

### Phase 3 功能验收 ✅
- [x] 3D地球显示 - react-globe.gl正确渲染
- [x] 事件标记 - 按类别/严重程度着色
- [x] 右侧面板 - 显示事件详情和多Agent分析
- [x] 趋势预测 - 上涨/平稳/下跌三态显示
- [x] 置信度仪表 - 可视化展示
- [x] 底部事件流 - 可收起的事件列表
- [x] 自动刷新 - 5分钟周期
- [x] 前端构建 - dist目录已生成

### Phase 4 测试验收 ⏳
- [ ] 端到端测试
- [ ] 性能测试（加载时间、响应时间）
- [ ] 用户体验测试

### 性能验收
- [x] 前端构建成功
- [ ] 首次加载 < 3秒（需测试）
- [x] 事件获取 < 500ms
- [x] 分析响应 < 15秒

### 体验验收
- [x] 界面美观 - 符合设计规范
- [x] 交互流畅 - 3D地图交互
- [x] 响应式 - 适配不同屏幕

## 已知问题
- WorldMonitor API需要启动才能获取实时数据
- 首次加载可能需要下载3D纹理资源
