# EventPredictor UI 组件规范

> **版本**: v3.2 | **日期**: 2026-03-14 | **用途**: 前端开发实现

---

## 1. 抽屉动画系统

### 1.1 三抽屉概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   左侧抽屉 (320px)              3D 地球               右侧抽屉 (360px)   │
│   ┌───────────┐              ┌─────────┐            ┌───────────┐      │
│   │           │              │         │            │           │      │
│   │  角色详情  │              │   🌍    │            │  分析结果  │      │
│   │           │              │         │            │           │      │
│   └───────────┘              └─────────┘            └───────────┘      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  ▼ 事件列表 (5)                                          [×]     │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                              底部抽屉 (48px → 200px)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 动画参数表

| 抽屉 | 宽度/高度 | 展开时长 | 收起时长 | 缓动函数 | Z-index |
|------|-----------|----------|----------|----------|---------|
| 右侧 | 360px | 300ms | 250ms | cubic-bezier(0.4, 0, 0.2, 1) | 900 |
| 左侧 | 320px | 280ms | 240ms | 同上 | 700 |
| 底部 | 48→200px | 250ms | 200ms | 同上 | 800 |

### 1.3 右侧抽屉完整实现

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

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);

  /* 动画 */
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 300ms;
}

/* 展开状态 */
.drawer-right.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 0ms;
}

/* 头部 */
.drawer-right .header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.05) 0%, rgba(0, 119, 255, 0.05) 100%);
}

/* 内容区 */
.drawer-right .content {
  padding: 20px;
  height: calc(100vh - 56px - 80px);
  overflow-y: auto;

  /* 内容淡入 */
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 200ms ease 100ms, transform 200ms ease 100ms;
}

.drawer-right.open .content {
  opacity: 1;
  transform: translateY(0);
}

/* 底部 */
.drawer-right .footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  border-top: 1px solid rgba(30, 41, 59, 0.6);
}
```

### 1.4 左侧抽屉完整实现

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
```

### 1.5 底部抽屉完整实现

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
  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);
  overflow: hidden;

  transition: height 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-bottom.open {
  height: 200px;
}

/* 头部 (可点击展开) */
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

