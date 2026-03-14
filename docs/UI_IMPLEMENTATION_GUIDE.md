# EventPredictor UI 实现指南

> **版本**: v3.1
> **日期**: 2026-03-14
> **用途**: 前端开发实现参考

---

## 目录

1. [抽屉展开动画效果](#1-抽屉展开动画效果)
2. [悬浮工具栏按钮功能](#2-悬浮工具栏按钮功能)
3. [事件标记脉动动画](#3-事件标记脉动动画)
4. [颜色规范](#4-颜色规范)
5. [字体间距](#5-字体间距)

---

## 1. 抽屉展开动画效果

### 1.1 动画原理图解

```
右侧抽屉展开过程:

时刻 0ms (关闭):
┌────────────────────────────────────────────────────────┐
│                                                        │
│                    3D 地球                              │
│                    100% 宽度                            │
│                                                        │
│                                    │← 抽屉在屏幕外      │
└────────────────────────────────────────────────────────┘

时刻 150ms (展开中):
┌────────────────────────────────────────────────────────┐
│                                              ╔═════════╗
│                    3D 地球                    ║         ║
│                    75% 宽度                   ║ 抽屉    ║
│                                              ║ 滑入中  ║
│                                              ║         ║
└────────────────────────────────────────────────────────╚

时刻 300ms (展开完成):
┌────────────────────────────────────────────────────────┐
│                                    ╔═══════════════════╗
│        3D 地球                      ║                   ║
│        calc(100% - 360px)           ║     抽屉面板      ║
│                                     ║     360px        ║
│                                    ║                   ║
└────────────────────────────────────╨───────────────────┨
```

### 1.2 动画参数详解

#### 右侧抽屉

```css
/* 动画参数 */
--drawer-right-duration: 300ms;
--drawer-right-easing: cubic-bezier(0.4, 0, 0.2, 1);
--drawer-right-width: 360px;
```

| 阶段 | 时间 | translateX | opacity | 地球宽度 |
|------|------|------------|---------|----------|
| 初始 | 0ms | 100% | 0.9 | 100% |
| 25% | 75ms | 75% | 1 | calc(100% - 90px) |
| 50% | 150ms | 50% | 1 | calc(100% - 180px) |
| 75% | 225ms | 25% | 1 | calc(100% - 270px) |
| 100% | 300ms | 0 | 1 | calc(100% - 360px) |

#### 底部抽屉

```css
/* 动画参数 */
--drawer-bottom-duration: 250ms;
--drawer-bottom-easing: cubic-bezier(0.4, 0, 0.2, 1);
--drawer-bottom-height-collapsed: 48px;
--drawer-bottom-height-expanded: 200px;
```

| 阶段 | 时间 | height | opacity (内容) |
|------|------|--------|----------------|
| 初始 | 0ms | 48px | 0 |
| 50% | 125ms | 124px | 0.5 |
| 100% | 250ms | 200px | 1 |

#### 左侧抽屉

```css
/* 动画参数 */
--drawer-left-duration: 280ms;
--drawer-left-easing: cubic-bezier(0.4, 0, 0.2, 1);
--drawer-left-width: 320px;
```

| 阶段 | 时间 | translateX | 地球宽度 |
|------|------|------------|----------|
| 初始 | 0ms | -100% | 100% |
| 50% | 140ms | -50% | calc(100% - 160px) |
| 100% | 280ms | 0 | calc(100% - 320px) |

### 1.3 完整 CSS 代码

```css
/* ============================================
   抽屉系统 - 完整实现
   ============================================ */

/* ===== 基础样式 ===== */
.drawer {
  position: fixed;
  z-index: var(--z-drawer);

  /* 毛玻璃效果 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);

  /* 性能优化 */
  will-change: transform, opacity;
  contain: layout style;
}

/* ===== 右侧抽屉 ===== */
.drawer-right {
  --drawer-width: 360px;
  --drawer-duration: 300ms;

  top: 0;
  right: 0;
  width: var(--drawer-width);
  height: 100vh;

  /* 边框和阴影 */
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);

  /* 初始状态 */
  transform: translateX(100%);
  opacity: 0.9;
  visibility: hidden;

  /* 过渡 */
  transition:
    transform var(--drawer-duration) cubic-bezier(0.4, 0, 0.2, 1),
    opacity calc(var(--drawer-duration) * 0.67) ease,
    visibility 0ms linear var(--drawer-duration);
}

.drawer-right.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;

  transition:
    transform var(--drawer-duration) cubic-bezier(0.4, 0, 0.2, 1),
    opacity calc(var(--drawer-duration) * 0.67) ease,
    visibility 0ms linear 0ms;
}

/* 右侧抽屉 - 头部 */
.drawer-right .drawer-header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  background: linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.05) 0%,
    rgba(0, 119, 255, 0.05) 100%
  );
}

/* 右侧抽屉 - 内容 */
.drawer-right .drawer-content {
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 56px - 80px);

  /* 内容淡入 */
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 200ms ease 100ms,
    transform 200ms ease 100ms;
}

.drawer-right.open .drawer-content {
  opacity: 1;
  transform: translateY(0);
}

/* 右侧抽屉 - 底部 */
.drawer-right .drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;

  border-top: 1px solid rgba(30, 41, 59, 0.6);
}

/* ===== 左侧抽屉 ===== */
.drawer-left {
  --drawer-width: 320px;
  --drawer-duration: 280ms;

  top: 0;
  left: 0;
  width: var(--drawer-width);
  height: 100vh;

  border-right: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);

  transform: translateX(-100%);
  opacity: 0.9;
  visibility: hidden;

  transition:
    transform var(--drawer-duration) cubic-bezier(0.4, 0, 0.2, 1),
    opacity calc(var(--drawer-duration) * 0.67) ease,
    visibility 0ms linear var(--drawer-duration);
}

.drawer-left.open {
  transform: translateX(0);
  opacity: 1;
  visibility: visible;

  transition:
    transform var(--drawer-duration) cubic-bezier(0.4, 0, 0.2, 1),
    opacity calc(var(--drawer-duration) * 0.67) ease,
    visibility 0ms linear 0ms;
}

/* ===== 底部抽屉 ===== */
.drawer-bottom {
  --drawer-height-collapsed: 48px;
  --drawer-height-expanded: 200px;
  --drawer-duration: 250ms;

  bottom: 0;
  left: 0;
  right: 0;
  height: var(--drawer-height-collapsed);

  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);

  overflow: hidden;

  transition:
    height var(--drawer-duration) cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-bottom.open {
  height: var(--drawer-height-expanded);
}

/* 底部抽屉 - 头部 */
.drawer-bottom .drawer-header {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

/* 底部抽屉 - 展开图标旋转 */
.drawer-bottom .expand-icon {
  transition: transform 200ms ease;
}

.drawer-bottom.open .expand-icon {
  transform: rotate(180deg);
}

/* 底部抽屉 - 内容 */
.drawer-bottom .drawer-content {
  padding: 0 24px 24px;
  height: calc(var(--drawer-height-expanded) - 48px);
  overflow-x: auto;
  overflow-y: hidden;

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

/* ===== 遮罩层 ===== */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);

  opacity: 0;
  visibility: hidden;
  z-index: calc(var(--z-drawer-right) - 1);

  transition:
    opacity 200ms ease,
    visibility 200ms ease;

  cursor: pointer;
}

.drawer-overlay.visible {
  opacity: 1;
  visibility: visible;
}

/* ===== 地球容器响应 ===== */
.globe-container {
  width: 100%;
  height: calc(100vh - 48px);
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* 右侧抽屉打开时 */
.globe-container.drawer-right-open {
  width: calc(100% - 360px);
}

/* 左侧抽屉打开时 */
.globe-container.drawer-left-open {
  width: calc(100% - 320px);
  margin-left: 320px;
}

/* 两侧同时打开 */
.globe-container.drawer-right-open.drawer-left-open {
  width: calc(100% - 360px - 320px);
  margin-left: 320px;
}
```

### 1.4 React 组件实现

```tsx
import { useState, useEffect, useCallback } from 'react';

// 抽屉状态类型
type DrawerState = 'closed' | 'opening' | 'open' | 'closing';

// 抽屉 Hook
function useDrawer(
  position: 'left' | 'right' | 'bottom',
  onOpen?: () => void,
  onClose?: () => void
) {
  const [state, setState] = useState<DrawerState>('closed');

  const open = useCallback(() => {
    setState('opening');
    setTimeout(() => {
      setState('open');
      onOpen?.();
    }, position === 'right' ? 300 : position === 'left' ? 280 : 250);
  }, [position, onOpen]);

  const close = useCallback(() => {
    setState('closing');
    setTimeout(() => {
      setState('closed');
      onClose?.();
    }, position === 'right' ? 250 : position === 'left' ? 240 : 200);
  }, [position, onClose]);

  const toggle = useCallback(() => {
    if (state === 'open' || state === 'opening') {
      close();
    } else {
      open();
    }
  }, [state, open, close]);

  return { state, open, close, toggle, isOpen: state === 'open' };
}

// 抽屉组件
interface DrawerProps {
  position: 'left' | 'right' | 'bottom';
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

const Drawer: React.FC<DrawerProps> = ({
  position,
  isOpen,
  onClose,
  title,
  children,
  footer
}) => {
  // ESC 键关闭
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // 禁止背景滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <>
      {/* 遮罩层 */}
      {position !== 'bottom' && (
        <div
          className={`drawer-overlay ${isOpen ? 'visible' : ''}`}
          onClick={onClose}
        />
      )}

      {/* 抽屉 */}
      <div className={`drawer drawer-${position} ${isOpen ? 'open' : ''}`}>
        <div className="drawer-header">
          <h3 className="drawer-title">{title}</h3>
          <button className="drawer-close" onClick={onClose}>
            <XIcon />
          </button>
        </div>

        <div className="drawer-content">
          {children}
        </div>

        {footer && (
          <div className="drawer-footer">
            {footer}
          </div>
        )}
      </div>
    </>
  );
};
```

---

## 2. 悬浮工具栏按钮功能

### 2.1 工具栏交互流程

```
用户交互流程:

1. 页面加载
   └→ 工具栏收起，仅显示主菜单按钮 (≡)

2. 点击主菜单
   └→ 工具栏展开，按钮依次动画出现 (0-300ms延迟)

3. 点击功能按钮
   ├→ 分析面板 (📊) → 右侧抽屉展开/收起
   ├→ 事件列表 (📋) → 底部抽屉展开/收起
   ├→ 角色详情 (👥) → 左侧抽屉展开/收起
   ├→ 主题切换 (🌙) → 深色/浅色主题切换
   ├→ 设置 (⚙️) → 设置弹窗打开
   └→ 刷新 (🔄) → 数据刷新，按钮旋转

4. 点击外部区域 / ESC键
   └→ 工具栏收起
```

### 2.2 按钮展开动画时间线

```
按钮展开动画 (总时长 350ms):

按钮1 (主菜单):
├─ 始终可见
├─ 不参与展开动画
└─ 作为展开/收起开关

按钮2 (分析): 延迟 0ms
├─ 0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
├─ 100ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
└─ 200ms: opacity: 1, transform: translateX(0) scale(1)

按钮3 (事件): 延迟 50ms
├─ 0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
├─ 150ms: opacity: 0.5, transform: translateX(-8px) scale(0.95)
└─ 250ms: opacity: 1, transform: translateX(0) scale(1)

按钮4 (角色): 延迟 100ms
...以此类推

按钮5 (主题): 延迟 150ms
按钮6 (设置): 延迟 200ms
按钮7 (刷新): 延迟 250ms
```

### 2.3 按钮状态矩阵

| 状态 | 背景色 | 边框 | 图标色 | 变换 | 阴影 |
|------|--------|------|--------|------|------|
| 默认 | rgba(15, 23, 42, 0.9) | #1E293B | #94A3B8 | none | none |
| 悬停 | rgba(0, 229, 255, 0.1) | rgba(0, 229, 255, 0.3) | #00E5FF | translateY(-4px) scale(1.05) | 发光 |
| 激活 | 渐变 cyan→blue | none | #FFFFFF | none | 强发光 |
| 禁用 | rgba(30, 41, 59, 0.5) | none | #475569 | none | none |
| 加载 | rgba(15, 23, 42, 0.9) | #1E293B | #94A3B8 | 图标旋转 | none |

### 2.4 完整 CSS 代码

```css
/* ============================================
   悬浮工具栏 - 完整实现
   ============================================ */

/* ===== 工具栏容器 ===== */
.toolbar {
  position: fixed;
  left: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: var(--z-toolbar);
}

/* ===== 按钮基础样式 ===== */
.toolbar-btn {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 1px solid var(--border-default);
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 初始状态 (非主按钮隐藏) */
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

/* ===== 收起动画 ===== */
.toolbar:not(.expanded) .toolbar-btn:not(.primary) {
  transition-delay: 0ms;
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
  color: var(--text-secondary);
  transition: color 150ms ease;
}

.toolbar-btn:hover:not(.disabled) svg {
  color: var(--accent-cyan);
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

/* ===== 快捷键提示 ===== */
.toolbar-btn[data-tooltip]::before {
  content: attr(data-shortcut);
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);
  transform: translate(calc(100% + 80px), -50%);

  padding: 4px 6px;
  border-radius: 4px;

  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(51, 65, 85, 0.5);

  font-size: 10px;
  font-weight: 500;
  font-family: var(--font-mono);
  color: var(--text-muted);

  opacity: 0;
  visibility: hidden;
  transition: opacity 150ms ease, visibility 150ms ease;
}

.toolbar-btn:hover[data-shortcut]::before {
  opacity: 1;
  visibility: visible;
}
```

### 2.5 React 组件实现

```tsx
import { useState, useCallback, useEffect } from 'react';
import {
  Menu, BarChart2, List, Users, Moon, Sun, Settings, RefreshCw
} from 'lucide-react';

// 按钮配置
interface ToolbarButtonConfig {
  id: string;
  icon: React.ReactNode;
  label: string;
  shortcut: string;
  action: () => void;
  isActive?: () => boolean;
  isDisabled?: () => boolean;
  isLoading?: () => boolean;
}

// 工具栏组件
const Toolbar: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { rightDrawer, leftDrawer, bottomDrawer } = useDrawers();
  const { theme, toggleTheme } = useTheme();
  const { refresh, isRefreshing } = useData();

  // 按钮配置
  const buttons: ToolbarButtonConfig[] = [
    {
      id: 'menu',
      icon: <Menu />,
      label: '菜单',
      shortcut: 'Esc',
      action: () => setIsExpanded(!isExpanded),
    },
    {
      id: 'analysis',
      icon: <BarChart2 />,
      label: '分析面板',
      shortcut: 'A',
      action: () => rightDrawer.toggle(),
      isActive: () => rightDrawer.isOpen,
    },
    {
      id: 'events',
      icon: <List />,
      label: '事件列表',
      shortcut: 'E',
      action: () => bottomDrawer.toggle(),
      isActive: () => bottomDrawer.isOpen,
    },
    {
      id: 'roles',
      icon: <Users />,
      label: '角色详情',
      shortcut: 'R',
      action: () => leftDrawer.toggle(),
      isActive: () => leftDrawer.isOpen,
    },
    {
      id: 'theme',
      icon: theme === 'dark' ? <Moon /> : <Sun />,
      label: '切换主题',
      shortcut: 'T',
      action: toggleTheme,
    },
    {
      id: 'settings',
      icon: <Settings />,
      label: '设置',
      shortcut: 'S',
      action: () => {/* 打开设置弹窗 */},
    },
    {
      id: 'refresh',
      icon: <RefreshCw />,
      label: '刷新数据',
      shortcut: 'F5',
      action: refresh,
      isLoading: () => isRefreshing,
    },
  ];

  // 快捷键处理
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 忽略输入框内的按键
      if (isInputFocused()) return;

      const shortcutMap: Record<string, string> = {
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

      const buttonId = shortcutMap[e.key];
      if (buttonId) {
        e.preventDefault();
        const button = buttons.find(b => b.id === buttonId);
        if (button && !button.isDisabled?.()) {
          button.action();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [buttons]);

  // 点击外部收起
  useEffect(() => {
    if (!isExpanded) return;

    const handleClickOutside = (e: MouseEvent) => {
      const toolbar = document.querySelector('.toolbar');
      if (toolbar && !toolbar.contains(e.target as Node)) {
        setIsExpanded(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isExpanded]);

  return (
    <div className={`toolbar ${isExpanded ? 'expanded' : ''}`}>
      {buttons.map((btn, index) => (
        <button
          key={btn.id}
          className={`
            toolbar-btn
            ${index === 0 ? 'primary' : ''}
            ${btn.isActive?.() ? 'active' : ''}
            ${btn.isDisabled?.() ? 'disabled' : ''}
            ${btn.isLoading?.() ? 'loading' : ''}
          `}
          onClick={btn.action}
          data-tooltip={btn.label}
          data-shortcut={btn.shortcut}
          disabled={btn.isDisabled?.()}
        >
          {btn.icon}
        </button>
      ))}
    </div>
  );
};
```

---

## 3. 事件标记脉动动画

### 3.1 脉动原理图解

```
事件标记结构 (3层):

      外层光晕 (pulse-outer)
      ┌───────────────────────────────────────┐
      │                                       │
      │     内层光晕 (pulse-inner)            │
      │     ┌───────────────────────────┐     │
      │     │                           │     │
      │     │     核心点 (core)         │     │
      │     │         ●                 │     │
      │     │      12px                 │     │
      │     │                           │     │
      │     └───────────────────────────┘     │
      │           24px                        │
      │                                       │
      └───────────────────────────────────────┘
                    40px
```

### 3.2 脉动动画时间线

```
脉动周期: 2000ms (2秒)

内层光晕 (pulse-inner):
时间    0ms      500ms    1000ms   1500ms   2000ms
       |---------|---------|---------|---------|
缩放    1.0       1.75      2.5      1.0      1.75
透明度  0.8       0.4       0        0.8      0.4
        ○ ──────────────────→ ◯
              扩散消失

外层光晕 (pulse-outer) - 延迟 500ms:
时间    0ms      500ms    1000ms   1500ms   2000ms   2500ms
       |---------|---------|---------|---------|---------|
       [等待]    │
缩放              1.0       1.75      2.5      1.0
透明度            0.6       0.3       0        0.6
                  ○ ──────────────────→ ◯
                        扩散消失 (错峰)

形成波纹效果:
时刻 0ms:    ●           (核心)
时刻 500ms:  ●○          (内层开始扩散)
时刻 1000ms: ●◯○         (内层继续, 外层开始)
时刻 1500ms: ●◯ ○        (内层淡出, 外层扩散)
时刻 2000ms: ●   ○       (内层消失, 外层继续)
```

### 3.3 严重程度样式详解

```css
/* ============================================
   事件标记 - 完整实现
   ============================================ */

/* ===== 标记容器 ===== */
.event-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: var(--z-marker);

  /* 性能优化 */
  will-change: transform;
  contain: layout style;
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

  transition:
    transform 200ms ease,
    box-shadow 200ms ease;
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
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

@keyframes pulseOuter {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.5);
    opacity: 0;
  }
}

/* ===== Severity 5 - 紧急 (红色) ===== */
.event-marker[data-severity="5"] .core {
  background: #EF4444;
  box-shadow:
    0 0 8px #EF4444,
    0 0 16px rgba(239, 68, 68, 0.6),
    0 0 32px rgba(239, 68, 68, 0.3);
}

.event-marker[data-severity="5"] .pulse-inner {
  border: 2px solid #EF4444;
  background: radial-gradient(
    circle,
    rgba(239, 68, 68, 0.4) 0%,
    rgba(239, 68, 68, 0.2) 40%,
    transparent 70%
  );
}

.event-marker[data-severity="5"] .pulse-outer {
  border: 2px solid rgba(239, 68, 68, 0.6);
  background: radial-gradient(
    circle,
    rgba(239, 68, 68, 0.2) 0%,
    transparent 60%
  );
}

/* ===== Severity 4 - 高危 (橙色) ===== */
.event-marker[data-severity="4"] .core {
  background: #F97316;
  box-shadow:
    0 0 6px #F97316,
    0 0 12px rgba(249, 115, 22, 0.6),
    0 0 24px rgba(249, 115, 22, 0.3);
}

.event-marker[data-severity="4"] .pulse-inner {
  border: 2px solid #F97316;
  background: radial-gradient(
    circle,
    rgba(249, 115, 22, 0.4) 0%,
    rgba(249, 115, 22, 0.2) 40%,
    transparent 70%
  );
}

.event-marker[data-severity="4"] .pulse-outer {
  border: 2px solid rgba(249, 115, 22, 0.6);
  background: radial-gradient(
    circle,
    rgba(249, 115, 22, 0.2) 0%,
    transparent 60%
  );
}

/* ===== Severity 3 - 重要 (黄色) ===== */
.event-marker[data-severity="3"] .core {
  background: #F59E0B;
  box-shadow:
    0 0 5px #F59E0B,
    0 0 10px rgba(245, 158, 11, 0.6),
    0 0 20px rgba(245, 158, 11, 0.3);
}

.event-marker[data-severity="3"] .pulse-inner {
  border: 2px solid #F59E0B;
  background: radial-gradient(
    circle,
    rgba(245, 158, 11, 0.4) 0%,
    rgba(245, 158, 11, 0.2) 40%,
    transparent 70%
  );
}

.event-marker[data-severity="3"] .pulse-outer {
  border: 2px solid rgba(245, 158, 11, 0.6);
  background: radial-gradient(
    circle,
    rgba(245, 158, 11, 0.2) 0%,
    transparent 60%
  );
}

/* ===== Severity 2 - 一般 (绿色) ===== */
.event-marker[data-severity="2"] .core {
  background: #22C55E;
  box-shadow:
    0 0 4px #22C55E,
    0 0 8px rgba(34, 197, 94, 0.6),
    0 0 16px rgba(34, 197, 94, 0.3);
}

.event-marker[data-severity="2"] .pulse-inner {
  border: 2px solid #22C55E;
  background: radial-gradient(
    circle,
    rgba(34, 197, 94, 0.4) 0%,
    rgba(34, 197, 94, 0.2) 40%,
    transparent 70%
  );
}

.event-marker[data-severity="2"] .pulse-outer {
  border: 2px solid rgba(34, 197, 94, 0.6);
  background: radial-gradient(
    circle,
    rgba(34, 197, 94, 0.2) 0%,
    transparent 60%
  );
}

/* ===== Severity 1 - 低 (蓝色) ===== */
.event-marker[data-severity="1"] .core {
  background: #3B82F6;
  box-shadow:
    0 0 3px #3B82F6,
    0 0 6px rgba(59, 130, 246, 0.6),
    0 0 12px rgba(59, 130, 246, 0.3);
}

.event-marker[data-severity="1"] .pulse-inner {
  border: 2px solid #3B82F6;
  background: radial-gradient(
    circle,
    rgba(59, 130, 246, 0.4) 0%,
    rgba(59, 130, 246, 0.2) 40%,
    transparent 70%
  );
}

.event-marker[data-severity="1"] .pulse-outer {
  border: 2px solid rgba(59, 130, 246, 0.6);
  background: radial-gradient(
    circle,
    rgba(59, 130, 246, 0.2) 0%,
    transparent 60%
  );
}

/* ===== 悬停效果 ===== */
.event-marker:hover {
  z-index: calc(var(--z-marker) + 10);
}

.event-marker:hover .core {
  transform: translate(-50%, -50%) scale(1.5);
}

.event-marker:hover .pulse-inner,
.event-marker:hover .pulse-outer {
  animation-duration: 1s; /* 加速脉动 */
}

/* ===== 选中效果 ===== */
.event-marker.selected {
  z-index: calc(var(--z-marker) + 20);
}

.event-marker.selected .core {
  transform: translate(-50%, -50%) scale(1.8);
}

.event-marker.selected .pulse-inner,
.event-marker.selected .pulse-outer {
  animation-duration: 1.5s;
  border-width: 3px;
}

/* ===== Tooltip ===== */
.event-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(8px);
  margin-bottom: 16px;

  min-width: 200px;
  max-width: 280px;
  padding: 12px 16px;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 41, 59, 0.8);
  border-radius: 12px;

  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(0, 229, 255, 0.1);

  opacity: 0;
  visibility: hidden;
  transition:
    opacity 150ms ease,
    visibility 150ms ease,
    transform 150ms ease;

  pointer-events: none;
}

.event-marker:hover .event-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

/* Tooltip 小三角 */
.event-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(15, 23, 42, 0.95);
}
```

---

## 4. 颜色规范

### 4.1 颜色系统架构

```
颜色层级结构:

┌─────────────────────────────────────────────────────────────────┐
│                        基础色 (Base)                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │
│  │ 背景色   │ │ 主色调   │ │ 语义色   │ │ 中性色   │               │
│  │ #0A0E1A │ │ #00E5FF │ │ #EF4444 │ │ #F8FAFC │               │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       变体色 (Variants)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 透明色: rgba(base, opacity)                              │   │
│  │ - 5%: 极浅背景                                          │   │
│  │ - 10%: 悬停背景                                         │   │
│  │ - 20%: 选中背景                                         │   │
│  │ - 30%: 边框                                             │   │
│  │ - 40%: 发光                                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 渐变色: linear-gradient(base1, base2)                   │   │
│  │ - 主渐变: cyan → blue                                   │   │
│  │ - 悬停渐变: cyan → purple                               │   │
│  │ - 趋势渐变: success/warning/danger                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 颜色使用场景速查

```css
/* ============================================
   颜色使用场景 - 完整指南
   ============================================ */

/* ===== 背景色使用 ===== */

/* 页面主背景 */
body, .app {
  background: var(--bg-primary);  /* #0A0E1A */
}

/* 卡片/面板背景 */
.card, .panel, .drawer {
  background: var(--bg-secondary);  /* #0F172A */
}

/* 弹窗/下拉菜单背景 */
.modal, .dropdown {
  background: var(--bg-tertiary);  /* #1E293B */
}

/* 遮罩层背景 */
.overlay {
  background: var(--bg-overlay);  /* rgba(0, 0, 0, 0.4) */
}

/* 悬停背景 */
.btn:hover, .card:hover {
  background: rgba(0, 229, 255, 0.1);  /* cyan-10 */
}

/* 选中背景 */
.btn.active, .card.selected {
  background: rgba(0, 229, 255, 0.15);  /* cyan-15 */
}

/* ===== 主色调使用 ===== */

/* 主按钮背景 */
.btn-primary {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
}

/* 强调文字 */
.text-highlight {
  color: var(--accent-cyan);
}

/* 链接 */
a {
  color: var(--accent-blue);
}

/* 边框强调 */
.border-highlight {
  border-color: var(--accent-cyan);
}

/* 发光效果 */
.glow {
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.25);
}

/* ===== 语义色使用 ===== */

/* 错误/紧急 */
.error, .severity-5 {
  color: var(--status-danger);  /* #EF4444 */
}

/* 警告/重要 */
.warning, .severity-3-4 {
  color: var(--status-warning);  /* #F59E0B */
}

/* 成功/正常 */
.success, .severity-1-2 {
  color: var(--status-success);  /* #10B981 */
}

/* 信息提示 */
.info {
  color: var(--status-info);  /* #3B82F6 */
}

/* ===== 文字色使用 ===== */

/* 标题、正文 */
h1, h2, h3, p {
  color: var(--text-primary);  /* #F8FAFC */
}

/* 描述、标签 */
.description, .label {
  color: var(--text-secondary);  /* #94A3B8 */
}

/* 辅助信息、时间戳 */
.timestamp, .meta {
  color: var(--text-muted);  /* #64748B */
}

/* 禁用状态 */
.disabled {
  color: var(--text-disabled);  /* #475569 */
}

/* ===== 边框色使用 ===== */

/* 默认边框 */
.card, .panel {
  border: 1px solid var(--border-default);  /* #1E293B */
}

/* 悬停边框 */
.card:hover {
  border-color: var(--border-light);  /* #334155 */
}

/* 强调边框 */
.card.selected {
  border-color: var(--accent-cyan);  /* #00E5FF */
}
```

### 4.3 颜色对比度验证

| 组合 | 对比度 | WCAG AA | WCAG AAA |
|------|--------|---------|----------|
| text-primary on bg-primary | 15.2:1 | ✓ | ✓ |
| text-secondary on bg-primary | 5.1:1 | ✓ | ✗ |
| text-muted on bg-primary | 3.5:1 | ✓ | ✗ |
| accent-cyan on bg-primary | 8.7:1 | ✓ | ✓ |
| accent-blue on bg-primary | 5.2:1 | ✓ | ✗ |
| status-danger on bg-primary | 4.8:1 | ✓ | ✗ |

---

## 5. 字体间距

### 5.1 字体层级系统

```
字体层级结构:

┌─────────────────────────────────────────────────────────────────┐
│                        H1 - 页面主标题                           │
│                     24px / 600 / 1.25                           │
│                     Inter, Bold                                 │
├─────────────────────────────────────────────────────────────────┤
│                      H2 - 区块标题                               │
│                    20px / 600 / 1.25                            │
│                    Inter, Semibold                              │
├─────────────────────────────────────────────────────────────────┤
│                      H3 - 卡片标题                               │
│                    16px / 600 / 1.375                           │
│                    Inter, Semibold                              │
├─────────────────────────────────────────────────────────────────┤
│                      H4 - 小标题                                 │
│                    14px / 500 / 1.5                             │
│                    Inter, Medium                                │
├─────────────────────────────────────────────────────────────────┤
│                      Body - 正文                                 │
│                    14px / 400 / 1.5                             │
│                    Inter, Normal                                │
├─────────────────────────────────────────────────────────────────┤
│                     Caption - 说明文字                           │
│                    12px / 400 / 1.5                             │
│                    Inter, Normal                                │
├─────────────────────────────────────────────────────────────────┤
│                      Label - 标签                                │
│                  10px / 500 / 1 / uppercase                     │
│                    Inter, Medium                                │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 组件字体规范详解

```css
/* ============================================
   组件字体规范 - 完整指南
   ============================================ */

/* ===== Header 组件 ===== */

/* Logo 标题 */
.header-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}

/* 副标题 */
.header-subtitle {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent-cyan);
}

/* 统计数字 */
.header-stat-value {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.025em;
  color: var(--text-primary);
}

/* 统计标签 */
.header-stat-label {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* ===== 抽屉组件 ===== */

/* 抽屉标题 */
.drawer-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.375;
  color: var(--text-primary);
}

/* 抽屉区块标题 */
.drawer-section-title {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* 抽屉正文 */
.drawer-text {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* ===== 事件卡片 ===== */

/* 卡片标题 */
.event-card-title {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);

  /* 多行截断 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 卡片元信息 */
.event-card-meta {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* 卡片时间 */
.event-card-time {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
}

/* ===== 数据展示 ===== */

/* 大数字 (置信度) */
.data-value-lg {
  font-family: var(--font-mono);
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.05em;
}

/* 中数字 */
.data-value-md {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.025em;
}

/* 小数字 */
.data-value-sm {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 500;
  line-height: 1.25;
}

/* 百分比 */
.data-percentage {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 500;
  line-height: 1;
}

/* 数据标签 */
.data-label {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* ===== 角色分析 ===== */

/* 角色名称 */
.role-name {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);
}

/* 角色类别 */
.role-category {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* 角色立场 */
.role-stance {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* ===== 时间线 ===== */

/* 时间 */
.timeline-time {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 事件描述 */
.timeline-event {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
}

/* 概率 */
.timeline-probability {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
}

/* ===== 按钮 ===== */

/* 按钮文字 */
.btn-text {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.25;
}

/* 小按钮文字 */
.btn-text-sm {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.25;
}

/* ===== 标签 ===== */

/* 标签文字 */
.tag-text {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.25;
}

/* 小标签文字 */
.tag-text-sm {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ===== Tooltip ===== */

/* Tooltip 标题 */
.tooltip-title {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

/* Tooltip 文字 */
.tooltip-text {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
}
```

### 5.3 间距规范详解

```css
/* ============================================
   间距规范 - 完整指南
   ============================================ */

/* ===== 页面级间距 ===== */

/* 页面内边距 */
.page {
  padding: 24px;
}

/* 页面安全区域 */
.page-safe {
  padding: 24px;
}

/* ===== 组件级间距 ===== */

/* Header */
.header {
  height: 68px;
  padding: 0 24px;
  gap: 24px;
}

.header-logo {
  margin-right: 16px;
}

.header-stats {
  gap: 32px;
}

.header-stat {
  gap: 8px;
}

/* 卡片 */
.card {
  padding: 20px;
  border-radius: 12px;
}

.card-header {
  margin-bottom: 16px;
  gap: 12px;
}

.card-body {
  gap: 12px;
}

.card-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-default);
}

/* 事件卡片 */
.event-card {
  width: 280px;
  height: 140px;
  padding: 16px;
  border-radius: 12px;
  margin-right: 16px;  /* 卡片间距 */
}

.event-card-icon {
  margin-right: 12px;
}

.event-card-content {
  gap: 8px;
}

.event-card-footer {
  margin-top: auto;
  padding-top: 12px;
  gap: 8px;
}

/* ===== 抽屉间距 ===== */

.drawer {
  padding: 0;
}

.drawer-header {
  height: 56px;
  padding: 0 20px;
}

.drawer-body {
  padding: 20px;
  gap: 24px;
}

.drawer-section {
  margin-bottom: 24px;
}

.drawer-section:last-child {
  margin-bottom: 0;
}

.drawer-section-title {
  margin-bottom: 12px;
  gap: 8px;
}

/* ===== 列表间距 ===== */

.list-item {
  padding: 12px 16px;
  gap: 12px;
}

.list-item + .list-item {
  border-top: 1px solid var(--border-default);
}

.list-item-icon {
  margin-right: 12px;
}

.list-item-content {
  gap: 4px;
}

/* ===== 表单间距 ===== */

.form-group {
  margin-bottom: 20px;
}

.form-label {
  margin-bottom: 8px;
}

.form-input {
  padding: 10px 14px;
}

.form-error {
  margin-top: 6px;
  font-size: 12px;
}

.form-help {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-muted);
}

/* ===== 按钮组间距 ===== */

.btn-group {
  gap: 12px;
}

.btn-group-sm {
  gap: 8px;
}

.btn-group-lg {
  gap: 16px;
}

/* ===== 标签组间距 ===== */

.tag-group {
  gap: 8px;
}

.tag-group-condensed {
  gap: 4px;
}

/* ===== 网格间距 ===== */

.grid-sm {
  gap: 12px;
}

.grid-md {
  gap: 16px;
}

.grid-lg {
  gap: 24px;
}

.grid-xl {
  gap: 32px;
}

/* ===== 图标与文字间距 ===== */

.icon-text {
  gap: 8px;
}

.icon-text-sm {
  gap: 6px;
}

.icon-text-lg {
  gap: 12px;
}
```

### 5.4 圆角规范详解

```css
/* ============================================
   圆角规范 - 完整指南
   ============================================ */

/* ===== 容器圆角 ===== */

/* 无圆角 */
.radius-none { border-radius: 0; }

/* 小圆角 - 小面板 */
.radius-sm { border-radius: 8px; }

/* 中圆角 - 卡片 */
.radius-md { border-radius: 12px; }

/* 大圆角 - 大面板 */
.radius-lg { border-radius: 16px; }

/* 超大圆角 - 抽屉 */
.radius-xl { border-radius: 20px; }

/* ===== 按钮圆角 ===== */

/* 小按钮 */
.btn-radius-sm { border-radius: 6px; }

/* 中按钮 */
.btn-radius-md { border-radius: 8px; }

/* 大按钮 */
.btn-radius-lg { border-radius: 10px; }

/* 药丸形按钮 */
.btn-radius-full { border-radius: 9999px; }

/* ===== 标签圆角 ===== */

/* 小标签 */
.tag-radius-sm { border-radius: 4px; }

/* 中标签 */
.tag-radius-md { border-radius: 6px; }

/* 药丸形标签 */
.tag-radius-full { border-radius: 9999px; }

/* ===== 输入框圆角 ===== */

/* 小输入框 */
.input-radius-sm { border-radius: 6px; }

/* 中输入框 */
.input-radius-md { border-radius: 8px; }

/* 大输入框 */
.input-radius-lg { border-radius: 10px; }

/* ===== 特殊元素圆角 ===== */

/* 头像 - 圆形 */
.avatar { border-radius: 50%; }

/* 头像 - 方形 */
.avatar-square { border-radius: 8px; }

/* 徽章 */
.badge { border-radius: 9999px; }

/* Tooltip */
.tooltip { border-radius: 12px; }

/* 进度条 */
.progress-bar { border-radius: 9999px; }
```

---

**文档完成** ✓

**实现优先级:**
1. P0 - 抽屉动画 + 工具栏
2. P1 - 事件标记脉动
3. P2 - 颜色/字体规范集成
