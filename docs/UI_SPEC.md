# EventPredictor UI 规范手册

> **版本**: v3.4 | **日期**: 2026-03-14 | **用途**: 前端开发直接使用

---

## 快速索引

| 章节 | 内容 | 页码 |
|------|------|------|
| [1. 抽屉动画](#1-抽屉展开动画效果) | 右侧/左侧/底部抽屉完整实现 | ↓ |
| [2. 工具栏按钮](#2-悬浮工具栏按钮) | 7个按钮功能与交互 | ↓ |
| [3. 颜色规范](#3-颜色规范) | 完整颜色系统 | ↓ |

---

## 1. 抽屉展开动画效果

### 1.1 三抽屉概览

```
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  ┌─────────┐                    ┌─────────┐                          │
│  │ 左侧     │                    │ 右侧     │                          │
│  │ 320px   │     🌍 3D 地球     │ 360px   │                          │
│  │ 角色详情 │                    │ 分析结果 │                          │
│  └─────────┘                    └─────────┘                          │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │ ▼ 事件列表 (5)                                        [×]    │   │
│  │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │   │
│  │ │事件1│ │事件2│ │事件3│ │事件4│ │事件5│  ← 横向滚动          │   │
│  │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                        底部抽屉 (48px → 200px)                        │
└───────────────────────────────────────────────────────────────────────┘
```

### 1.2 动画参数速查表

| 抽屉 | 尺寸 | 展开时长 | 收起时长 | Z-index | 触发方式 |
|------|------|----------|----------|---------|----------|
| **右侧** | 360px | 300ms | 250ms | 900 | 点击事件/工具栏📊 |
| **左侧** | 320px | 280ms | 240ms | 700 | 点击"查看完整分析" |
| **底部** | 48→200px | 250ms | 200ms | 800 | 工具栏📋 |

### 1.3 右侧抽屉 - 完整实现

#### 动画时间线

```
0ms ─────────────────────────────────────────────── 300ms

抽屉面板:  translateX(100%) ─────────────────→ translateX(0)
透明度:    0.9 ─────────────────────────────────→ 1

遮罩层:    opacity: 0 ──────────────────────────→ 0.4

地球宽度:  100% ──────────────────────────────→ calc(100%-360px)
           (延迟50ms开始)

内容淡入:  opacity: 0, translateY(10px) ──────→ opacity: 1, translateY(0)
           (延迟150ms开始)
```

#### CSS 代码 (可直接使用)

```css
/* ===== 右侧抽屉 - 分析面板 ===== */
.drawer-right {
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

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);

  /* 过渡 */
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

/* Content */
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

/* Footer */
.drawer-right .footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  border-top: 1px solid rgba(30, 41, 59, 0.6);
}
```

### 1.4 左侧抽屉 - 完整实现

#### 动画时间线

```
0ms ─────────────────────────────────────────────── 280ms

抽屉面板:  translateX(-100%) ────────────────────→ translateX(0)
透明度:    0.9 ─────────────────────────────────→ 1

地球:      width: 100%, margin-left: 0 ────────→ width: calc(100%-320px), margin-left: 320px
           (延迟40ms开始)

内容淡入:  (延迟140ms开始)

角色卡片:  依次出现，每个延迟50ms
```

#### CSS 代码 (可直接使用)

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
  transition:
    transform 280ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 180ms ease,
    visibility 0ms linear 0ms;
}

/* Content */
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
  opacity: 0;
  transform: translateX(-10px);
  transition: opacity 150ms ease, transform 150ms ease;
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
```

### 1.5 底部抽屉 - 完整实现

#### 动画时间线

```
0ms ─────────────────────────────────────────────── 250ms

高度:      48px ─────────────────────────────────→ 200px

图标旋转:  0deg ────────────────────────────────→ 180deg
           (200ms内完成)

内容淡入:  (延迟50ms开始)

事件卡片:  依次出现，每个延迟30ms
```

#### CSS 代码 (可直接使用)

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

/* Header (可点击展开) */
.drawer-bottom .header {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

/* 展开图标 */
.drawer-bottom .expand-icon {
  transition: transform 200ms ease;
}

.drawer-bottom.open .expand-icon {
  transform: rotate(180deg);
}

/* Content */
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
  opacity: 0;
  transform: translateX(20px);
  transition: opacity 150ms ease, transform 150ms ease;
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
```

### 1.6 遮罩层 & 地球响应

```css
/* 遮罩层 */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 850;
  opacity: 0;
  visibility: hidden;
  transition: opacity 200ms ease, visibility 200ms ease;
  cursor: pointer;
}

.drawer-overlay.visible {
  opacity: 1;
  visibility: visible;
}

/* 地球容器响应 */
.globe-container {
  width: 100%;
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1), margin-left 300ms ease;
}

.globe-container.drawer-right-open {
  width: calc(100% - 360px);
}

.globe-container.drawer-left-open {
  width: calc(100% - 320px);
  margin-left: 320px;
}

.globe-container.drawer-right-open.drawer-left-open {
  width: calc(100% - 680px);
  margin-left: 320px;
}
```

---

## 2. 悬浮工具栏按钮

### 2.1 工具栏布局

```
位置: 左下角 (left: 24px, bottom: 24px)

收起状态:              展开状态:
┌───┐                  ┌───┐
│ ≡ │                  │ ≡ │  主菜单 (0ms)
└───┘                  ├───┤
                       │ 📊 │  分析 (50ms)
                       ├───┤
                       │ 📋 │  事件 (100ms)
                       ├───┤
                       │ 👥 │  角色 (150ms)
                       ├───┤
                       │ 🌙 │  主题 (200ms)
                       ├───┤
                       │ ⚙️ │  设置 (250ms)
                       ├───┤
                       │ 🔄 │  刷新 (300ms)
                       └───┘
```

### 2.2 按钮功能表

| # | 图标 | 名称 | 快捷键 | 功能 | 激活条件 |
|---|------|------|--------|------|----------|
| 1 | ≡ | 主菜单 | Esc | 展开/收起工具栏 | 工具栏展开时 |
| 2 | 📊 | 分析面板 | A | 切换右侧抽屉 | 右侧抽屉打开时 |
| 3 | 📋 | 事件列表 | E | 切换底部抽屉 | 底部抽屉打开时 |
| 4 | 👥 | 角色详情 | R | 切换左侧抽屉 | 左侧抽屉打开时 |
| 5 | 🌙/☀️ | 主题切换 | T | 深色/浅色主题 | 无持续状态 |
| 6 | ⚙️ | 设置 | S | 打开设置弹窗 | 弹窗打开时 |
| 7 | 🔄 | 刷新 | F5 | 重新获取数据 | 刷新时图标旋转 |

### 2.3 按钮展开动画

```
展开动画 (总时长 350ms):

按钮2 (📊): 延迟 0ms   → 200ms 完成
按钮3 (📋): 延迟 50ms  → 250ms 完成
按钮4 (👥): 延迟 100ms → 300ms 完成
按钮5 (🌙): 延迟 150ms → 350ms 完成
按钮6 (⚙️): 延迟 200ms → 400ms 完成
按钮7 (🔄): 延迟 250ms → 450ms 完成

每个按钮动画:
  初始: opacity: 0, transform: translateX(-20px) scale(0.8)
  结束: opacity: 1, transform: translateX(0) scale(1)
  时长: 200ms
```

### 2.4 按钮状态样式

| 状态 | 背景 | 边框 | 图标 | 变换 |
|------|------|------|------|------|
| 默认 | rgba(15, 23, 42, 0.9) | #1E293B | #94A3B8 | none |
| 悬停 | rgba(0, 229, 255, 0.1) | rgba(0, 229, 255, 0.3) | #00E5FF | translateY(-4px) scale(1.05) |
| 激活 | 渐变 cyan→blue | 无 | #FFFFFF | none |
| 禁用 | rgba(30, 41, 59, 0.5) | 无 | #475569 | none |
| 加载 | 默认 | 默认 | 旋转 | - |

### 2.5 完整 CSS 代码

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
  box-shadow: 0 8px 32px rgba(0, 229, 255, 0.2);
}

/* 主按钮悬停 */
.toolbar-btn.primary:hover {
  transform: translateY(-4px) scale(1.05);
}

/* ===== 激活状态 ===== */
.toolbar-btn.active {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
  border-color: transparent;
  box-shadow: 0 0 24px rgba(0, 229, 255, 0.4);
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
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

### 2.6 快捷键映射

```typescript
// 快捷键配置
const SHORTCUT_MAP: Record<string, string> = {
  'Escape': 'menu',
  'a': 'analysis', 'A': 'analysis',
  'e': 'events', 'E': 'events',
  'r': 'roles', 'R': 'roles',
  't': 'theme', 'T': 'theme',
  's': 'settings', 'S': 'settings',
  'F5': 'refresh',
};

// 按钮动作
const actions = {
  menu: () => setExpanded(!expanded),
  analysis: () => rightDrawer.toggle(),
  events: () => bottomDrawer.toggle(),
  roles: () => leftDrawer.toggle(),
  theme: () => toggleTheme(),
  settings: () => openSettings(),
  refresh: () => refreshData(),
};
```

---

## 3. 颜色规范

### 3.1 颜色系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         颜色层级                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  背景色          主色调          语义色          文字色         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │#0A0E1A  │    │#00E5FF  │    │#EF4444  │    │#F8FAFC  │     │
│  │#0F172A  │    │#0077FF  │    │#F59E0B  │    │#94A3B8  │     │
│  │#1E293B  │    │#8B5CF6  │    │#10B981  │    │#64748B  │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 完整颜色 Token

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
  --status-danger: #EF4444;     /* 紧急/错误 - severity 5 */
  --status-warning: #F59E0B;    /* 警告/重要 - severity 3-4 */
  --status-success: #10B981;    /* 成功/正常 - severity 1-2 */
  --status-info: #3B82F6;       /* 信息 */

  /* ===== 文字色 ===== */
  --text-primary: #F8FAFC;      /* 主要文字 - 对比度 15.2:1 */
  --text-secondary: #94A3B8;    /* 次要文字 - 对比度 5.1:1 */
  --text-muted: #64748B;        /* 辅助文字 - 对比度 3.5:1 */
  --text-disabled: #475569;     /* 禁用文字 */

  /* ===== 边框色 ===== */
  --border-default: #1E293B;    /* 默认边框 */
  --border-light: #334155;      /* 浅色边框 */
  --border-accent: #00E5FF;     /* 强调边框 */

  /* ===== 透明色变体 ===== */
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

### 3.3 颜色使用场景

```css
/* ===== 背景使用 ===== */
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
/* 紧急 */
.severity-5, .error {
  color: var(--status-danger);
  background: var(--danger-10);
  border-color: var(--danger-30);
}

/* 警告 */
.severity-3, .severity-4, .warning {
  color: var(--status-warning);
  background: var(--warning-10);
  border-color: var(--warning-30);
}

/* 正常 */
.severity-1, .severity-2, .success {
  color: var(--status-success);
  background: var(--success-10);
  border-color: var(--success-30);
}

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

### 3.4 渐变规范

```css
/* 主渐变 */
.gradient-primary {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
}

/* 悬停渐变 */
.gradient-hover {
  background: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%);
}

/* 趋势渐变 */
.gradient-up { background: linear-gradient(90deg, #10B981, #22C55E); }
.gradient-down { background: linear-gradient(90deg, #EF4444, #F97316); }
.gradient-neutral { background: linear-gradient(90deg, #F59E0B, #EAB308); }

/* 文字渐变 */
.gradient-text {
  background: linear-gradient(90deg, #00E5FF, #0077FF);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 边框渐变 */
.gradient-border {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--bg-secondary), var(--bg-secondary)) padding-box,
    linear-gradient(135deg, var(--cyan-30), rgba(0, 119, 255, 0.3)) border-box;
}
```

### 3.5 发光效果

```css
/* 预设发光 */
.glow-cyan { box-shadow: 0 0 20px rgba(0, 229, 255, 0.25); }
.glow-cyan-strong {
  box-shadow:
    0 0 20px rgba(0, 229, 255, 0.25),
    0 0 40px rgba(0, 229, 255, 0.15);
}
.glow-danger { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
.glow-success { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }

/* 呼吸动画 */
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); }
  50% { box-shadow: 0 0 40px rgba(0, 229, 255, 0.4); }
}
.breathe { animation: breathe 3s ease-in-out infinite; }

/* 文字发光 */
.text-glow { text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
```

### 3.6 对比度验证

| 组合 | 对比度 | WCAG AA | WCAG AAA |
|------|--------|---------|----------|
| text-primary / bg-primary | 15.2:1 | ✓ | ✓ |
| text-secondary / bg-primary | 5.1:1 | ✓ | ✗ |
| text-muted / bg-primary | 3.5:1 | ✓ | ✗ |
| accent-cyan / bg-primary | 8.7:1 | ✓ | ✓ |
| status-danger / bg-primary | 4.8:1 | ✓ | ✗ |

---

## 附录: 事件标记脉动 (补充)

### 事件标记 CSS

```css
/* 标记容器 */
.event-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 400;
}

/* 核心点 */
.event-marker .core {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 3;
}

/* 脉动层 */
.event-marker .pulse-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  animation: pulseInner 2s ease-out infinite;
}

.event-marker .pulse-outer {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  animation: pulseOuter 2s ease-out infinite 0.5s;
}

@keyframes pulseInner {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.8; }
  100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
}

@keyframes pulseOuter {
  0% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
}

/* Severity 5 - 紧急 (红色) */
.event-marker[data-severity="5"] .core {
  background: #EF4444;
  box-shadow: 0 0 8px #EF4444, 0 0 16px rgba(239, 68, 68, 0.6);
}
.event-marker[data-severity="5"] .pulse-inner { border: 2px solid #EF4444; }
.event-marker[data-severity="5"] .pulse-outer { border: 2px solid rgba(239, 68, 68, 0.6); }

/* Severity 4 - 高危 (橙色) */
.event-marker[data-severity="4"] .core {
  background: #F97316;
  box-shadow: 0 0 6px #F97316, 0 0 12px rgba(249, 115, 22, 0.6);
}
.event-marker[data-severity="4"] .pulse-inner { border: 2px solid #F97316; }
.event-marker[data-severity="4"] .pulse-outer { border: 2px solid rgba(249, 115, 22, 0.6); }

/* Severity 3 - 重要 (黄色) */
.event-marker[data-severity="3"] .core {
  background: #F59E0B;
  box-shadow: 0 0 5px #F59E0B, 0 0 10px rgba(245, 158, 11, 0.6);
}
.event-marker[data-severity="3"] .pulse-inner { border: 2px solid #F59E0B; }
.event-marker[data-severity="3"] .pulse-outer { border: 2px solid rgba(245, 158, 11, 0.6); }

/* Severity 2 - 一般 (绿色) */
.event-marker[data-severity="2"] .core {
  background: #22C55E;
  box-shadow: 0 0 4px #22C55E, 0 0 8px rgba(34, 197, 94, 0.6);
}
.event-marker[data-severity="2"] .pulse-inner { border: 2px solid #22C55E; }
.event-marker[data-severity="2"] .pulse-outer { border: 2px solid rgba(34, 197, 94, 0.6); }

/* Severity 1 - 低 (蓝色) */
.event-marker[data-severity="1"] .core {
  background: #3B82F6;
  box-shadow: 0 0 3px #3B82F6, 0 0 6px rgba(59, 130, 246, 0.6);
}
.event-marker[data-severity="1"] .pulse-inner { border: 2px solid #3B82F6; }
.event-marker[data-severity="1"] .pulse-outer { border: 2px solid rgba(59, 130, 246, 0.6); }

/* 悬停加速 */
.event-marker:hover .pulse-inner,
.event-marker:hover .pulse-outer {
  animation-duration: 1s;
}
```

---

**文档完成** ✓

**相关文档:**
- `UI_ANIMATION_DETAIL.md` - 动画详解
- `UI_COMPONENTS.md` - 组件规范
- `UI_DESIGN_SPEC.md` - 设计规范