/* 内容区 */
.drawer-bottom .content {
  height: 152px;
  padding: 0 24px 24px;
  overflow-x: auto;
  overflow-y: hidden;
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
```

### 1.6 遮罩层

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
```

### 1.7 地球容器响应

```css
/* 地球容器 */
.globe-container {
  width: 100%;
  height: calc(100vh - 48px);
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1), margin-left 300ms ease;
}

/* 右侧抽屉打开 */
.globe-container.drawer-right-open {
  width: calc(100% - 360px);
}

/* 左侧抽屉打开 */
.globe-container.drawer-left-open {
  width: calc(100% - 320px);
  margin-left: 320px;
}

/* 两侧同时打开 */
.globe-container.drawer-right-open.drawer-left-open {
  width: calc(100% - 680px);
  margin-left: 320px;
}
```

### 1.8 React Hook 实现

```tsx
import { useState, useCallback, useEffect } from 'react';

type DrawerPosition = 'left' | 'right' | 'bottom';
type DrawerState = 'closed' | 'opening' | 'open' | 'closing';

// 抽屉配置
const DRAWER_CONFIG = {
  right: { openDuration: 300, closeDuration: 250 },
  left: { openDuration: 280, closeDuration: 240 },
  bottom: { openDuration: 250, closeDuration: 200 },
};

// 抽屉 Hook
function useDrawer(position: DrawerPosition) {
  const [state, setState] = useState<DrawerState>('closed');

  const open = useCallback(() => {
    setState('opening');
    setTimeout(() => setState('open'), DRAWER_CONFIG[position].openDuration);
  }, [position]);

  const close = useCallback(() => {
    setState('closing');
    setTimeout(() => setState('closed'), DRAWER_CONFIG[position].closeDuration);
  }, [position]);

  const toggle = useCallback(() => {
    state === 'open' || state === 'opening' ? close() : open();
  }, [state, open, close]);

  // ESC 关闭
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && state === 'open') close();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [state, close]);

  return { state, open, close, toggle, isOpen: state === 'open' };
}
```

---

## 2. 悬浮工具栏系统

### 2.1 工具栏布局

```
收起状态:                    展开状态:

┌───┐                        ┌───┐
│ ≡ │  主菜单                │ ≡ │  主菜单 (0ms)
└───┘                        ├───┤
                             │ 📊 │  分析面板 (50ms)
左下角固定                    ├───┤
left: 24px                   │ 📋 │  事件列表 (100ms)
bottom: 24px                 ├───┤
                             │ 👥 │  角色详情 (150ms)
                             ├───┤
                             │ 🌙 │  主题切换 (200ms)
                             ├───┤
                             │ ⚙️ │  设置 (250ms)
                             ├───┤
                             │ 🔄 │  刷新 (300ms)
                             └───┘
```

### 2.2 按钮功能定义

| ID | 图标 | 标签 | 快捷键 | 功能 | 激活条件 |
|----|------|------|--------|------|----------|
| menu | ≡ | 菜单 | Esc | 展开/收起工具栏 | - |
| analysis | 📊 | 分析面板 | A | 右侧抽屉 | 右侧抽屉打开 |
| events | 📋 | 事件列表 | E | 底部抽屉 | 底部抽屉打开 |
| roles | 👥 | 角色详情 | R | 左侧抽屉 | 左侧抽屉打开 |
| theme | 🌙/☀️ | 切换主题 | T | 深色/浅色切换 | - |
| settings | ⚙️ | 设置 | S | 打开设置弹窗 | - |
| refresh | 🔄 | 刷新数据 | F5 | 重新获取数据 | 刷新中旋转 |

### 2.3 完整 CSS 实现

```css
/* ========================================
   悬浮工具栏
   ======================================== */

/* 工具栏容器 */
.toolbar {
  position: fixed;
  left: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 600;
}

/* 按钮基础样式 */
.toolbar-btn {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 1px solid var(--border-default);
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 初始隐藏 (非主按钮) */
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

/* 展开状态 */
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

/* 悬停状态 */
.toolbar-btn:hover:not(.disabled) {
  transform: translateY(-4px) scale(1.05);
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);
  box-shadow:
    0 8px 32px rgba(0, 229, 255, 0.2),
    0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* 激活状态 (抽屉打开时) */
.toolbar-btn.active {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
  border-color: transparent;
  box-shadow: 0 0 24px rgba(0, 229, 255, 0.4);
}

/* 激活状态图标 */
.toolbar-btn.active svg {
  color: #FFFFFF;
}

/* 禁用状态 */
.toolbar-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* 按下状态 */
.toolbar-btn:active:not(.disabled) {
  transform: translateY(-2px) scale(0.98);
  transition-duration: 50ms;
}

/* 图标样式 */
.toolbar-btn svg {
  width: 24px;
  height: 24px;
  color: var(--text-secondary);
  transition: color 150ms ease;
}

.toolbar-btn:hover:not(.disabled) svg {
  color: var(--accent-cyan);
}

/* 加载状态 (刷新按钮) */
.toolbar-btn.loading svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Tooltip */
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
  color: var(--text-primary);
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
```

### 2.4 React 组件实现

```tsx
import { useState, useEffect, useCallback } from 'react';
import { Menu, BarChart2, List, Users, Moon, Sun, Settings, RefreshCw } from 'lucide-react';

// 按钮配置
const BUTTONS = [
  { id: 'menu', icon: Menu, label: '菜单', shortcut: 'Esc', primary: true },
  { id: 'analysis', icon: BarChart2, label: '分析面板', shortcut: 'A' },
  { id: 'events', icon: List, label: '事件列表', shortcut: 'E' },
  { id: 'roles', icon: Users, label: '角色详情', shortcut: 'R' },
  { id: 'theme', icon: Moon, label: '切换主题', shortcut: 'T' },
  { id: 'settings', icon: Settings, label: '设置', shortcut: 'S' },
  { id: 'refresh', icon: RefreshCw, label: '刷新数据', shortcut: 'F5' },
];

// 快捷键映射
const SHORTCUT_MAP: Record<string, string> = {
  Escape: 'menu', a: 'analysis', A: 'analysis', e: 'events', E: 'events',
  r: 'roles', R: 'roles', t: 'theme', T: 'theme', s: 'settings', S: 'settings', F5: 'refresh',
};

const Toolbar: React.FC = () => {
  const [expanded, setExpanded] = useState(false);
  const { rightDrawer, leftDrawer, bottomDrawer } = useDrawers();
  const { theme, toggleTheme, isRefreshing, refresh } = useApp();

  // 按钮动作
  const getAction = (id: string) => {
    const actions: Record<string, () => void> = {
      menu: () => setExpanded(!expanded),
      analysis: rightDrawer.toggle,
      events: bottomDrawer.toggle,
      roles: leftDrawer.toggle,
      theme: toggleTheme,
      settings: () => {},
      refresh: refresh,
    };
    return actions[id];
  };

  // 按钮激活状态
  const isActive = (id: string) => {
    const activeStates: Record<string, boolean> = {
      analysis: rightDrawer.isOpen,
      events: bottomDrawer.isOpen,
      roles: leftDrawer.isOpen,
    };
    return activeStates[id] || false;
  };

  // 快捷键处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isInputFocused()) return;
      const buttonId = SHORTCUT_MAP[e.key];
      if (buttonId) {
        e.preventDefault();
        getAction(buttonId)?.();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [expanded]);

  // 点击外部收起
  useEffect(() => {
    if (!expanded) return;
    const handleClick = (e: MouseEvent) => {
      const toolbar = document.querySelector('.toolbar');
      if (toolbar && !toolbar.contains(e.target as Node)) setExpanded(false);
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [expanded]);

  return (
    <div className={`toolbar ${expanded ? 'expanded' : ''}`}>
      {BUTTONS.map((btn, i) => {
        const Icon = btn.id === 'theme' ? (theme === 'dark' ? Moon : Sun) : btn.icon;
        return (
          <button
            key={btn.id}
            className={`toolbar-btn ${btn.primary ? 'primary' : ''} ${isActive(btn.id) ? 'active' : ''} ${btn.id === 'refresh' && isRefreshing ? 'loading' : ''}`}
            onClick={getAction(btn.id)}
            data-tooltip={`${btn.label} (${btn.shortcut})`}
          >
            <Icon />
          </button>
        );
      })}
    </div>
  );
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
│  背景色          主色调          语义色          中性色          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │#0A0E1A  │    │#00E5FF  │    │#EF4444  │    │#F8FAFC  │      │
│  │#0F172A  │    │#0077FF  │    │#F59E0B  │    │#94A3B8  │      │
│  │#1E293B  │    │#8B5CF6  │    │#10B981  │    │#64748B  │      │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
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
  --accent-cyan: #00E5FF;       /* 主强调 */
  --accent-blue: #0077FF;       /* 次强调 */
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

  /* ===== 透明色 (主色变体) ===== */
  --cyan-5: rgba(0, 229, 255, 0.05);
  --cyan-10: rgba(0, 229, 255, 0.1);
  --cyan-20: rgba(0, 229, 255, 0.2);
  --cyan-30: rgba(0, 229, 255, 0.3);
  --cyan-40: rgba(0, 229, 255, 0.4);
}
```

### 3.3 颜色使用场景

```css
/* ===== 背景色使用 ===== */
body { background: var(--bg-primary); }
.card, .drawer { background: var(--bg-secondary); }
.modal, .dropdown { background: var(--bg-tertiary); }
.overlay { background: var(--bg-overlay); }

/* 悬停/选中背景 */
.btn:hover { background: var(--cyan-10); }
.btn.active { background: var(--cyan-20); }

/* ===== 主色调使用 ===== */
.btn-primary { background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)); }
.text-highlight { color: var(--accent-cyan); }
a { color: var(--accent-blue); }
.border-highlight { border-color: var(--accent-cyan); }
.glow { box-shadow: 0 0 20px var(--cyan-40); }

/* ===== 语义色使用 ===== */
.error, .severity-5 { color: var(--status-danger); }
.warning, .severity-3-4 { color: var(--status-warning); }
.success, .severity-1-2 { color: var(--status-success); }
.info { color: var(--status-info); }

/* 标签样式 */
.tag-danger { background: rgba(239, 68, 68, 0.2); color: var(--status-danger); border: 1px solid rgba(239, 68, 68, 0.3); }
.tag-warning { background: rgba(245, 158, 11, 0.2); color: var(--status-warning); border: 1px solid rgba(245, 158, 11, 0.3); }
.tag-success { background: rgba(16, 185, 129, 0.2); color: var(--status-success); border: 1px solid rgba(16, 185, 129, 0.3); }

/* ===== 文字色使用 ===== */
h1, h2, h3, p { color: var(--text-primary); }
.description, .label { color: var(--text-secondary); }
.timestamp, .meta { color: var(--text-muted); }
.disabled { color: var(--text-disabled); }

/* ===== 边框色使用 ===== */
.card { border: 1px solid var(--border-default); }
.card:hover { border-color: var(--border-light); }
.card.selected { border-color: var(--border-accent); }
```

### 3.4 渐变色规范

```css
/* ===== 主渐变 ===== */
.gradient-primary { background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%); }
.gradient-hover { background: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%); }

/* ===== 趋势渐变 ===== */
.gradient-up { background: linear-gradient(90deg, #10B981 0%, #22C55E 100%); }
.gradient-down { background: linear-gradient(90deg, #EF4444 0%, #F97316 100%); }
.gradient-neutral { background: linear-gradient(90deg, #F59E0B 0%, #EAB308 100%); }

/* ===== 文字渐变 ===== */
.gradient-text {
  background: linear-gradient(90deg, #00E5FF 0%, #0077FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ===== 边框渐变 ===== */
.gradient-border {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--bg-secondary), var(--bg-secondary)) padding-box,
    linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 119, 255, 0.3)) border-box;
}
```

### 3.5 发光效果

```css
/* ===== 预设发光 ===== */
.glow-cyan { box-shadow: 0 0 20px rgba(0, 229, 255, 0.25); }
.glow-cyan-strong { box-shadow: 0 0 20px rgba(0, 229, 255, 0.25), 0 0 40px rgba(0, 229, 255, 0.15); }
.glow-danger { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
.glow-success { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }

/* ===== 呼吸动画 ===== */
@keyframes breathe {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 229, 255, 0.2); }
  50% { box-shadow: 0 0 40px rgba(0, 229, 255, 0.4); }
}
.breathe { animation: breathe 3s ease-in-out infinite; }

/* ===== 文字发光 ===== */
.text-glow-cyan { text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
```

### 3.6 颜色对比度验证

| 组合 | 对比度 | WCAG AA | WCAG AAA |
|------|--------|---------|----------|
| text-primary / bg-primary | 15.2:1 | ✓ | ✓ |
| text-secondary / bg-primary | 5.1:1 | ✓ | ✗ |
| text-muted / bg-primary | 3.5:1 | ✓ | ✗ |
| accent-cyan / bg-primary | 8.7:1 | ✓ | ✓ |
| status-danger / bg-primary | 4.8:1 | ✓ | ✗ |

---

## 4. 事件标记脉动 (补充)

### 4.1 标记结构

```html
<div class="event-marker" data-severity="5">
  <div class="core"></div>
  <div class="pulse-inner"></div>
  <div class="pulse-outer"></div>
  <div class="tooltip">...</div>
</div>
```

### 4.2 完整 CSS

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
  transition: transform 200ms ease, box-shadow 200ms ease;
}

