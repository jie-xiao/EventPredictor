# EventPredictor UI 完整设计规范

> **版本**: v4.0 | **日期**: 2026-03-14 | **用途**: 前端开发完整参考

---

## 目录

1. [抽屉展开动画效果](#1-抽屉展开动画效果)
2. [悬浮工具栏按钮及功能](#2-悬浮工具栏按钮及功能)
3. [事件标记脉动动画效果](#3-事件标记脉动动画效果)
4. [颜色规范和渐变光效](#4-颜色规范和渐变光效)
5. [字体和间距规范](#5-字体和间距规范)

---

## 1. 抽屉展开动画效果

### 1.1 动画系统总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              抽屉动画三要素                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    面板移动               内容淡入               背景响应                   │
│   ┌─────────┐           ┌─────────┐           ┌─────────┐                │
│   │transform│           │ opacity │           │  width  │                │
│   │translate│           │  delay  │           │ margin  │                │
│   │ 300ms   │           │ 150ms   │           │ 300ms   │                │
│   └─────────┘           └─────────┘           └─────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 三抽屉参数速查表

| 抽屉 | 尺寸 | 展开时长 | 收起时长 | Z-index | 内容延迟 |
|------|------|----------|----------|---------|----------|
| **右侧** | 360px | 300ms | 250ms | 900 | 150ms |
| **左侧** | 320px | 280ms | 240ms | 700 | 140ms |
| **底部** | 48→200px | 250ms | 200ms | 800 | 50ms |

### 1.3 右侧抽屉 (360px) - 分析面板

#### 完整结构

```
┌────────────────────────────────────┐
│ ◀ 趋势预测                   [×]  │  Header (56px)
├────────────────────────────────────┤
│                                    │
│  ┌────────────┐    ┌─────────┐    │
│  │     ↑      │    │   75%   │    │  趋势 + 置信度
│  │    上涨    │    │   ○     │    │
│  └────────────┘    └─────────┘    │
│                                    │
│  ████████████████░░░░░░            │  置信度进度条
│                                    │
├────────────────────────────────────┤
│  📌 关键洞察                       │  Section 1
│  • 美方可能增派舰艇                 │
│  • 中方或将加强巡航                 │
├────────────────────────────────────┤
│  ⚠️ 风险: 高    🔥 冲突: 3        │  Section 2
├────────────────────────────────────┤
│  ⏱ 时间线                          │  Section 3
│  ●───○───○                         │
├────────────────────────────────────┤
│  📋 共识                           │  Section 4
│  [外交磋商] [区域稳定]              │
├────────────────────────────────────┤
│  [    查看完整分析 →    ]          │  Footer (80px)
└────────────────────────────────────┘
```

#### 毫秒级动画时间线

```
右侧抽屉展开动画 (总时长: 300ms)

0ms      50ms     100ms    150ms    200ms    250ms    300ms
|---------|---------|---------|---------|---------|---------|

【抽屉面板 translateX】
100%─────85%─────65%─────45%─────25%─────10%──────0%

【透明度 opacity】
0.9──────────────────────────────────────────────────1

【遮罩层 opacity】
0─────────────────────────────────────────────────0.4

【地球 width】 (延迟50ms)
100%─────────────────────────────────────────calc(100%-360px)

【内容 opacity】 (延迟150ms)
0──────────────────────────────────────────────1

【Section 依次出现】
Sec1: 300ms延迟 → Sec2: 350ms → Sec3: 400ms → Sec4: 450ms → Footer: 500ms
```

#### 完整 CSS

```css
/* ===== 右侧抽屉 - 分析面板 ===== */
.drawer-right {
  position: fixed;
  top: 0;
  right: 0;
  width: 360px;
  height: 100vh;
  z-index: 900;

  transform: translateX(100%);
  opacity: 0.9;
  visibility: hidden;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);

  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 300ms;
}

.drawer-right.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 0ms;
}

/* Header */
.drawer-right .header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.05), rgba(0, 119, 255, 0.05));
}

/* Content - 淡入动画 */
.drawer-right .content {
  padding: 20px;
  height: calc(100vh - 136px);
  overflow-y: auto;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 200ms ease 150ms, transform 200ms ease 150ms;
}

.drawer-right.open .content {
  opacity: 1;
  transform: translateY(0);
}

/* Section 依次出现 */
.drawer-section {
  margin-bottom: 24px;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 150ms ease, transform 150ms ease;
}

.drawer-right.open .drawer-section:nth-child(1) { opacity: 1; transform: none; transition-delay: 300ms; }
.drawer-right.open .drawer-section:nth-child(2) { opacity: 1; transform: none; transition-delay: 350ms; }
.drawer-right.open .drawer-section:nth-child(3) { opacity: 1; transform: none; transition-delay: 400ms; }
.drawer-right.open .drawer-section:nth-child(4) { opacity: 1; transform: none; transition-delay: 450ms; }

/* Footer */
.drawer-right .footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  border-top: 1px solid rgba(30, 41, 59, 0.6);
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 150ms ease 500ms, transform 150ms ease 500ms;
}

.drawer-right.open .footer {
  opacity: 1;
  transform: translateY(0);
}
```

### 1.4 左侧抽屉 (320px) - 角色详情

#### 完整结构

```
┌────────────────────────────────┐
│ [×]                      16角色│  Header (56px)
├────────────────────────────────┤
│ 🔍 搜索角色...                 │  Search (48px)
├────────────────────────────────┤
│ [全部][政府][企业][民众][媒体] │  Tabs (40px)
├────────────────────────────────┤
│ ┌────────────────────────────┐│
│ │ 🇨🇳 中国政府               ││
│ │ 立场: 维护主权             ││  Role Card 1
│ │ 置信度: ████████░░ 82%    ││
│ └────────────────────────────┘│
│ ┌────────────────────────────┐│
│ │ 🇺🇸 美国政府               ││  Role Card 2
│ │ ...                        ││
│ └────────────────────────────┘│
│ ... 更多角色 (可滚动)          │
└────────────────────────────────┘
```

#### 毫秒级动画时间线

```
左侧抽屉展开动画 (总时长: 280ms)

0ms      56ms     112ms    168ms    224ms    280ms
|---------|---------|---------|---------|---------|

【抽屉面板 translateX】
-100%────-75%────-50%────-25%────-10%─────0%

【地球响应】 (延迟40ms)
width: 100% → calc(100%-320px)
margin-left: 0 → 320px

【内容淡入】 (延迟140ms)

【角色卡片依次出现】 (每个延迟50ms)
卡片1: 280ms → 卡片2: 330ms → 卡片3: 380ms → 卡片4: 430ms → ...
```

#### 完整 CSS

```css
/* ===== 左侧抽屉 - 角色详情 ===== */
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

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);

  transition:
    transform 280ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 180ms ease,
    visibility 0ms linear 280ms;
}

.drawer-left.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
}

/* Content 淡入 */
.drawer-left .content {
  padding: 16px;
  height: calc(100vh - 144px);
  overflow-y: auto;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 180ms ease 140ms, transform 180ms ease 140ms;
}

.drawer-left.open .content {
  opacity: 1;
  transform: translateY(0);
}

/* 角色卡片依次出现 */
.role-card {
  padding: 16px;
  border-radius: 10px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(30, 41, 59, 0.5);
  margin-bottom: 12px;
  cursor: pointer;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 150ms ease;
}

.drawer-left.open .role-card { opacity: 1; transform: translateX(0); }
.drawer-left.open .role-card:nth-child(1) { transition-delay: 280ms; }
.drawer-left.open .role-card:nth-child(2) { transition-delay: 330ms; }
.drawer-left.open .role-card:nth-child(3) { transition-delay: 380ms; }
.drawer-left.open .role-card:nth-child(4) { transition-delay: 430ms; }
.drawer-left.open .role-card:nth-child(5) { transition-delay: 480ms; }
.drawer-left.open .role-card:nth-child(6) { transition-delay: 530ms; }

.role-card:hover {
  background: rgba(30, 41, 59, 0.5);
  transform: translateX(4px);
}
```

### 1.5 底部抽屉 (48→200px) - 事件列表

#### 完整结构

```
收起状态 (48px):
┌────────────────────────────────────────────────────────────────┐
│  ▼ 事件列表 (5)   🔴2 紧急 · 🟡1 重要 · 🟢2 一般      [×]    │
└────────────────────────────────────────────────────────────────┘

展开状态 (200px):
┌────────────────────────────────────────────────────────────────┐
│  ▲ 事件列表 (5)   🔴2 紧急 · 🟡1 重要 · 🟢2 一般      [×]    │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────┐│
│  │🔴 紧急   │ │🔴 紧急   │ │🟡 重要   │ │🟢 一般   │ │🟢   ││
│  │美军航母  │ │美联储    │ │中美贸易  │ │气候峰会  │ │...  ││
│  │进入南海  │ │利率决议  │ │谈判      │ │          │ │     ││
│  │📍 南海   │ │📍 美国   │ │📍 北京   │ │📍 日内瓦 │ │     ││
│  │🕐 2h前   │ │🕐 5h前   │ │🕐 1d前   │ │🕐 2d前   │ │     ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────┘│
│  ←──────────────────── 横向滚动 ─────────────────────→       │
└────────────────────────────────────────────────────────────────┘
```

#### 毫秒级动画时间线

```
底部抽屉展开动画 (总时长: 250ms)

0ms      50ms     100ms    150ms    200ms    250ms
|---------|---------|---------|---------|---------|

【高度】
48px─────80px─────120px───160px───185px───200px

【展开图标旋转】
0deg──────────────────────────────────180deg (200ms完成)

【内容淡入】 (延迟50ms)

【事件卡片依次出现】 (每个延迟30ms)
卡片1: 100ms → 卡片2: 130ms → 卡片3: 160ms → 卡片4: 190ms → 卡片5: 220ms
```

#### 完整 CSS

```css
/* ===== 底部抽屉 - 事件列表 ===== */
.drawer-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 800;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);
  overflow: hidden;

  transition: height 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-bottom.open {
  height: 200px;
}

/* Header - 可点击 */
.drawer-bottom .header {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

/* 展开图标旋转 */
.drawer-bottom .expand-icon {
  transition: transform 200ms ease;
}

.drawer-bottom.open .expand-icon {
  transform: rotate(180deg);
}

/* Content 淡入 */
.drawer-bottom .content {
  height: 152px;
  padding: 0 24px 24px;
  overflow-x: auto;
  display: flex;
  gap: 16px;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 150ms ease 50ms, transform 150ms ease 50ms;
}

.drawer-bottom.open .content {
  opacity: 1;
  transform: translateY(0);
}

/* 事件卡片依次出现 */
.event-card {
  flex-shrink: 0;
  width: 280px;
  height: 120px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(30, 41, 59, 0.5);
  cursor: pointer;
  opacity: 0;
  transform: translateX(20px);
  transition: all 150ms ease;
}

.drawer-bottom.open .event-card { opacity: 1; transform: translateX(0); }
.drawer-bottom.open .event-card:nth-child(1) { transition-delay: 100ms; }
.drawer-bottom.open .event-card:nth-child(2) { transition-delay: 130ms; }
.drawer-bottom.open .event-card:nth-child(3) { transition-delay: 160ms; }
.drawer-bottom.open .event-card:nth-child(4) { transition-delay: 190ms; }
.drawer-bottom.open .event-card:nth-child(5) { transition-delay: 220ms; }

.event-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
```

---

## 2. 悬浮工具栏按钮及功能

### 2.1 工具栏布局

```
位置: 左下角 (left: 24px, bottom: 24px)

收起状态:                    展开状态:

┌───┐                        ┌───┐
│ ≡ │  主菜单                │ ≡ │  主菜单 (0ms)
└───┘                        ├───┤
                             │ 📊 │  分析面板 (50ms)
                             ├───┤
                             │ 📋 │  事件列表 (100ms)
                             ├───┤
                             │ 👥 │  角色详情 (150ms)
                             ├───┤
                             │ 🌙 │  主题切换 (200ms)
                             ├───┤
                             │ ⚙️ │  设置 (250ms)
                             ├───┤
                             │ 🔄 │  刷新 (300ms)
                             └───┘
```

### 2.2 七个按钮功能详解

| # | 按钮 | 快捷键 | 功能 | 激活条件 | 特殊行为 |
|---|------|--------|------|----------|----------|
| 1 | ≡ | Esc | 展开/收起工具栏 | 工具栏展开时 | 始终可见 |
| 2 | 📊 | A | 切换右侧抽屉 | 右侧打开时 | - |
| 3 | 📋 | E | 切换底部抽屉 | 底部打开时 | - |
| 4 | 👥 | R | 切换左侧抽屉 | 左侧打开时 | - |
| 5 | 🌙/☀️ | T | 主题切换 | 无 | 图标变化 |
| 6 | ⚙️ | S | 打开设置 | 弹窗打开时 | - |
| 7 | 🔄 | F5 | 刷新数据 | 无 | 图标旋转 |

### 2.3 按钮状态样式

| 状态 | 背景 | 边框 | 图标色 | 变换 | 阴影 |
|------|------|------|--------|------|------|
| **默认** | rgba(15,23,42,0.9) | rgba(30,41,59,0.8) | #94A3B8 | none | none |
| **悬停** | rgba(0,229,255,0.1) | rgba(0,229,255,0.3) | #00E5FF | translateY(-4px) scale(1.05) | 发光 |
| **激活** | 渐变 cyan→blue | none | #FFFFFF | none | 强发光 |
| **禁用** | rgba(30,41,59,0.5) | none | #475569 | none | none |
| **加载** | 默认 | 默认 | #94A3B8 | 图标旋转 | none |

### 2.4 展开/收起动画时间线

```
展开动画 (总时长 350ms):

按钮2 (📊): 延迟 0ms
  0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
  100ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
  200ms: opacity: 1, transform: translateX(0) scale(1)

按钮3 (📋): 延迟 50ms
  0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
  150ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
  250ms: opacity: 1, transform: translateX(0) scale(1)

... 以此类推，每个按钮延迟 50ms

收起动画 (反向):
按钮7 → 按钮2，每个延迟 30ms
```

### 2.5 完整 CSS

```css
/* ===== 工具栏容器 ===== */
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

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 初始隐藏 */
  opacity: 0;
  transform: translateX(-20px) scale(0.8);
  pointer-events: none;

  transition:
    opacity 200ms cubic-bezier(0.4, 0, 0.2, 1),
    transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
    background 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease;
}

/* 主按钮始终可见 */
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

/* ===== 悬停状态 ===== */
.toolbar-btn:hover:not(.disabled) {
  transform: translateY(-4px) scale(1.05);
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);
  box-shadow:
    0 8px 32px rgba(0, 229, 255, 0.2),
    0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* ===== 激活状态 ===== */
.toolbar-btn.active {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
  border-color: transparent;
  box-shadow:
    0 0 24px rgba(0, 229, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.toolbar-btn.active svg {
  color: #FFFFFF;
}

/* ===== 加载状态 ===== */
.toolbar-btn.loading svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

/* ===== Tooltip ===== */
.toolbar-btn::after {
  content: attr(data-tooltip);
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);
  padding: 8px 12px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(30, 41, 59, 0.8);
  font-size: 12px;
  color: #F8FAFC;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 150ms ease, visibility 150ms ease;
  pointer-events: none;
  z-index: 10;
}

.toolbar-btn:hover::after {
  opacity: 1;
  visibility: visible;
}
```

---

## 3. 事件标记脉动动画效果

### 3.1 标记结构

```
                    ┌── 外层光晕 (pulse-outer)
                    │      尺寸: 40px → 100px
                    │      透明度: 0.6 → 0
                    │      周期: 2s, 延迟 0.5s
                    │
        ┌───────────┼───────────┐
        │     ┌─────┼─────┐     │
        │     │  ┌──┼──┐  │     │
        │     │  │核心│  │     │  ← 核心点 (12px)
        │     │  │点 │  │     │     固定不缩放
        │     │  └──┼──┘  │     │     带发光阴影
        │     │     │     │     │
        │     └─────┼─────┘     │
        │           │           │
        └───────────┼───────────┘
                    │
                    └── 内层光晕 (pulse-inner)
                           尺寸: 24px → 60px
                           透明度: 0.8 → 0
                           周期: 2s, 无延迟
```

### 3.2 脉动动画时间线

```
脉动周期: 2000ms (2秒)

内层光晕 (pulse-inner):
0ms      500ms    1000ms   1500ms   2000ms
|---------|---------|---------|---------|
scale:    1.0       1.75      2.5       1.0
opacity:  0.8       0.4       0         0.8

外层光晕 (pulse-outer) - 延迟 500ms:
0ms      500ms    1000ms   1500ms   2000ms   2500ms
|---------|---------|---------|---------|---------|
[等待]    │
          scale:    1.0       1.75      2.5       1.0
          opacity:  0.6       0.3       0         0.6

形成波纹效果:
时刻 0ms:    ●           (核心)
时刻 500ms:  ●○          (内层开始扩散)
时刻 1000ms: ●◯○         (内层继续, 外层开始)
时刻 1500ms: ●◯ ○        (内层淡出, 外层扩散)
时刻 2000ms: ●   ○       (内层消失, 外层继续)
```

### 3.3 严重程度颜色

| 级别 | 颜色 | 色值 | 发光色 | 用途 |
|------|------|------|--------|------|
| 5-紧急 | 🔴 红色 | #EF4444 | rgba(239,68,68,0.6) | 紧急事件 |
| 4-高危 | 🟠 橙色 | #F97316 | rgba(249,115,22,0.6) | 高危事件 |
| 3-重要 | 🟡 黄色 | #F59E0B | rgba(245,158,11,0.6) | 重要事件 |
| 2-一般 | 🟢 绿色 | #22C55E | rgba(34,197,94,0.6) | 一般事件 |
| 1-低 | 🔵 蓝色 | #3B82F6 | rgba(59,130,246,0.6) | 低优先级 |

### 3.4 完整 CSS

```css
/* ===== 事件标记容器 ===== */
.event-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 400;
}

/* ===== 核心点 ===== */
.event-marker .core {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 3;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

/* ===== 内层脉动 ===== */
.event-marker .pulse-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  pointer-events: none;
  animation: pulseInner 2s ease-out infinite;
}

/* ===== 外层脉动 ===== */
.event-marker .pulse-outer {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  pointer-events: none;
  animation: pulseOuter 2s ease-out infinite 0.5s;
}

/* ===== 脉动动画 ===== */
@keyframes pulseInner {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.8; }
  100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
}

@keyframes pulseOuter {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
}

/* ===== Severity 5 - 紧急 (红色) ===== */
.event-marker[data-severity="5"] .core {
  background: #EF4444;
  box-shadow: 0 0 8px #EF4444, 0 0 16px rgba(239, 68, 68, 0.6), 0 0 32px rgba(239, 68, 68, 0.3);
}
.event-marker[data-severity="5"] .pulse-inner {
  border: 2px solid #EF4444;
  background: radial-gradient(circle, rgba(239, 68, 68, 0.4) 0%, rgba(239, 68, 68, 0.2) 40%, transparent 70%);
}
.event-marker[data-severity="5"] .pulse-outer {
  border: 2px solid rgba(239, 68, 68, 0.6);
  background: radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 60%);
}

/* ===== Severity 4 - 高危 (橙色) ===== */
.event-marker[data-severity="4"] .core {
  background: #F97316;
  box-shadow: 0 0 6px #F97316, 0 0 12px rgba(249, 115, 22, 0.6), 0 0 24px rgba(249, 115, 22, 0.3);
}
.event-marker[data-severity="4"] .pulse-inner {
  border: 2px solid #F97316;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, rgba(249, 115, 22, 0.2) 40%, transparent 70%);
}
.event-marker[data-severity="4"] .pulse-outer {
  border: 2px solid rgba(249, 115, 22, 0.6);
  background: radial-gradient(circle, rgba(249, 115, 22, 0.2) 0%, transparent 60%);
}

/* ===== Severity 3 - 重要 (黄色) ===== */
.event-marker[data-severity="3"] .core {
  background: #F59E0B;
  box-shadow: 0 0 5px #F59E0B, 0 0 10px rgba(245, 158, 11, 0.6), 0 0 20px rgba(245, 158, 11, 0.3);
}
.event-marker[data-severity="3"] .pulse-inner {
  border: 2px solid #F59E0B;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.4) 0%, rgba(245, 158, 11, 0.2) 40%, transparent 70%);
}
.event-marker[data-severity="3"] .pulse-outer {
  border: 2px solid rgba(245, 158, 11, 0.6);
  background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, transparent 60%);
}

/* ===== Severity 2 - 一般 (绿色) ===== */
.event-marker[data-severity="2"] .core {
  background: #22C55E;
  box-shadow: 0 0 4px #22C55E, 0 0 8px rgba(34, 197, 94, 0.6), 0 0 16px rgba(34, 197, 94, 0.3);
}
.event-marker[data-severity="2"] .pulse-inner {
  border: 2px solid #22C55E;
  background: radial-gradient(circle, rgba(34, 197, 94, 0.4) 0%, rgba(34, 197, 94, 0.2) 40%, transparent 70%);
}
.event-marker[data-severity="2"] .pulse-outer {
  border: 2px solid rgba(34, 197, 94, 0.6);
  background: radial-gradient(circle, rgba(34, 197, 94, 0.2) 0%, transparent 60%);
}

/* ===== Severity 1 - 低 (蓝色) ===== */
.event-marker[data-severity="1"] .core {
  background: #3B82F6;
  box-shadow: 0 0 3px #3B82F6, 0 0 6px rgba(59, 130, 246, 0.6), 0 0 12px rgba(59, 130, 246, 0.3);
}
.event-marker[data-severity="1"] .pulse-inner {
  border: 2px solid #3B82F6;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, rgba(59, 130, 246, 0.2) 40%, transparent 70%);
}
.event-marker[data-severity="1"] .pulse-outer {
  border: 2px solid rgba(59, 130, 246, 0.6);
  background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 60%);
}

/* ===== 悬停效果 ===== */
.event-marker:hover { z-index: 410; }
.event-marker:hover .core { transform: translate(-50%, -50%) scale(1.5); }
.event-marker:hover .pulse-inner,
.event-marker:hover .pulse-outer { animation-duration: 1s; }

/* ===== 选中效果 ===== */
.event-marker.selected { z-index: 420; }
.event-marker.selected .core { transform: translate(-50%, -50%) scale(1.8); }
.event-marker.selected .pulse-inner,
.event-marker.selected .pulse-outer { animation-duration: 1.5s; border-width: 3px; }
```

---

## 4. 颜色规范和渐变光效

### 4.1 颜色系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              颜色层级                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   背景色              主色调              语义色              文字色       │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐    │
│  │#0A0E1A  │        │#00E5FF  │        │#EF4444  │        │#F8FAFC  │    │
│  │#0F172A  │        │#0077FF  │        │#F59E0B  │        │#94A3B8  │    │
│  │#1E293B  │        │#8B5CF6  │        │#10B981  │        │#64748B  │    │
│  └─────────┘        └─────────┘        └─────────┘        └─────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 完整颜色 Token

```css
:root {
  /* ===== 背景色 ===== */
  --bg-primary: #0A0E1A;        /* 页面主背景 */
  --bg-secondary: #0F172A;      /* 卡片/面板 */
  --bg-tertiary: #1E293B;       /* 抬起元素 */
  --bg-overlay: rgba(0, 0, 0, 0.4);  /* 遮罩 */

  /* ===== 主色调 ===== */
  --accent-cyan: #00E5FF;       /* 主强调 - 科技青 */
  --accent-blue: #0077FF;       /* 次强调 - 科技蓝 */
  --accent-purple: #8B5CF6;     /* 特殊强调 */
  --accent-pink: #EC4899;       /* 点缀 */

  /* ===== 语义色 ===== */
  --status-danger: #EF4444;     /* 紧急/错误 */
  --status-warning: #F59E0B;    /* 警告/重要 */
  --status-success: #10B981;    /* 成功/正常 */
  --status-info: #3B82F6;       /* 信息 */

  /* ===== 文字色 ===== */
  --text-primary: #F8FAFC;      /* 主要文字 15.2:1 */
  --text-secondary: #94A3B8;    /* 次要文字 5.1:1 */
  --text-muted: #64748B;        /* 辅助文字 3.5:1 */
  --text-disabled: #475569;     /* 禁用文字 */

  /* ===== 边框色 ===== */
  --border-default: #1E293B;    /* 默认边框 */
  --border-light: #334155;      /* 浅色边框 */
  --border-accent: #00E5FF;     /* 强调边框 */

  /* ===== 透明变体 ===== */
  --cyan-5: rgba(0, 229, 255, 0.05);
  --cyan-10: rgba(0, 229, 255, 0.1);
  --cyan-20: rgba(0, 229, 255, 0.2);
  --cyan-30: rgba(0, 229, 255, 0.3);
  --cyan-40: rgba(0, 229, 255, 0.4);

  --danger-10: rgba(239, 68, 68, 0.1);
  --danger-20: rgba(239, 68, 68, 0.2);
  --danger-30: rgba(239, 68, 68, 0.3);

  --warning-10: rgba(245, 158, 11, 0.1);
  --warning-20: rgba(245, 158, 11, 0.2);
  --warning-30: rgba(245, 158, 11, 0.3);

  --success-10: rgba(16, 185, 129, 0.1);
  --success-20: rgba(16, 185, 129, 0.2);
  --success-30: rgba(16, 185, 129, 0.3);
}
```

### 4.3 渐变规范

```css
/* ===== 主渐变 ===== */
.gradient-primary {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
}

.gradient-hover {
  background: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%);
}

/* ===== 趋势渐变 ===== */
.gradient-up {
  background: linear-gradient(90deg, #10B981 0%, #22C55E 100%);
}

.gradient-down {
  background: linear-gradient(90deg, #EF4444 0%, #F97316 100%);
}

.gradient-neutral {
  background: linear-gradient(90deg, #F59E0B 0%, #EAB308 100%);
}

/* ===== 文字渐变 ===== */
.gradient-text {
  background: linear-gradient(90deg, #00E5FF 0%, #0077FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ===== 边框渐变 ===== */
.gradient-border {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--bg-secondary), var(--bg-secondary)) padding-box,
    linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 119, 255, 0.3)) border-box;
}

/* ===== 背景渐变 ===== */
.gradient-bg-page {
  background: radial-gradient(ellipse at 50% 0%, rgba(0, 229, 255, 0.05) 0%, transparent 50%),
              linear-gradient(180deg, #0A0E1A 0%, #0F172A 100%);
}

.gradient-bg-card {
  background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
}
```

### 4.4 发光效果

```css
/* ===== 预设发光 ===== */
.glow-cyan {
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.25);
}

.glow-cyan-strong {
  box-shadow:
    0 0 20px rgba(0, 229, 255, 0.25),
    0 0 40px rgba(0, 229, 255, 0.15),
    0 0 60px rgba(0, 229, 255, 0.1);
}

.glow-danger {
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
}

.glow-success {
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.glow-warning {
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
}

/* ===== 呼吸发光动画 ===== */
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); }
  50% { box-shadow: 0 0 40px rgba(0, 229, 255, 0.4); }
}

.breathe-glow {
  animation: breathe 3s ease-in-out infinite;
}

/* ===== 流光效果 ===== */
@keyframes flowing {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

.flowing-light {
  background: linear-gradient(90deg, transparent 0%, rgba(0, 229, 255, 0.4) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: flowing 3s linear infinite;
}

/* ===== 文字发光 ===== */
.text-glow-cyan {
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.text-glow-white {
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

/* ===== 光晕效果 ===== */
.halo-cyan {
  position: relative;
}

.halo-cyan::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0) 70%);
  pointer-events: none;
  z-index: -1;
}
```

### 4.5 颜色使用场景

```css
/* ===== 背景色使用 ===== */
body { background: var(--bg-primary); }
.card, .drawer { background: var(--bg-secondary); }
.modal, .dropdown { background: var(--bg-tertiary); }
.overlay { background: var(--bg-overlay); }

/* 悬停/选中背景 */
.btn:hover { background: var(--cyan-10); }
.btn.active, .card.selected { background: var(--cyan-20); }

/* ===== 主色使用 ===== */
.btn-primary { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); }
.text-link { color: var(--accent-blue); }
.text-highlight { color: var(--accent-cyan); }
.border-highlight { border-color: var(--accent-cyan); }
.glow { box-shadow: 0 0 20px var(--cyan-40); }

/* ===== 语义色使用 ===== */
.error, .severity-5 { color: var(--status-danger); background: var(--danger-10); }
.warning, .severity-3-4 { color: var(--status-warning); background: var(--warning-10); }
.success, .severity-1-2 { color: var(--status-success); background: var(--success-10); }
.info { color: var(--status-info); }

/* ===== 文字使用 ===== */
h1, h2, h3, p { color: var(--text-primary); }
.description, .label { color: var(--text-secondary); }
.timestamp, .meta { color: var(--text-muted); }
.disabled { color: var(--text-disabled); }

/* ===== 边框使用 ===== */
.card { border: 1px solid var(--border-default); }
.card:hover { border-color: var(--border-light); }
.card.selected { border-color: var(--border-accent); }
```

---

## 5. 字体和间距规范

### 5.1 字体系统

```css
:root {
  /* ===== 字体家族 ===== */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, monospace;
  --font-chinese: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  --font-display: 'Inter', 'PingFang SC', sans-serif;

  /* ===== 字体大小 ===== */
  --text-xs: 10px;      /* 极小 - 标签 */
  --text-sm: 12px;      /* 小号 - 次要信息 */
  --text-base: 14px;    /* 基础 - 正文 */
  --text-md: 16px;      /* 中号 - 小标题 */
  --text-lg: 20px;      /* 大号 - 标题 */
  --text-xl: 24px;      /* 超大 - 主标题 */
  --text-2xl: 32px;     /* 巨大 - 数据展示 */
  --text-3xl: 48px;     /* 特大 - 关键数据 */

  /* ===== 字重 ===== */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* ===== 行高 ===== */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  /* ===== 字间距 ===== */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

### 5.2 字体层级

```
┌─────────────────────────────────────────────────────────────────┐
│                        H1 - 页面主标题                           │
│                     24px / 700 / 1.25                           │
├─────────────────────────────────────────────────────────────────┤
│                      H2 - 区块标题                               │
│                    20px / 600 / 1.25                            │
├─────────────────────────────────────────────────────────────────┤
│                      H3 - 卡片标题                               │
│                    16px / 600 / 1.375                           │
├─────────────────────────────────────────────────────────────────┤
│                      Body - 正文                                 │
│                    14px / 400 / 1.5                             │
├─────────────────────────────────────────────────────────────────┤
│                     Caption - 说明文字                           │
│                    12px / 400 / 1.5                             │
├─────────────────────────────────────────────────────────────────┤
│                      Label - 标签                                │
│                  10px / 500 / 1 / uppercase                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 组件字体规范

```css
/* ===== Header ===== */
.header-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

.header-stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-none);
}

/* ===== 抽屉标题 ===== */
.drawer-title {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
}

.drawer-section-title {
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
}

/* ===== 卡片 ===== */
.card-title {
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
}

.card-description {
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
}

/* ===== 数据展示 ===== */
.data-value-lg {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-none);
  letter-spacing: -0.05em;
}

.data-value-md {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-none);
}

.data-value-sm {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
}

.data-label {
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
}

/* ===== 按钮 ===== */
.btn-text {
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
}

/* ===== 标签 ===== */
.tag-text {
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
}

/* ===== 时间 ===== */
.timestamp {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
}
```

### 5.4 间距系统 (4px 基准)

```css
:root {
  /* ===== 基础间距 ===== */
  --space-0: 0;
  --space-1: 4px;      /* 极小 */
  --space-2: 8px;      /* 小 */
  --space-3: 12px;     /* 中小 */
  --space-4: 16px;     /* 基础 */
  --space-5: 20px;     /* 中等 */
  --space-6: 24px;     /* 常用 */
  --space-8: 32px;     /* 大 */
  --space-10: 40px;    /* 较大 */
  --space-12: 48px;    /* 大区块 */
  --space-16: 64px;    /* 超大 */
  --space-20: 80px;    /* 区块 */
  --space-24: 96px;    /* 页面级 */

  /* ===== 圆角 ===== */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 20px;
  --radius-full: 9999px;
}
```

### 5.5 组件间距规范

```css
/* ===== Header ===== */
.header {
  height: 68px;
  padding: 0 var(--space-6);
  gap: var(--space-6);
}

/* ===== 卡片 ===== */
.card {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
}

.card-header {
  margin-bottom: var(--space-4);
  gap: var(--space-3);
}

.card-body {
  gap: var(--space-3);
}

.card-footer {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
}

/* ===== 事件卡片 ===== */
.event-card {
  width: 280px;
  height: 120px;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  margin-right: var(--space-4);
}

/* ===== 抽屉 ===== */
.drawer-header {
  height: 56px;
  padding: 0 var(--space-5);
}

.drawer-body {
  padding: var(--space-5);
  gap: var(--space-6);
}

.drawer-section {
  margin-bottom: var(--space-6);
}

/* ===== 按钮 ===== */
.btn-sm {
  padding: var(--space-1) var(--space-3);
}

.btn-md {
  padding: var(--space-2) var(--space-4);
}

.btn-lg {
  padding: var(--space-3) var(--space-6);
}

/* ===== 列表 ===== */
.list-item {
  padding: var(--space-3) var(--space-4);
  gap: var(--space-3);
}

/* ===== 工具栏 ===== */
.toolbar {
  gap: var(--space-3);
  left: var(--space-6);
  bottom: var(--space-6);
}

.toolbar-btn {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
}

/* ===== 网格 ===== */
.grid-sm { gap: var(--space-3); }
.grid-md { gap: var(--space-4); }
.grid-lg { gap: var(--space-6); }
.grid-xl { gap: var(--space-8); }

/* ===== 标签组 ===== */
.tag-group {
  gap: var(--space-2);
}

.tag-group-condensed {
  gap: var(--space-1);
}

/* ===== 表单 ===== */
.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  margin-bottom: var(--space-2);
}

.form-input {
  padding: 10px var(--space-4);
}

.form-error {
  margin-top: var(--space-2);
  font-size: var(--text-sm);
}
```

---

## 附录: 动画参数汇总

### 抽屉动画

| 参数 | 右侧 | 左侧 | 底部 |
|------|------|------|------|
| 尺寸 | 360px | 320px | 48→200px |
| 展开时长 | 300ms | 280ms | 250ms |
| 收起时长 | 250ms | 240ms | 200ms |
| 内容延迟 | 150ms | 140ms | 50ms |
| 缓动函数 | cubic-bezier(0.4, 0, 0.2, 1) | 同左 | 同左 |

### 工具栏动画

| 参数 | 值 |
|------|-----|
| 按钮间距 | 12px |
| 展开延迟 | 0-300ms (每个50ms) |
| 收起延迟 | 0-150ms (每个30ms) |
| 过渡时长 | 200ms |
| 缓动函数 | cubic-bezier(0.4, 0, 0.2, 1) |

### 事件标记脉动

| 参数 | 值 |
|------|-----|
| 周期 | 2000ms |
| 内层延迟 | 0ms |
| 外层延迟 | 500ms |
| 缩放倍数 | 2.5x |
| 悬停加速 | 1s |

---

**文档完成** ✓

**文件位置:** `E:\EventPredictor\docs\UI_COMPLETE_SPEC.md`
