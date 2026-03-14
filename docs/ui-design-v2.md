# EventPredictor UI 设计规范 V2.0

> 全屏地球 + 抽屉展开式布局方案
> 基于现有组件结构 `E:\EventPredictor\frontend\src` 重构设计

---

## 目录

1. [设计理念](#1-设计理念)
2. [布局架构](#2-布局架构)
3. [抽屉组件设计](#3-抽屉组件设计)
4. [悬浮工具栏](#4-悬浮工具栏)
5. [颜色规范](#5-颜色规范)
6. [渐变光效](#6-渐变光效)
7. [动画系统](#7-动画系统)
8. [组件映射](#8-组件映射)
9. [实施指南](#9-实施指南)

---

## 1. 设计理念

### 1.1 核心原则

```
┌─────────────────────────────────────────────────────────────────┐
│                        设计哲学                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🌍 沉浸式地球   →   全屏地球占据视觉中心                        │
│   📱 信息按需     →   抽屉展开，减少视觉干扰                      │
│   ✨ 流畅交互     →   自然过渡动画，60fps流畅体验                  │
│   🎨 科技美学     →   玻璃态 + 霓虹光效 + 深空主题                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 布局对比

| 特性 | V1 (现有) | V2 (新版) |
|------|-----------|-----------|
| 地球显示 | 60% 区域 | **全屏 100%** |
| 信息面板 | 固定右侧 40% | **抽屉式展开** |
| 事件列表 | 底部固定 | **抽屉/浮层** |
| 导航 | 顶部Header | **悬浮工具栏** |
| 交互自由度 | 有限 | **高度自由** |

---

## 2. 布局架构

### 2.1 全屏地球主布局

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                                                                      │
│                      ┌─────────────────────┐                        │
│                      │   悬浮工具栏 (左上)   │                        │
│                      └─────────────────────┘                        │
│                                                                      │
│                                                                      │
│                                                                      │
│                         ┌───────────────┐                            │
│                         │               │                            │
│                         │    全屏地球    │                            │
│                         │   GlobeMap     │                            │
│                         │               │                            │
│                         │               │                            │
│                         └───────────────┘                            │
│                                                                      │
│                                                                      │
│                      ┌─────────────────────┐                        │
│                      │  事件提示气泡 (右下)  │                        │
│                      └─────────────────────┘                        │
│                                                                      │
│              ┌────────────────────────────────────┐                 │
│              │     迷你事件栏 (底部可展开)          │                 │
│              └────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 抽屉展开状态

```
┌──────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────┬────────────────────────────────────────────────┐│
│  │                 │                                                ││
│  │   悬浮工具栏     │           抽屉遮罩层 (半透明)                   ││
│  │                 │                                                ││
│  │                 │   ┌────────────────────────────────────────┐   ││
│  │                 │   │                                        │   ││
│  │   全屏地球      │   │         抽屉面板 (400-600px)            │   ││
│  │   (被遮挡部分)   │   │                                        │   ││
│  │                 │   │    • InfoPanel 内容                    │   ││
│  │                 │   │    • EventList 详情                    │   ││
│  │                 │   │    • 分析结果                          │   ││
│  │                 │   │                                        │   ││
│  │                 │   │                                        │   ││
│  │                 │   │    (可滑动/关闭)                        │   ││
│  │                 │   └────────────────────────────────────────┘   ││
│  └─────────────────┴────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 响应式断点

```typescript
const BREAKPOINTS = {
  xs: '0px',      // 手机竖屏
  sm: '640px',    // 手机横屏
  md: '768px',    // 平板竖屏
  lg: '1024px',   // 平板横屏
  xl: '1280px',   // 笔记本
  '2xl': '1536px' // 桌面显示器
};

const DRAWER_WIDTH = {
  xs: '100%',      // 全屏抽屉
  sm: '100%',      // 全屏抽屉
  md: '80%',       // 80% 宽度
  lg: '500px',     // 固定宽度
  xl: '550px',     // 固定宽度
  '2xl': '600px'   // 固定宽度
};
```

---

## 3. 抽屉组件设计

### 3.1 抽屉类型定义

```typescript
// src/components/Drawer/types.ts

export type DrawerPosition = 'left' | 'right' | 'bottom' | 'top';

export type DrawerVariant = 'standard' | 'glass' | 'floating';

export interface DrawerConfig {
  position: DrawerPosition;
  width: string | number;
  variant: DrawerVariant;
  backdrop: boolean;
  backdropOpacity: number;
  closeOnBackdropClick: boolean;
  closeOnEscape: boolean;
  animationDuration: number; // ms
  animationEasing: string;
}
```

### 3.2 抽屉层级架构

```
Z-Index 层级规划
─────────────────────────────────────────────────
  9999  │  Modal / Toast / Notification
  9000  │  ─────────────────────────────
        │  抽屉遮罩层 (Backdrop)
  8000  │  ─────────────────────────────
        │  抽屉面板 (Drawer Panel)
  7000  │  ─────────────────────────────
        │  悬浮工具栏 (FloatingToolbar)
  6000  │  ─────────────────────────────
        │  事件气泡 (EventBubble)
  5000  │  ─────────────────────────────
        │  迷你事件栏 (MiniEventBar)
  1000  │  ─────────────────────────────
        │  地球组件 (GlobeMap)
   100  │  ─────────────────────────────
        │  背景层 (Background)
─────────────────────────────────────────────────
```

### 3.3 抽屉组件结构

```tsx
// src/components/Drawer/Drawer.tsx

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  position?: DrawerPosition;
  width?: string;
  title?: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  showBackdrop?: boolean;
  variant?: DrawerVariant;
}

const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  position = 'right',
  width = '500px',
  title,
  icon,
  children,
  showBackdrop = true,
  variant = 'glass'
}) => {
  // 组件实现...
};
```

### 3.4 抽屉内容区域规划

```
┌────────────────────────────────────────┐
│  ┌──────────────────────────────────┐  │
│  │  ┌─────┐  抽屉标题          ✕  │  │  ← Header (60px)
│  │  │ 🎯  │  事件预测分析          │  │
│  │  └─────┘                        │  │
│  └──────────────────────────────────┘  │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │      可滚动内容区域               │  │  ← Content (flex-1)
│  │                                  │  │
│  │   • InfoPanel 内容               │  │
│  │   • TrendGauge                   │  │
│  │   • ProbabilityBar               │  │
│  │   • KeyInsights                  │  │
│  │   • Timeline 预览                │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │  [查看完整分析]  [关闭]          │  │  ← Footer (56px)
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## 4. 悬浮工具栏

### 4.1 工具栏布局

```
悬浮位置: 左上角 (20px, 80px)
┌────────────────────────┐
│  ┌──┐                  │
│  │≡ │ ← 菜单/导航      │
│  └──┘                  │
│  ┌──┐                  │
│  │🔍│ ← 搜索事件       │
│  └──┘                  │
│  ┌──┐                  │
│  │📊│ ← 数据面板       │
│  └──┘                  │
│  ┌──┐                  │
│  │⚙ │ ← 设置          │
│  └──┘                  │
│  ┌──┐                  │
│  │❓│ ← 帮助          │
│  └──┘                  │
└────────────────────────┘
```

### 4.2 工具栏组件设计

```tsx
// src/components/FloatingToolbar/FloatingToolbar.tsx

interface ToolbarAction {
  id: string;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  badge?: number | string;
  disabled?: boolean;
  active?: boolean;
}

interface FloatingToolbarProps {
  actions: ToolbarAction[];
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const FloatingToolbar: React.FC<FloatingToolbarProps> = ({
  actions,
  position = 'top-left',
  collapsed = false,
  onToggleCollapse
}) => {
  return (
    <div className={cn(
      "floating-toolbar",
      `floating-toolbar--${position}`,
      collapsed && "floating-toolbar--collapsed"
    )}>
      {actions.map(action => (
        <ToolbarButton key={action.id} {...action} />
      ))}
    </div>
  );
};
```

### 4.3 工具栏按钮状态

```
按钮状态设计
─────────────────────────────────────────────────────────

  默认状态          悬停状态          激活状态          禁用状态
  ┌────┐           ┌────┐           ┌────┐           ┌────┐
  │    │           │ ✨ │           │ ▓▓▓ │           │    │
  │ 🔍 │           │ 🔍 │           │ 🔍 │           │ 🔍 │
  │    │           │    │           │    │           │    │
  └────┘           └────┘           └────┘           └────┘

  背景: 透明        背景: 青色       背景: 实心       背景: 暗灰
  边框: 1px        边框: 发光       边框: 加粗       边框: 暗淡
  图标: 白色       图标: 亮白       图标: 黑色       图标: 灰色
```

### 4.4 默认工具栏配置

```typescript
// src/components/FloatingToolbar/defaultActions.ts

import {
  Menu,
  Search,
  BarChart3,
  Settings,
  HelpCircle,
  Bell,
  Layers,
  Maximize2
} from 'lucide-react';

export const defaultToolbarActions: ToolbarAction[] = [
  {
    id: 'menu',
    icon: <Menu />,
    label: '导航菜单',
    onClick: () => openNavigationDrawer()
  },
  {
    id: 'search',
    icon: <Search />,
    label: '搜索事件',
    onClick: () => openSearchModal()
  },
  {
    id: 'dashboard',
    icon: <BarChart3 />,
    label: '数据面板',
    onClick: () => openInfoDrawer(),
    active: true // 当前激活
  },
  {
    id: 'layers',
    icon: <Layers />,
    label: '图层控制',
    onClick: () => toggleLayerPanel()
  },
  {
    id: 'notifications',
    icon: <Bell />,
    label: '通知',
    badge: 3, // 未读数量
    onClick: () => openNotifications()
  },
  {
    id: 'fullscreen',
    icon: <Maximize2 />,
    label: '全屏模式',
    onClick: () => toggleFullscreen()
  },
  {
    id: 'settings',
    icon: <Settings />,
    label: '设置',
    onClick: () => openSettingsDrawer()
  },
  {
    id: 'help',
    icon: <HelpCircle />,
    label: '帮助',
    onClick: () => openHelpModal()
  }
];
```

---

## 5. 颜色规范

### 5.1 主色板

```
主题色系 - 科技蓝青
═══════════════════════════════════════════════════════════════

  青色系 (Cyan)                    紫色系 (Purple)
  ─────────────                   ───────────────

  #00E5FF  ██████  primary-500    #8B5CF6  ██████  secondary-500
  #67E8F9  ██████  primary-300    #A78BFA  ██████  secondary-300
  #22D3EE  ██████  primary-400    #C4B5FD  ██████  secondary-200
  #06B6D4  ██████  primary-600    #7C3AED  ██████  secondary-600
  #0891B2  ██████  primary-700    #6D28D9  ██████  secondary-700
  #155E75  ██████  primary-800    #5B21B6  ██████  secondary-800
```

### 5.2 功能色

```
状态色系
═══════════════════════════════════════════════════════════════

  成功 (Success)                  警告 (Warning)
  ─────────────                  ───────────────
  #10B981  ██████  success-500   #F59E0B  ██████  warning-500
  #34D399  ██████  success-400   #FBBF24  ██████  warning-400
  #059669  ██████  success-600   #D97706  ██████  warning-600

  危险 (Danger)                   信息 (Info)
  ─────────────                   ───────────────
  #EF4444  ██████  danger-500    #3B82F6  ██████  info-500
  #F87171  ██████  danger-400    #60A5FA  ██████  info-400
  #DC2626  ██████  danger-600    #2563EB  ██████  info-600
```

### 5.3 背景色

```
深空背景色系
═══════════════════════════════════════════════════════════════

  层级            色值          用途
  ───────────────────────────────────────────────
  背景-深         #0A0E1A      页面主背景
  背景-中         #0F172A      卡片/面板背景
  背景-浅         #1E293B      次级背景
  背景-悬浮       #334155      悬浮层背景

  渐变背景:
  ┌────────────────────────────────────────────┐
  │  linear-gradient(180deg,                   │
  │    #0A0E1A 0%,      ← 顶部深空             │
  │    #0F172A 50%,     ← 中间过渡             │
  │    #020617 100%     ← 底部星空             │
  │  )                                         │
  └────────────────────────────────────────────┘
```

### 5.4 文字色

```
文字色系
═══════════════════════════════════════════════════════════════

  层级            色值          对比度    用途
  ───────────────────────────────────────────────────────
  主要文字        #F8FAFC      15.3:1    标题、重要内容
  次要文字        #94A3B8      4.9:1     正文、描述
  辅助文字        #64748B      3.5:1     提示、时间戳
  禁用文字        #475569      2.3:1     禁用状态
```

### 5.5 CSS变量定义

```css
/* src/styles/colors.css */

:root {
  /* === 主色 === */
  --color-primary-50: #ECFEFF;
  --color-primary-100: #CFFAFE;
  --color-primary-200: #A5F3FC;
  --color-primary-300: #67E8F9;
  --color-primary-400: #22D3EE;
  --color-primary-500: #00E5FF;
  --color-primary-600: #06B6D4;
  --color-primary-700: #0891B2;
  --color-primary-800: #155E75;
  --color-primary-900: #164E63;

  /* === 辅助色 === */
  --color-secondary-50: #F5F3FF;
  --color-secondary-100: #EDE9FE;
  --color-secondary-200: #DDD6FE;
  --color-secondary-300: #C4B5FD;
  --color-secondary-400: #A78BFA;
  --color-secondary-500: #8B5CF6;
  --color-secondary-600: #7C3AED;
  --color-secondary-700: #6D28D9;
  --color-secondary-800: #5B21B6;
  --color-secondary-900: #4C1D95;

  /* === 功能色 === */
  --color-success-500: #10B981;
  --color-warning-500: #F59E0B;
  --color-danger-500: #EF4444;
  --color-info-500: #3B82F6;

  /* === 背景色 === */
  --bg-deep: #0A0E1A;
  --bg-base: #0F172A;
  --bg-elevated: #1E293B;
  --bg-overlay: #334155;

  /* === 文字色 === */
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-disabled: #475569;

  /* === 边框色 === */
  --border-subtle: #1E293B;
  --border-default: #334155;
  --border-emphasis: #475569;
}
```

---

## 6. 渐变光效

### 6.1 渐变类型

```css
/* src/styles/gradients.css */

:root {
  /* === 主色渐变 === */
  --gradient-primary: linear-gradient(
    135deg,
    #00E5FF 0%,
    #0077FF 50%,
    #8B5CF6 100%
  );

  --gradient-primary-horizontal: linear-gradient(
    90deg,
    #00E5FF 0%,
    #06B6D4 50%,
    #0077FF 100%
  );

  --gradient-primary-vertical: linear-gradient(
    180deg,
    rgba(0, 229, 255, 0.2) 0%,
    rgba(0, 229, 255, 0) 100%
  );

  /* === 背景渐变 === */
  --gradient-bg-deep: radial-gradient(
    ellipse at 50% 0%,
    #0F172A 0%,
    #0A0E1A 50%,
    #020617 100%
  );

  --gradient-bg-glow: radial-gradient(
    circle at 50% 50%,
    rgba(0, 229, 255, 0.1) 0%,
    transparent 50%
  );

  /* === 状态渐变 === */
  --gradient-success: linear-gradient(
    90deg,
    #10B981 0%,
    #34D399 100%
  );

  --gradient-warning: linear-gradient(
    90deg,
    #F59E0B 0%,
    #FBBF24 100%
  );

  --gradient-danger: linear-gradient(
    90deg,
    #EF4444 0%,
    #F87171 100%
  );

  /* === 玻璃渐变 === */
  --gradient-glass: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.05) 100%
  );

  --gradient-glass-border: linear-gradient(
    135deg,
    rgba(0, 229, 255, 0.5) 0%,
    rgba(139, 92, 246, 0.5) 100%
  );
}
```

### 6.2 发光效果

```css
/* === 外发光效果 === */

.glow-cyan {
  box-shadow:
    0 0 20px rgba(0, 229, 255, 0.3),
    0 0 40px rgba(0, 229, 255, 0.2),
    0 0 60px rgba(0, 229, 255, 0.1);
}

.glow-purple {
  box-shadow:
    0 0 20px rgba(139, 92, 246, 0.3),
    0 0 40px rgba(139, 92, 246, 0.2),
    0 0 60px rgba(139, 92, 246, 0.1);
}

.glow-success {
  box-shadow:
    0 0 15px rgba(16, 185, 129, 0.4),
    0 0 30px rgba(16, 185, 129, 0.2);
}

.glow-warning {
  box-shadow:
    0 0 15px rgba(245, 158, 11, 0.4),
    0 0 30px rgba(245, 158, 11, 0.2);
}

.glow-danger {
  box-shadow:
    0 0 15px rgba(239, 68, 68, 0.4),
    0 0 30px rgba(239, 68, 68, 0.2);
}

/* === 边缘发光 === */
.edge-glow {
  position: relative;
}

.edge-glow::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  padding: 2px;
  background: var(--gradient-primary);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
}

/* === 内发光 === */
.inner-glow {
  box-shadow:
    inset 0 0 20px rgba(0, 229, 255, 0.1),
    inset 0 0 40px rgba(0, 229, 255, 0.05);
}

/* === 脉冲发光动画 === */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow:
      0 0 20px rgba(0, 229, 255, 0.3),
      0 0 40px rgba(0, 229, 255, 0.2);
  }
  50% {
    box-shadow:
      0 0 30px rgba(0, 229, 255, 0.5),
      0 0 60px rgba(0, 229, 255, 0.3);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

### 6.3 玻璃态效果

```css
/* === 玻璃态基础 === */
.glass {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* === 玻璃卡片 === */
.glass-card {
  background: linear-gradient(
    135deg,
    rgba(30, 41, 59, 0.8) 0%,
    rgba(15, 23, 42, 0.6) 100%
  );
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(0, 229, 255, 0.2);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* === 玻璃抽屉 === */
.glass-drawer {
  background: linear-gradient(
    180deg,
    rgba(15, 23, 42, 0.95) 0%,
    rgba(10, 14, 26, 0.98) 100%
  );
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border-left: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow:
    -20px 0 60px rgba(0, 0, 0, 0.5),
    inset 2px 0 0 rgba(0, 229, 255, 0.2);
}

/* === 玻璃工具栏 === */
.glass-toolbar {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 12px;
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(0, 229, 255, 0.1);
}
```

### 6.4 地球光效

```css
/* === 地球大气层光效 === */
.globe-atmosphere {
  position: absolute;
  inset: -50px;
  border-radius: 50%;
  background: radial-gradient(
    circle at 30% 30%,
    rgba(0, 229, 255, 0.15) 0%,
    rgba(0, 229, 255, 0.05) 40%,
    transparent 70%
  );
  pointer-events: none;
  animation: atmosphere-rotate 60s linear infinite;
}

@keyframes atmosphere-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* === 地球标记点发光 === */
.globe-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-primary-500);
  box-shadow:
    0 0 10px rgba(0, 229, 255, 0.8),
    0 0 20px rgba(0, 229, 255, 0.5),
    0 0 40px rgba(0, 229, 255, 0.3);
  animation: marker-pulse 1.5s ease-out infinite;
}

@keyframes marker-pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.5);
    opacity: 0.6;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}
```

---

## 7. 动画系统

### 7.1 抽屉展开动画

```css
/* === 抽屉基础动画 === */

/* 右侧抽屉进入 */
@keyframes drawer-slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 右侧抽屉退出 */
@keyframes drawer-slide-out-right {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* 底部抽屉进入 */
@keyframes drawer-slide-in-bottom {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 遮罩层淡入 */
@keyframes backdrop-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 动画类 */
.drawer-enter {
  animation: drawer-slide-in-right 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.drawer-exit {
  animation: drawer-slide-out-right 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.drawer-backdrop-enter {
  animation: backdrop-fade-in 0.3s ease-out forwards;
}
```

### 7.2 弹簧动画配置

```typescript
// src/utils/animations.ts

import { type Variants } from 'framer-motion';

// 抽屉动画配置
export const drawerVariants: Variants = {
  closed: {
    x: '100%',
    opacity: 0,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 40,
    }
  },
  open: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 40,
    }
  }
};

// 遮罩动画配置
export const backdropVariants: Variants = {
  closed: {
    opacity: 0,
    transition: {
      duration: 0.3,
    }
  },
  open: {
    opacity: 1,
    transition: {
      duration: 0.3,
    }
  }
};

// 工具栏按钮悬停动画
export const toolbarButtonVariants: Variants = {
  rest: {
    scale: 1,
    boxShadow: '0 0 0 rgba(0, 229, 255, 0)',
  },
  hover: {
    scale: 1.1,
    boxShadow: '0 0 20px rgba(0, 229, 255, 0.4)',
    transition: {
      type: 'spring',
      stiffness: 400,
      damping: 10,
    }
  },
  tap: {
    scale: 0.95,
  }
};

// 内容淡入动画
export const contentVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.16, 1, 0.3, 1],
    }
  }
};

// 交错动画
export const staggerContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    }
  }
};

export const staggerItemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.16, 1, 0.3, 1],
    }
  }
};
```

### 7.3 缓动函数

```css
/* src/styles/easings.css */

:root {
  /* === 标准缓动 === */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);

  /* === 弹性缓动 === */
  --ease-spring: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

  /* === 平滑缓动 === */
  --ease-smooth: cubic-bezier(0.25, 0.1, 0.25, 1);
  --ease-swift: cubic-bezier(0.55, 0, 0.1, 1);
}

/* 动画时长 */
:root {
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 400ms;
  --duration-slower: 500ms;
}
```

### 7.4 Framer Motion 抽屉实现

```tsx
// src/components/Drawer/Drawer.tsx

import { motion, AnimatePresence } from 'framer-motion';

const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  children,
  position = 'right',
  width = '500px',
  title,
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* 遮罩层 */}
          <motion.div
            className="drawer-backdrop"
            variants={backdropVariants}
            initial="closed"
            animate="open"
            exit="closed"
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
              zIndex: 8000,
            }}
          />

          {/* 抽屉面板 */}
          <motion.div
            className="drawer-panel glass-drawer"
            variants={drawerVariants}
            initial="closed"
            animate="open"
            exit="closed"
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width,
              zIndex: 9000,
            }}
          >
            {/* 抽屉头部 */}
            <div className="drawer-header">
              <h2 className="drawer-title">{title}</h2>
              <button onClick={onClose} className="drawer-close">
                <X />
              </button>
            </div>

            {/* 抽屉内容 */}
            <motion.div
              className="drawer-content"
              variants={contentVariants}
              initial="hidden"
              animate="visible"
            >
              {children}
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
```

---

## 8. 组件映射

### 8.1 现有组件到新架构的映射

| 现有组件 | 原位置 | 新位置 | 说明 |
|---------|--------|--------|------|
| `GlobeMap.tsx` | 全屏60% | **全屏100%** | 作为背景层，Z-index降低 |
| `InfoPanel.tsx` | 右侧固定 | **抽屉内** | 通过工具栏按钮触发 |
| `EventList.tsx` | 底部固定 | **迷你栏+抽屉** | 底部收缩栏，点击展开 |
| `Home.tsx` | 主页 | **保留** | 集成新布局组件 |
| `AnalysisResult.tsx` | 分析页 | **抽屉内** | 作为抽屉内容展示 |

### 8.2 新增组件

```
src/components/
├── Drawer/
│   ├── index.ts              # 导出
│   ├── Drawer.tsx            # 抽屉主组件
│   ├── DrawerHeader.tsx      # 抽屉头部
│   ├── DrawerContent.tsx     # 抽屉内容
│   ├── DrawerFooter.tsx      # 抽屉底部
│   ├── Drawer.types.ts       # 类型定义
│   └── Drawer.module.css     # 样式
│
├── FloatingToolbar/
│   ├── index.ts
│   ├── FloatingToolbar.tsx   # 悬浮工具栏
│   ├── ToolbarButton.tsx     # 工具栏按钮
│   ├── ToolbarAction.tsx     # 工具栏操作
│   └── Toolbar.module.css
│
├── MiniEventBar/
│   ├── index.ts
│   ├── MiniEventBar.tsx      # 迷你事件栏
│   ├── EventBubble.tsx       # 事件气泡
│   └── MiniEventBar.module.css
│
├── EventDrawer/
│   ├── index.ts
│   ├── EventDrawer.tsx       # 事件抽屉(整合InfoPanel)
│   └── EventDrawer.module.css
│
└── GlobeOverlay/
    ├── index.ts
    ├── GlobeOverlay.tsx      # 地球叠加层(标记、气泡)
    └── GlobeOverlay.module.css
```

### 8.3 组件依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        Home.tsx (重构)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  GlobeMap    │  │FloatingToolbar│  │ MiniEventBar │          │
│  │  (全屏背景)   │  │  (悬浮左上)   │  │  (底部收缩)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                  │
│         │                 │                  │                  │
│         ▼                 ▼                  ▼                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Drawer (容器)                        │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ EventDrawer │  │ InfoPanel   │  │AnalysisResult│     │   │
│  │  │ (事件详情)   │  │ (预测面板)   │  │ (分析页)    │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. 实施指南

### 9.1 文件创建顺序

```
Phase 1: 基础组件 (1-2天)
────────────────────────────────────────
1. src/styles/colors.css          # 颜色变量
2. src/styles/gradients.css       # 渐变光效
3. src/styles/easings.css         # 缓动函数
4. src/utils/animations.ts        # 动画配置

Phase 2: 抽屉系统 (2-3天)
────────────────────────────────────────
5. src/components/Drawer/Drawer.types.ts
6. src/components/Drawer/Drawer.module.css
7. src/components/Drawer/Drawer.tsx
8. src/components/Drawer/DrawerHeader.tsx
9. src/components/Drawer/DrawerContent.tsx
10. src/components/Drawer/DrawerFooter.tsx
11. src/components/Drawer/index.ts

Phase 3: 工具栏系统 (1-2天)
────────────────────────────────────────
12. src/components/FloatingToolbar/FloatingToolbar.tsx
13. src/components/FloatingToolbar/ToolbarButton.tsx
14. src/components/FloatingToolbar/Toolbar.module.css
15. src/components/FloatingToolbar/defaultActions.ts
16. src/components/FloatingToolbar/index.ts

Phase 4: 事件栏系统 (1-2天)
────────────────────────────────────────
17. src/components/MiniEventBar/MiniEventBar.tsx
18. src/components/MiniEventBar/EventBubble.tsx
19. src/components/MiniEventBar/MiniEventBar.module.css
20. src/components/MiniEventBar/index.ts

Phase 5: 整合重构 (2-3天)
────────────────────────────────────────
21. 重构 src/pages/Home.tsx
22. 适配 src/components/GlobeMap.tsx
23. 适配 src/components/InfoPanel.tsx
24. 创建 src/components/EventDrawer/
25. 集成测试与调优
```

### 9.2 Home.tsx 重构示例

```tsx
// src/pages/Home.tsx (重构后)

import { useState } from 'react';
import GlobeMap from '../components/GlobeMap';
import FloatingToolbar from '../components/FloatingToolbar';
import MiniEventBar from '../components/MiniEventBar';
import Drawer from '../components/Drawer';
import InfoPanel from '../components/InfoPanel';
import { defaultToolbarActions } from '../components/FloatingToolbar/defaultActions';

const Home: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerContent, setDrawerContent] = useState<'info' | 'events' | 'settings'>('info');

  const handleToolbarAction = (actionId: string) => {
    switch (actionId) {
      case 'dashboard':
        setDrawerContent('info');
        setDrawerOpen(true);
        break;
      case 'events':
        setDrawerContent('events');
        setDrawerOpen(true);
        break;
      // ... 其他操作
    }
  };

  return (
    <div className="home-container">
      {/* 全屏地球背景 */}
      <div className="globe-container">
        <GlobeMap
          events={events}
          selectedEvent={selectedEvent}
          onEventSelect={handleEventSelect}
          fullscreen
        />
      </div>

      {/* 悬浮工具栏 */}
      <FloatingToolbar
        actions={defaultToolbarActions.map(action => ({
          ...action,
          onClick: () => handleToolbarAction(action.id)
        }))}
        position="top-left"
      />

      {/* 迷你事件栏 */}
      <MiniEventBar
        events={events}
        onExpand={() => {
          setDrawerContent('events');
          setDrawerOpen(true);
        }}
      />

      {/* 抽屉面板 */}
      <Drawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerContent === 'info' ? '事件预测分析' : '事件列表'}
      >
        {drawerContent === 'info' && (
          <InfoPanel event={selectedEvent} />
        )}
        {drawerContent === 'events' && (
          <EventList events={events} onSelect={handleEventSelect} />
        )}
      </Drawer>
    </div>
  );
};
```

### 9.3 样式导入顺序

```css
/* src/index.css */

/* 1. Tailwind 基础 */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 2. 设计系统变量 */
@import './styles/colors.css';
@import './styles/gradients.css';
@import './styles/easings.css';

/* 3. 动画关键帧 */
@import './styles/animations.css';

/* 4. 全局基础样式 */
@import './styles/base.css';

/* 5. 组件样式 */
@import './components/Drawer/Drawer.module.css';
@import './components/FloatingToolbar/Toolbar.module.css';
@import './components/MiniEventBar/MiniEventBar.module.css';
```

### 9.4 依赖安装

```bash
# 动画库 (如果尚未安装)
npm install framer-motion

# 类型定义
npm install -D @types/react
```

### 9.5 验收标准

```
✅ 功能验收
────────────────────────────────────────
□ 全屏地球正常渲染，支持缩放和旋转
□ 悬浮工具栏显示正确，按钮可点击
□ 工具栏按钮悬停有发光效果
□ 抽屉可以从右侧滑入滑出
□ 抽屉遮罩层可点击关闭
□ 迷你事件栏底部显示，可展开
□ 事件列表在抽屉内正常显示
□ 信息面板内容在抽屉内正常显示

✅ 动画验收
────────────────────────────────────────
□ 抽屉展开动画流畅 (60fps)
□ 背遮罩层渐变自然
□ 按钮悬停动画弹性自然
□ 内容淡入有交错效果
□ 无卡顿或闪烁现象

✅ 样式验收
────────────────────────────────────────
□ 玻璃态效果正确显示
□ 发光效果边界清晰
□ 颜色符合设计规范
□ 渐变过渡平滑
□ 暗色主题一致

✅ 响应式验收
────────────────────────────────────────
□ 手机端抽屉全屏显示
□ 平板端抽屉80%宽度
□ 桌面端抽屉固定宽度
□ 工具栏位置自适应
□ 迷你事件栏适配不同屏幕
```

---

## 附录

### A. 完整颜色代码参考

```typescript
// src/constants/colors.ts

export const COLORS = {
  primary: {
    cyan: '#00E5FF',
    blue: '#0077FF',
    light: '#67E8F9',
    dark: '#0891B2',
  },
  secondary: {
    purple: '#8B5CF6',
    light: '#A78BFA',
    dark: '#6D28D9',
  },
  status: {
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#3B82F6',
  },
  bg: {
    deep: '#0A0E1A',
    base: '#0F172A',
    elevated: '#1E293B',
    overlay: '#334155',
  },
  text: {
    primary: '#F8FAFC',
    secondary: '#94A3B8',
    muted: '#64748B',
    disabled: '#475569',
  },
  border: {
    subtle: '#1E293B',
    default: '#334155',
    emphasis: '#475569',
  },
  glass: {
    base: 'rgba(15, 23, 42, 0.6)',
    elevated: 'rgba(30, 41, 59, 0.8)',
    highlight: 'rgba(0, 229, 255, 0.2)',
  },
} as const;

export const GRADIENTS = {
  primary: 'linear-gradient(135deg, #00E5FF 0%, #0077FF 50%, #8B5CF6 100%)',
  primaryHorizontal: 'linear-gradient(90deg, #00E5FF 0%, #06B6D4 50%, #0077FF 100%)',
  bgDeep: 'radial-gradient(ellipse at 50% 0%, #0F172A 0%, #0A0E1A 50%, #020617 100%)',
  glass: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
  glassBorder: 'linear-gradient(135deg, rgba(0,229,255,0.5) 0%, rgba(139,92,246,0.5) 100%)',
} as const;
```

### B. 动画时长配置

```typescript
// src/constants/animations.ts

export const DURATION = {
  instant: 100,
  fast: 200,
  normal: 300,
  slow: 400,
  slower: 500,
} as const;

export const EASING = {
  inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  out: 'cubic-bezier(0, 0, 0.2, 1)',
  in: 'cubic-bezier(0.4, 0, 1, 1)',
  spring: 'cubic-bezier(0.16, 1, 0.3, 1)',
  bounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const;
```

---

**文档版本**: V2.0
**创建日期**: 2026-03-14
**适用项目**: EventPredictor Frontend
**基于组件**: `E:\EventPredictor\frontend\src`
