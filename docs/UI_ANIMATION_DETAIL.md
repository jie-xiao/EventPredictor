# EventPredictor UI 动画与交互详解

> **版本**: v3.3 | **日期**: 2026-03-14 | **用途**: 前端开发详细参考

---

## 目录

1. [右侧抽屉 - 分析面板](#1-右侧抽屉---分析面板)
2. [左侧抽屉 - 角色详情](#2-左侧抽屉---角色详情)
3. [底部抽屉 - 事件列表](#3-底部抽屉---事件列表)
4. [悬浮工具栏按钮功能](#4-悬浮工具栏按钮功能)

---

## 1. 右侧抽屉 - 分析面板

### 1.1 抽屉结构

```
┌────────────────────────────────┐
│ ◀ 趋势预测              [×]   │  Header (56px)
│   ┌────────────────────────┐  │
│   │ ◀ 返回                 │  │
├────────────────────────────────┤
│                                │
│  ┌───────────┐    ┌─────┐     │
│  │    ↑      │    │ 75% │     │  趋势 + 置信度
│  │   上涨    │    │ ○   │     │
│  └───────────┘    └─────┘     │
│                                │
│  ████████████████░░░░░░        │  置信度进度条
│                                │
├────────────────────────────────┤
│  📌 关键洞察                   │  Section
│  • 美方可能增派舰艇             │
│  • 中方或将加强巡航             │
│                                │
├────────────────────────────────┤
│  ⚠️ 风险: 高    🔥 冲突: 3     │  Grid 2x2
│                                │
├────────────────────────────────┤
│  ⏱ 时间线                      │  Section
│  ●───○───○                     │
│  24h  72h  7d                  │
│                                │
├────────────────────────────────┤
│  📋 共识                       │  Tags
│  [外交磋商] [区域稳定]          │
│                                │
├────────────────────────────────┤
│                                │
│  [    查看完整分析 →    ]      │  Footer (80px)
│                                │
└────────────────────────────────┘
        360px width
```

### 1.2 展开动画详细时间线

```
右侧抽屉展开动画 (总时长: 300ms)

时间轴:
├────────┼────────┼────────┼────────┼────────┤
0ms     60ms    120ms    180ms    240ms    300ms

【抽屉面板】
位置:     100%─────75%─────50%─────25%─────10%─────0
          translateX
透明度:   0.9──────────────────────────────────1

【遮罩层】
透明度:   0──────────────────────────────────0.4
          (延迟0ms开始)

【地球容器】
宽度:     100%────────────────────────────calc(100%-360px)
          (延迟50ms开始)

【内容淡入】
透明度:   0───────────────────(延迟150ms)──1
位移Y:    10px────────────────────────────0px
```

### 1.3 动画参数表

| 属性 | 初始值 | 结束值 | 时长 | 延迟 | 缓动函数 |
|------|--------|--------|------|------|----------|
| translateX | 100% | 0 | 300ms | 0 | cubic-bezier(0.4, 0, 0.2, 1) |
| opacity | 0.9 | 1 | 200ms | 0 | ease |
| visibility | hidden | visible | 0 | 300ms | - |
| 地球 width | 100% | calc(100%-360px) | 300ms | 50ms | 同上 |
| 内容 opacity | 0 | 1 | 200ms | 150ms | ease |
| 内容 translateY | 10px | 0 | 200ms | 150ms | ease |

### 1.4 关键帧分解

```css
/* 0ms - 初始状态 */
.drawer-right {
  transform: translateX(100%);
  opacity: 0.9;
}

/* 60ms - 开始滑动 */
.drawer-right.animating {
  transform: translateX(75%);
  opacity: 0.95;
}

/* 120ms - 滑动过半 */
.drawer-right.animating {
  transform: translateX(50%);
  opacity: 1;
}

/* 180ms - 接近完成 */
.drawer-right.animating {
  transform: translateX(25%);
}

/* 240ms - 即将到位 */
.drawer-right.animating {
  transform: translateX(10%);
}

/* 300ms - 动画完成 */
.drawer-right.open {
  transform: translateX(0);
  opacity: 1;
}
```

### 1.5 完整 CSS 代码

```css
/* ========================================
   右侧抽屉 - 分析面板
   ======================================== */

.drawer-right {
  /* 定位 */
  position: fixed;
  top: 0;
  right: 0;
  width: 360px;
  height: 100vh;
  z-index: 900;

  /* 初始状态 */
  transform: translateX(100%);
  opacity: 0.9;
  visibility: hidden;
  pointer-events: none;

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);

  /* 过渡动画 */
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 300ms;

  /* 性能优化 */
  will-change: transform, opacity;
  contain: layout style;
}

/* 展开状态 */
.drawer-right.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
  pointer-events: auto;

  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 0ms;
}

/* ===== Header ===== */
.drawer-right .drawer-header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;

  background: linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.05) 0%,
    rgba(0, 119, 255, 0.05) 100%
  );
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
}

.drawer-right .drawer-title {
  font-size: 16px;
  font-weight: 600;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-right .drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #94A3B8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms ease;
}

.drawer-right .drawer-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #F8FAFC;
}

/* ===== Content ===== */
.drawer-right .drawer-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;

  /* 内容淡入动画 */
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 200ms ease 150ms,
    transform 200ms ease 150ms;
}

.drawer-right.open .drawer-content {
  opacity: 1;
  transform: translateY(0);
}

/* 自定义滚动条 */
.drawer-right .drawer-content::-webkit-scrollbar {
  width: 6px;
}

.drawer-right .drawer-content::-webkit-scrollbar-track {
  background: transparent;
}

.drawer-right .drawer-content::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}

.drawer-right .drawer-content::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}

/* ===== Section ===== */
.drawer-section {
  margin-bottom: 24px;
}

.drawer-section:last-child {
  margin-bottom: 0;
}

.drawer-section-title {
  font-size: 12px;
  font-weight: 500;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ===== Footer ===== */
.drawer-right .drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  flex-shrink: 0;

  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid rgba(30, 41, 59, 0.6);
}

.drawer-right .drawer-footer button {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 200ms ease;
}

.drawer-right .drawer-footer button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 229, 255, 0.3);
}
```

---

## 2. 左侧抽屉 - 角色详情

### 2.1 抽屉结构

```
┌────────────────────────────────┐
│ [×]                    16角色  │  Header (56px)
├────────────────────────────────┤
│ 🔍 搜索角色...                 │  Search (48px)
├────────────────────────────────┤
│ [全部] [政府] [企业] [民众]    │  Tabs (40px)
├────────────────────────────────┤
│                                │
│ ┌────────────────────────────┐ │
│ │ 🇨🇳 中国政府               │ │  Role Card
│ │ 立场: 维护主权             │ │
│ │ 行动: 加强巡航             │ │
│ │ 置信度: 82% ████████░░     │ │
│ └────────────────────────────┘ │
│                                │
│ ┌────────────────────────────┐ │
│ │ 🇺🇸 美国政府               │ │  Role Card
│ │ 立场: 航行自由             │ │
│ │ 行动: 继续存在             │ │
│ │ 置信度: 78% ███████░░░     │ │
│ └────────────────────────────┘ │
│                                │
│ ┌────────────────────────────┐ │
│ │ 🇪🇺 欧盟                   │ │  Role Card
│ │ ...                        │ │
│ └────────────────────────────┘ │
│                                │
│ ... 更多角色 (可滚动)          │
│                                │
└────────────────────────────────┘
        320px width
```

### 2.2 展开动画详细时间线

```
左侧抽屉展开动画 (总时长: 280ms)

时间轴:
├────────┼────────┼────────┼────────┼────────┤
0ms     56ms    112ms    168ms    224ms    280ms

【抽屉面板】
位置:     -100%────-75%────-50%────-25%────-10%────0
          translateX
透明度:   0.9──────────────────────────────────1

【地球容器】
宽度:     100%────────────────────────────calc(100%-320px)
边距:     0──────────────────────────────320px
          (延迟40ms开始)

【内容淡入】
透明度:   0───────────────────(延迟140ms)──1
位移Y:    10px────────────────────────────0px

【角色卡片依次出现】
卡片1:    0ms延迟, 150ms动画
卡片2:    50ms延迟, 150ms动画
卡片3:    100ms延迟, 150ms动画
... 依次类推
```

### 2.3 动画参数表

| 属性 | 初始值 | 结束值 | 时长 | 延迟 | 缓动函数 |
|------|--------|--------|------|------|----------|
| translateX | -100% | 0 | 280ms | 0 | cubic-bezier(0.4, 0, 0.2, 1) |
| opacity | 0.9 | 1 | 180ms | 0 | ease |
| visibility | hidden | visible | 0 | 280ms | - |
| 地球 width | 100% | calc(100%-320px) | 280ms | 40ms | 同上 |
| 地球 margin-left | 0 | 320px | 280ms | 40ms | 同上 |
| 内容 opacity | 0 | 1 | 180ms | 140ms | ease |

### 2.4 完整 CSS 代码

```css
/* ========================================
   左侧抽屉 - 角色详情
   ======================================== */

.drawer-left {
  position: fixed;
  top: 0;
  left: 0;
  width: 320px;
  height: 100vh;
  z-index: 700;

  transform: translateX(-100%);
  opacity: 0.9;
  visibility: hidden;
  pointer-events: none;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);

  transition:
    transform 280ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 180ms ease,
    visibility 0ms linear 280ms;

  will-change: transform, opacity;
  contain: layout style;
}

.drawer-left.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
  pointer-events: auto;

  transition:
    transform 280ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 180ms ease,
    visibility 0ms linear 0ms;
}

/* ===== Header ===== */
.drawer-left .drawer-header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;

  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
}

.drawer-left .drawer-title {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
}

.drawer-left .drawer-count {
  font-size: 12px;
  font-weight: 500;
  color: #64748B;
  background: rgba(30, 41, 59, 0.6);
  padding: 4px 10px;
  border-radius: 12px;
}

/* ===== Search ===== */
.drawer-left .drawer-search {
  padding: 12px 20px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
}

.drawer-left .search-input {
  width: 100%;
  height: 36px;
  padding: 0 12px 0 36px;
  border-radius: 8px;
  border: 1px solid rgba(30, 41, 59, 0.8);
  background: rgba(30, 41, 59, 0.4);
  color: #F8FAFC;
  font-size: 14px;
  transition: all 150ms ease;
}

.drawer-left .search-input:focus {
  outline: none;
  border-color: rgba(0, 229, 255, 0.5);
  background: rgba(30, 41, 59, 0.6);
}

.drawer-left .search-input::placeholder {
  color: #64748B;
}

/* ===== Tabs ===== */
.drawer-left .drawer-tabs {
  padding: 12px 20px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  overflow-x: auto;
}

.drawer-left .tab-item {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #94A3B8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 150ms ease;
}

.drawer-left .tab-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #F8FAFC;
}

.drawer-left .tab-item.active {
  background: rgba(0, 229, 255, 0.1);
  color: #00E5FF;
}

/* ===== Content ===== */
.drawer-left .drawer-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;

  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 180ms ease 140ms,
    transform 180ms ease 140ms;
}

.drawer-left.open .drawer-content {
  opacity: 1;
  transform: translateY(0);
}

/* ===== Role Card ===== */
.role-card {
  padding: 16px;
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(30, 41, 59, 0.5);
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 150ms ease;

  /* 依次出现动画 */
  opacity: 0;
  transform: translateX(-10px);
}

.drawer-left.open .role-card {
  opacity: 1;
  transform: translateX(0);
}

.drawer-left.open .role-card:nth-child(1) { transition-delay: 0ms; }
.drawer-left.open .role-card:nth-child(2) { transition-delay: 50ms; }
.drawer-left.open .role-card:nth-child(3) { transition-delay: 100ms; }
.drawer-left.open .role-card:nth-child(4) { transition-delay: 150ms; }
.drawer-left.open .role-card:nth-child(5) { transition-delay: 200ms; }
.drawer-left.open .role-card:nth-child(6) { transition-delay: 250ms; }
.drawer-left.open .role-card:nth-child(7) { transition-delay: 300ms; }
.drawer-left.open .role-card:nth-child(8) { transition-delay: 350ms; }

.role-card:hover {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(51, 65, 85, 0.8);
  transform: translateX(4px);
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.role-card-icon {
  font-size: 20px;
}

.role-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
}

.role-card-category {
  font-size: 10px;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-card-stance {
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 4px;
}

.role-card-action {
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 8px;
}

.role-card-confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-card-confidence-label {
  font-size: 11px;
  color: #64748B;
}

.role-card-confidence-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: rgba(30, 41, 59, 0.8);
  overflow: hidden;
}

.role-card-confidence-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #10B981 0%, #00E5FF 100%);
  transition: width 500ms ease;
}

.role-card-confidence-value {
  font-size: 11px;
  font-weight: 500;
  color: #F8FAFC;
  font-family: 'JetBrains Mono', monospace;
  min-width: 32px;
  text-align: right;
}
```

---

## 3. 底部抽屉 - 事件列表

### 3.1 抽屉结构

```
收起状态 (48px):
┌────────────────────────────────────────────────────────────────┐
│  ▼ 事件列表 (5)    2个紧急 · 1个重要 · 2个一般          [×]   │
└────────────────────────────────────────────────────────────────┘

展开状态 (200px):
┌────────────────────────────────────────────────────────────────┐
│  ▲ 事件列表 (5)    2个紧急 · 1个重要 · 2个一般          [×]   │ Header
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │🔴 紧急  │ │🔴 紧急  │ │🟡 重要  │ │🟢 一般  │ │🟢 一般  │  │ Cards
│  │         │ │         │ │         │ │         │ │         │  │
│  │美军航母  │ │美联储   │ │中美贸易 │ │气候峰会 │ │科技合作 │  │
│  │进入南海  │ │利率决议 │ │谈判     │ │         │ │         │  │
│ │         │ │         │ │         │ │         │ │         │  │
│  │2h前    │ │5h前    │ │1d前    │ │2d前    │ │3d前    │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                                │
│  ←─────────────────── 横向滚动 ──────────────────────→        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 展开动画详细时间线

```
底部抽屉展开动画 (总时长: 250ms)

时间轴:
├────────┼────────┼────────┼────────┼────────┤
0ms     50ms    100ms    150ms    200ms    250ms

【抽屉高度】
高度:     48px────80px────120px───160px───185px───200px

【展开图标旋转】
旋转:     0deg──────────────────────────────180deg
          (200ms内完成)

【内容淡入】
透明度:   0────────(延迟50ms)──────────────1
位移Y:    10px────────────────────────────0px

【事件卡片依次出现】
卡片1:    0ms延迟, 150ms动画
卡片2:    30ms延迟, 150ms动画
卡片3:    60ms延迟, 150ms动画
... 依次类推
```

### 3.3 动画参数表

| 属性 | 初始值 | 结束值 | 时长 | 延迟 | 缓动函数 |
|------|--------|--------|------|------|----------|
| height | 48px | 200px | 250ms | 0 | cubic-bezier(0.4, 0, 0.2, 1) |
| 展开图标 rotate | 0deg | 180deg | 200ms | 0 | ease |
| 内容 opacity | 0 | 1 | 150ms | 50ms | ease |
| 内容 translateY | 10px | 0 | 150ms | 50ms | ease |

### 3.4 完整 CSS 代码

```css
/* ========================================
   底部抽屉 - 事件列表
   ======================================== */

.drawer-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 800;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);
  overflow: hidden;

  transition: height 250ms cubic-bezier(0.4, 0, 0.2, 1);

  will-change: height;
  contain: layout style;
}

.drawer-bottom.open {
  height: 200px;
}

/* ===== Header ===== */
.drawer-bottom .drawer-header {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  cursor: pointer;
  user-select: none;
}

.drawer-bottom .drawer-header:hover {
  background: rgba(255, 255, 255, 0.02);
}

.drawer-bottom .header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.drawer-bottom .expand-icon {
  width: 20px;
  height: 20px;
  color: #94A3B8;
  transition: transform 200ms ease;
}

.drawer-bottom.open .expand-icon {
  transform: rotate(180deg);
}

.drawer-bottom .drawer-title {
  font-size: 14px;
  font-weight: 500;
  color: #F8FAFC;
}

.drawer-bottom .drawer-count {
  font-size: 12px;
  color: #64748B;
}

.drawer-bottom .header-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-bottom .stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94A3B8;
}

.drawer-bottom .stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.drawer-bottom .stat-dot.danger { background: #EF4444; }
.drawer-bottom .stat-dot.warning { background: #F59E0B; }
.drawer-bottom .stat-dot.success { background: #22C55E; }

.drawer-bottom .drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #94A3B8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms ease;
}

.drawer-bottom .drawer-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #F8FAFC;
}

/* ===== Content ===== */
.drawer-bottom .drawer-content {
  height: 152px;
  padding: 0 24px 24px;
  overflow-x: auto;
  overflow-y: hidden;
  display: flex;
  gap: 16px;
  align-items: flex-start;

  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 150ms ease 50ms,
    transform 150ms ease 50ms;
}

.drawer-bottom.open .drawer-content {
  opacity: 1;
  transform: translateY(0);
}

/* 自定义滚动条 */
.drawer-bottom .drawer-content::-webkit-scrollbar {
  height: 6px;
}

.drawer-bottom .drawer-content::-webkit-scrollbar-track {
  background: transparent;
}

.drawer-bottom .drawer-content::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}

/* ===== Event Card ===== */
.event-card {
  flex-shrink: 0;
  width: 280px;
  height: 120px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(30, 41, 59, 0.5);
  cursor: pointer;
  transition: all 150ms ease;
  display: flex;
  flex-direction: column;

  /* 依次出现动画 */
  opacity: 0;
  transform: translateX(20px);
}

.drawer-bottom.open .event-card {
  opacity: 1;
  transform: translateX(0);
}

.drawer-bottom.open .event-card:nth-child(1) { transition-delay: 0ms; }
.drawer-bottom.open .event-card:nth-child(2) { transition-delay: 30ms; }
.drawer-bottom.open .event-card:nth-child(3) { transition-delay: 60ms; }
.drawer-bottom.open .event-card:nth-child(4) { transition-delay: 90ms; }
.drawer-bottom.open .event-card:nth-child(5) { transition-delay: 120ms; }

.event-card:hover {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(51, 65, 85, 0.8);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.event-card.selected {
  border-color: rgba(0, 229, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.3);
}

.event-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.event-card-severity {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.event-card-severity.severity-5 {
  background: rgba(239, 68, 68, 0.2);
  color: #EF4444;
}

.event-card-severity.severity-4 {
  background: rgba(249, 115, 22, 0.2);
  color: #F97316;
}

.event-card-severity.severity-3 {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
}

.event-card-severity.severity-2 {
  background: rgba(34, 197, 94, 0.2);
  color: #22C55E;
}

.event-card-category {
  font-size: 10px;
  color: #64748B;
}

.event-card-title {
  font-size: 14px;
  font-weight: 500;
  color: #F8FAFC;
  line-height: 1.4;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
}

.event-card-location {
  font-size: 12px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-card-time {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: #64748B;
}
```

---

## 4. 悬浮工具栏按钮功能

### 4.1 工具栏布局

```
位置: 左下角, left: 24px, bottom: 24px

收起状态 (仅主菜单):
┌───┐
│ ≡ │  ← 点击展开/收起
└───┘

展开状态 (7个按钮):
┌───┐
│ ≡ │  主菜单 - 始终可见
├───┤
│ 📊 │  分析面板 (A) - 右侧抽屉
├───┤
│ 📋 │  事件列表 (E) - 底部抽屉
├───┤
│ 👥 │  角色详情 (R) - 左侧抽屉
├───┤
│ 🌙 │  主题切换 (T) - 深色/浅色
├───┤
│ ⚙️ │  设置 (S) - 弹窗
├───┤
│ 🔄 │  刷新 (F5) - 数据刷新
└───┘
```

### 4.2 按钮展开动画时间线

```
展开动画 (总时长: 350ms)

按钮依次出现:

按钮1 (≡ 主菜单):
  - 始终可见，不参与动画
  - opacity: 1, transform: none

按钮2 (📊 分析): 延迟 0ms
  0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
  100ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
  200ms: opacity: 1, transform: translateX(0) scale(1)

按钮3 (📋 事件): 延迟 50ms
  0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
  150ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
  250ms: opacity: 1, transform: translateX(0) scale(1)

按钮4 (👥 角色): 延迟 100ms
  0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
  200ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
  300ms: opacity: 1, transform: translateX(0) scale(1)

按钮5 (🌙 主题): 延迟 150ms
按钮6 (⚙️ 设置): 延迟 200ms
按钮7 (🔄 刷新): 延迟 250ms
... 以此类推
```

### 4.3 按钮功能详细说明

#### 按钮 1: 主菜单 (≡)

| 属性 | 值 |
|------|-----|
| 图标 | Menu (≡) |
| 快捷键 | Esc |
| 功能 | 展开/收起工具栏 |
| 激活条件 | 工具栏展开时 |
| 特殊行为 | 始终可见，不参与展开动画 |

```tsx
// 实现代码
const handleMenuClick = () => {
  setExpanded(!expanded);
};
```

#### 按钮 2: 分析面板 (📊)

| 属性 | 值 |
|------|-----|
| 图标 | BarChart2 (📊) |
| 快捷键 | A |
| 功能 | 切换右侧抽屉 (分析结果) |
| 激活条件 | 右侧抽屉打开时 |
| 关联组件 | DrawerRight |

```tsx
// 实现代码
const handleAnalysisClick = () => {
  rightDrawer.toggle();
};

// 激活状态判断
const isActive = rightDrawer.isOpen;
```

#### 按钮 3: 事件列表 (📋)

| 属性 | 值 |
|------|-----|
| 图标 | List (📋) |
| 快捷键 | E |
| 功能 | 切换底部抽屉 (事件列表) |
| 激活条件 | 底部抽屉打开时 |
| 关联组件 | DrawerBottom |

```tsx
// 实现代码
const handleEventsClick = () => {
  bottomDrawer.toggle();
};

// 激活状态判断
const isActive = bottomDrawer.isOpen;
```

#### 按钮 4: 角色详情 (👥)

| 属性 | 值 |
|------|-----|
| 图标 | Users (👥) |
| 快捷键 | R |
| 功能 | 切换左侧抽屉 (角色详情) |
| 激活条件 | 左侧抽屉打开时 |
| 关联组件 | DrawerLeft |

```tsx
// 实现代码
const handleRolesClick = () => {
  leftDrawer.toggle();
};

// 激活状态判断
const isActive = leftDrawer.isOpen;
```

#### 按钮 5: 主题切换 (🌙/☀️)

| 属性 | 值 |
|------|-----|
| 图标 | Moon (🌙) / Sun (☀️) |
| 快捷键 | T |
| 功能 | 深色/浅色主题切换 |
| 激活条件 | 无 (无持续激活状态) |
| 特殊行为 | 图标根据当前主题变化 |

```tsx
// 实现代码
const handleThemeClick = () => {
  toggleTheme();
};

// 图标显示
const ThemeIcon = theme === 'dark' ? Moon : Sun;
```

#### 按钮 6: 设置 (⚙️)

| 属性 | 值 |
|------|-----|
| 图标 | Settings (⚙️) |
| 快捷键 | S |
| 功能 | 打开设置弹窗 |
| 激活条件 | 设置弹窗打开时 |
| 关联组件 | SettingsModal |

```tsx
// 实现代码
const handleSettingsClick = () => {
  settingsModal.open();
};

// 激活状态判断
const isActive = settingsModal.isOpen;
```

#### 按钮 7: 刷新 (🔄)

| 属性 | 值 |
|------|-----|
| 图标 | RefreshCw (🔄) |
| 快捷键 | F5 |
| 功能 | 重新获取数据并分析 |
| 激活条件 | 无 |
| 特殊行为 | 刷新时图标旋转 |

```tsx
// 实现代码
const handleRefreshClick = async () => {
  setIsRefreshing(true);
  try {
    await data.refresh();
  } finally {
    setIsRefreshing(false);
  }
};

// 加载状态
const isLoading = isRefreshing;

// 图标旋转动画
// CSS: .toolbar-btn.loading svg { animation: spin 1s linear infinite; }
```

### 4.4 快捷键处理

```tsx
// 快捷键映射表
const SHORTCUT_MAP: Record<string, string> = {
  'Escape': 'menu',
  'a': 'analysis',
  'A': 'analysis',
  'e': 'events',
  'E': 'events',
  'r': 'roles',
  'R': 'roles',
  't': 'theme',
  'T': 'theme',
  's': 'settings',
  'S': 'settings',
  'F5': 'refresh',
};

// 按钮动作映射
const BUTTON_ACTIONS: Record<string, () => void> = {
  menu: () => setExpanded(!expanded),
  analysis: () => rightDrawer.toggle(),
  events: () => bottomDrawer.toggle(),
  roles: () => leftDrawer.toggle(),
  theme: () => toggleTheme(),
  settings: () => settingsModal.open(),
  refresh: () => data.refresh(),
};

// 键盘事件处理
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // 忽略输入框内的按键
    const target = e.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      return;
    }

    const buttonId = SHORTCUT_MAP[e.key];
    if (buttonId) {
      e.preventDefault();
      const action = BUTTON_ACTIONS[buttonId];
      if (action) {
        action();
      }
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [expanded, rightDrawer, bottomDrawer, leftDrawer, theme, settingsModal, data]);
```

### 4.5 完整 CSS 代码

```css
/* ========================================
   悬浮工具栏
   ======================================== */

.toolbar {
  position: fixed;
  left: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 600;
}

/* ===== 按钮基础 ===== */
.toolbar-btn {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 1px solid rgba(30, 41, 59, 0.8);
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 初始隐藏 (非主按钮) */
  opacity: 0;
  transform: translateX(-20px) scale(0.8);
  pointer-events: none;

  /* 过渡 */
  transition:
    opacity 200ms cubic-bezier(0.4, 0, 0.2, 1),
    transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
    background 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease;
}

/* 主按钮 - 始终可见 */
.toolbar-btn.primary {
  opacity: 1;
  transform: none;
  pointer-events: auto;
}

/* ===== 展开状态 ===== */
.toolbar.expanded .toolbar-btn {
  opacity: 1;
  transform: translateX(0) scale(1);
  pointer-events: auto;
}

/* 依次展开延迟 */
.toolbar.expanded .toolbar-btn:nth-child(1) { transition-delay: 0ms; }
.toolbar.expanded .toolbar-btn:nth-child(2) { transition-delay: 50ms; }
.toolbar.expanded .toolbar-btn:nth-child(3) { transition-delay: 100ms; }
.toolbar.expanded .toolbar-btn:nth-child(4) { transition-delay: 150ms; }
.toolbar.expanded .toolbar-btn:nth-child(5) { transition-delay: 200ms; }
.toolbar.expanded .toolbar-btn:nth-child(6) { transition-delay: 250ms; }
.toolbar.expanded .toolbar-btn:nth-child(7) { transition-delay: 300ms; }

/* ===== 收起动画 (反向延迟) ===== */
.toolbar:not(.expanded) .toolbar-btn:not(.primary) {
  opacity: 0;
  transform: translateX(-20px) scale(0.8);
  pointer-events: none;
}

.toolbar:not(.expanded) .toolbar-btn:nth-child(7) { transition-delay: 0ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(6) { transition-delay: 30ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(5) { transition-delay: 60ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(4) { transition-delay: 90ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(3) { transition-delay: 120ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(2) { transition-delay: 150ms; }

/* ===== 悬停状态 ===== */
.toolbar-btn:hover:not(.disabled) {
  transform: translateY(-4px) scale(1.05);
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);

  box-shadow:
    0 8px 32px rgba(0, 229, 255, 0.2),
    0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* 主按钮悬停保持可见 */
.toolbar-btn.primary:hover {
  opacity: 1;
  transform: translateY(-4px) scale(1.05);
}

/* ===== 激活状态 ===== */
.toolbar-btn.active {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
  border-color: transparent;

  box-shadow:
    0 0 24px rgba(0, 229, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.toolbar-btn.active:hover {
  transform: translateY(-2px);
  box-shadow:
    0 4px 24px rgba(0, 229, 255, 0.5),
    0 0 40px rgba(0, 229, 255, 0.3);
}

/* ===== 禁用状态 ===== */
.toolbar-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* ===== 按下状态 ===== */
.toolbar-btn:active:not(.disabled) {
  transform: translateY(-2px) scale(0.98);
  transition-duration: 50ms;
}

/* ===== 图标样式 ===== */
.toolbar-btn svg {
  width: 24px;
  height: 24px;
  color: #94A3B8;
  transition: color 150ms ease;
}

.toolbar-btn:hover:not(.disabled) svg {
  color: #00E5FF;
}

.toolbar-btn.active svg {
  color: #FFFFFF;
}

/* ===== 加载状态 ===== */
.toolbar-btn.loading svg {
  animation: toolbar-spin 1s linear infinite;
}

@keyframes toolbar-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ===== Tooltip ===== */
.toolbar-btn[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);

  padding: 8px 12px;
  border-radius: 6px;

  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);

  font-size: 12px;
  font-weight: 500;
  color: #F8FAFC;
  white-space: nowrap;

  opacity: 0;
  visibility: hidden;
  transition: opacity 150ms ease, visibility 150ms ease;

  pointer-events: none;
  z-index: 10;
}

.toolbar-btn:hover[data-tooltip]::after {
  opacity: 1;
  visibility: visible;
}

/* ===== 快捷键提示 ===== */
.toolbar-btn .shortcut {
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translate(0, -50%);

  margin-left: calc(100% + 80px);

  padding: 4px 6px;
  border-radius: 4px;

  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(51, 65, 85, 0.5);

  font-size: 10px;
  font-weight: 500;
  font-family: 'JetBrains Mono', monospace;
  color: #64748B;

  opacity: 0;
  visibility: hidden;
  transition: opacity 150ms ease, visibility 150ms ease;

  pointer-events: none;
}

.toolbar-btn:hover .shortcut {
  opacity: 1;
  visibility: visible;
}
```

---

## 5. 动画参数汇总

### 5.1 抽屉动画对比

| 参数 | 右侧抽屉 | 左侧抽屉 | 底部抽屉 |
|------|----------|----------|----------|
| 宽度/高度 | 360px | 320px | 48px→200px |
| 展开时长 | 300ms | 280ms | 250ms |
| 收起时长 | 250ms | 240ms | 200ms |
| 初始位置 | translateX(100%) | translateX(-100%) | height: 48px |
| 内容延迟 | 150ms | 140ms | 50ms |
| 缓动函数 | cubic-bezier(0.4, 0, 0.2, 1) | 同左 | 同左 |
| Z-index | 900 | 700 | 800 |

### 5.2 工具栏动画参数

| 参数 | 值 |
|------|-----|
| 按钮间距 | 12px |
| 展开延迟 | 0-300ms (每个按钮间隔50ms) |
| 收起延迟 | 0-150ms (每个按钮间隔30ms) |
| 初始状态 | opacity: 0, translateX(-20px), scale(0.8) |
| 结束状态 | opacity: 1, translateX(0), scale(1) |
| 过渡时长 | 200ms |
| 缓动函数 | cubic-bezier(0.4, 0, 0.2, 1) |

---

**文档完成** ✓