/* 脉动层 */
.event-marker .pulse-inner,
.event-marker .pulse-outer {
  position: absolute;
  top: 50%;
  left: 50%;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.event-marker .pulse-inner {
  width: 24px;
  height: 24px;
  z-index: 2;
  animation: pulseInner 2s ease-out infinite;
}

.event-marker .pulse-outer {
  width: 40px;
  height: 40px;
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

/* Severity 5 - 紧急 */
.event-marker[data-severity="5"] .core {
  background: #EF4444;
  box-shadow: 0 0 8px #EF4444, 0 0 16px rgba(239, 68, 68, 0.6), 0 0 32px rgba(239, 68, 68, 0.3);
}
.event-marker[data-severity="5"] .pulse-inner { border: 2px solid #EF4444; background: radial-gradient(circle, rgba(239, 68, 68, 0.4) 0%, transparent 70%); }
.event-marker[data-severity="5"] .pulse-outer { border: 2px solid rgba(239, 68, 68, 0.6); background: radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 60%); }

/* Severity 4 - 高危 */
.event-marker[data-severity="4"] .core { background: #F97316; box-shadow: 0 0 6px #F97316, 0 0 12px rgba(249, 115, 22, 0.6); }
.event-marker[data-severity="4"] .pulse-inner { border: 2px solid #F97316; background: radial-gradient(circle, rgba(249, 115, 22, 0.4) 0%, transparent 70%); }
.event-marker[data-severity="4"] .pulse-outer { border: 2px solid rgba(249, 115, 22, 0.6); background: radial-gradient(circle, rgba(249, 115, 22, 0.2) 0%, transparent 60%); }

/* Severity 3 - 重要 */
.event-marker[data-severity="3"] .core { background: #F59E0B; box-shadow: 0 0 5px #F59E0B, 0 0 10px rgba(245, 158, 11, 0.6); }
.event-marker[data-severity="3"] .pulse-inner { border: 2px solid #F59E0B; background: radial-gradient(circle, rgba(245, 158, 11, 0.4) 0%, transparent 70%); }
.event-marker[data-severity="3"] .pulse-outer { border: 2px solid rgba(245, 158, 11, 0.6); background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, transparent 60%); }

/* Severity 2 - 一般 */
.event-marker[data-severity="2"] .core { background: #22C55E; box-shadow: 0 0 4px #22C55E, 0 0 8px rgba(34, 197, 94, 0.6); }
.event-marker[data-severity="2"] .pulse-inner { border: 2px solid #22C55E; background: radial-gradient(circle, rgba(34, 197, 94, 0.4) 0%, transparent 70%); }
.event-marker[data-severity="2"] .pulse-outer { border: 2px solid rgba(34, 197, 94, 0.6); background: radial-gradient(circle, rgba(34, 197, 94, 0.2) 0%, transparent 60%); }

/* Severity 1 - 低 */
.event-marker[data-severity="1"] .core { background: #3B82F6; box-shadow: 0 0 3px #3B82F6, 0 0 6px rgba(59, 130, 246, 0.6); }
.event-marker[data-severity="1"] .pulse-inner { border: 2px solid #3B82F6; background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%); }
.event-marker[data-severity="1"] .pulse-outer { border: 2px solid rgba(59, 130, 246, 0.6); background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, transparent 60%); }

/* 悬停加速 */
.event-marker:hover .core { transform: translate(-50%, -50%) scale(1.5); }
.event-marker:hover .pulse-inner, .event-marker:hover .pulse-outer { animation-duration: 1s; }

/* 选中状态 */
.event-marker.selected .core { transform: translate(-50%, -50%) scale(1.8); }
.event-marker.selected .pulse-inner, .event-marker.selected .pulse-outer { animation-duration: 1.5s; border-width: 3px; }
```

---

## 5. 实现优先级

| 优先级 | 组件 | 文件 | 状态 |
|--------|------|------|------|
| P0 | 抽屉系统 | `Drawer.tsx` | 待实现 |
| P0 | 工具栏 | `Toolbar.tsx` | 待实现 |
| P1 | 事件标记 | `EventMarker.tsx` | 待实现 |
| P2 | 颜色 Tokens | `tokens.css` | 待实现 |

---

**文档完成** ✓

**相关文档:**
- `UI_DESIGN_SPEC.md` - 完整设计规范
- `UI_IMPLEMENTATION_GUIDE.md` - 详细实现指南
