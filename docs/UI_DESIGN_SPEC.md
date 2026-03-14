# EventPredictor UI 设计规范

> **版本**: v3.0
> **日期**: 2026-03-14
> **状态**: 完整规范
> **适用范围**: EventPredictor 全球态势推演大屏

---

## 目录

1. [设计理念](#1-设计理念)
2. [设计 Tokens](#2-设计-tokens)
3. [整体布局](#3-整体布局)
4. [组件系统](#4-组件系统)
5. [抽屉系统](#5-抽屉系统)
6. [工具栏系统](#6-工具栏系统)
7. [事件标记系统](#7-事件标记系统)
8. [动画规范](#8-动画规范)
9. [响应式设计](#9-响应式设计)
10. [可访问性规范](#10-可访问性规范)

---

## 1. 设计理念

### 1.1 核心原则

| 原则 | 英文 | 描述 | 实现方式 |
|------|------|------|----------|
| 极简初始 | Minimal Initial | 打开时界面干净整洁 | 全屏地球 + 精简底部信息 |
| 按需展开 | Progressive Disclosure | 通过抽屉逐步显示内容 | 多级抽屉系统 |
| 层级叠加 | Layered UI | Z-index 层级管理界面元素 | 抽屉叠加显示 |
| 高端大气 | Premium Feel | 深色科技风 + 光效动效 | 渐变 + 发光动画 |
| 微交互 | Micro-interactions | 精细的交互反馈 | 150-300ms 过渡动画 |

### 1.2 视觉风格

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   风格关键词:                                                    │
│                                                                 │
│   🌌 深空科技感    - 深色背景 + 星空氛围                          │
│   ✨ 光效美学      - 渐变 + 发光 + 流光效果                       │
│   🔮 玻璃拟态      - 毛玻璃 + 半透明叠加                          │
│   ⚡ 动态反馈      - 脉动 + 呼吸 + 平滑过渡                       │
│   🎯 数据可视化    - 清晰的信息层级                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 层级架构 (Z-index Map)

```
层级高度
    ▲
    │
1000├─────────────────────────────────────────────────
    │  📱 Modal / Toast        弹窗、提示
    │
 900├─────────────────────────────────────────────────
    │  📋 右侧抽屉             分析结果面板
    │
 800├─────────────────────────────────────────────────
    │  📋 底部抽屉             事件列表
    │
 700├─────────────────────────────────────────────────
    │  📋 左侧抽屉             角色详情
    │
 600├─────────────────────────────────────────────────
    │  🔧 悬浮工具栏           功能按钮
    │
 500├─────────────────────────────────────────────────
    │  💬 Tooltip              悬停提示
    │
 400├─────────────────────────────────────────────────
    │  📍 事件标记             地图上的点
    │
 100├─────────────────────────────────────────────────
    │  🌍 3D 地球              主视觉
    │
   0├─────────────────────────────────────────────────
    │  🎨 背景层               最底层
    ▼
```

---

## 2. 设计 Tokens

### 2.1 颜色 Tokens

#### 2.1.1 背景色

| Token | 值 | 用途 |
|-------|-----|------|
| `--bg-primary` | `#0A0E1A` | 页面主背景 - 深空蓝黑 |
| `--bg-secondary` | `#0F172A` | 卡片/面板背景 |
| `--bg-tertiary` | `#1E293B` | 第三级背景、抬起元素 |
| `--bg-elevated` | `#1E293B` | 弹窗、下拉菜单 |
| `--bg-overlay` | `rgba(0, 0, 0, 0.4)` | 遮罩层 |

#### 2.1.2 主色调 (Accent)

| Token | 值 | 用途 |
|-------|-----|------|
| `--accent-cyan` | `#00E5FF` | 主强调色 - 科技青 |
| `--accent-blue` | `#0077FF` | 次强调色 - 科技蓝 |
| `--accent-purple` | `#8B5CF6` | 特殊强调 - 科技紫 |
| `--accent-pink` | `#EC4899` | 点缀色 - 科技粉 |

#### 2.1.3 语义色 (Semantic)

| Token | 值 | 严重度 | 用途 |
|-------|-----|--------|------|
| `--status-danger` | `#EF4444` | 5 | 紧急/错误 |
| `--status-warning` | `#F59E0B` | 3-4 | 警告/重要 |
| `--status-success` | `#10B981` | 1-2 | 成功/正常 |
| `--status-info` | `#3B82F6` | - | 信息提示 |

#### 2.1.4 文字色

| Token | 值 | 对比度 | 用途 |
|-------|-----|--------|------|
| `--text-primary` | `#F8FAFC` | 15.2:1 | 标题、正文 |
| `--text-secondary` | `#94A3B8` | 5.1:1 | 次要信息 |
| `--text-muted` | `#64748B` | 3.5:1 | 辅助信息 |
| `--text-disabled` | `#475569` | 2.4:1 | 禁用状态 |

#### 2.1.5 边框色

| Token | 值 | 用途 |
|-------|-----|------|
| `--border-default` | `#1E293B` | 默认边框 |
| `--border-light` | `#334155` | 浅色边框 |
| `--border-accent` | `#00E5FF` | 强调边框 |

#### 2.1.6 透明色

| Token | 值 | 用途 |
|-------|-----|------|
| `--cyan-5` | `rgba(0, 229, 255, 0.05)` | 极浅背景 |
| `--cyan-10` | `rgba(0, 229, 255, 0.1)` | 悬停背景 |
| `--cyan-20` | `rgba(0, 229, 255, 0.2)` | 选中背景 |
| `--cyan-30` | `rgba(0, 229, 255, 0.3)` | 边框 |
| `--cyan-40` | `rgba(0, 229, 255, 0.4)` | 发光 |

### 2.2 字体 Tokens

#### 2.2.1 字体家族

```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, monospace;
--font-chinese: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
--font-display: 'Inter', 'PingFang SC', sans-serif;
```

#### 2.2.2 字体大小

| Token | 值 | 行高 | 用途 |
|-------|-----|------|------|
| `--text-xs` | 10px | 1 | 极小 - 标签 |
| `--text-sm` | 12px | 1.5 | 小号 - 次要信息 |
| `--text-base` | 14px | 1.5 | 基础 - 正文 |
| `--text-md` | 16px | 1.375 | 中号 - 小标题 |
| `--text-lg` | 20px | 1.25 | 大号 - 标题 |
| `--text-xl` | 24px | 1.25 | 超大 - 主标题 |
| `--text-2xl` | 32px | 1 | 巨大 - 数据展示 |
| `--text-3xl` | 48px | 1 | 特大 - 关键数据 |

#### 2.2.3 字重

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-normal` | 400 | 正文 |
| `--font-medium` | 500 | 小标题 |
| `--font-semibold` | 600 | 标题 |
| `--font-bold` | 700 | 大标题 |

#### 2.2.4 字间距

| Token | 值 | 用途 |
|-------|-----|------|
| `--tracking-tight` | -0.025em | 大标题 |
| `--tracking-normal` | 0 | 正文 |
| `--tracking-wide` | 0.025em | 小标题 |
| `--tracking-wider` | 0.05em | 标签 |

### 2.3 间距 Tokens

#### 2.3.1 基础间距 (4px 基准)

| Token | 值 | 名称 | 用途 |
|-------|-----|------|------|
| `--space-0` | 0 | 无 | - |
| `--space-1` | 4px | 极小 | 元素内部紧凑间距 |
| `--space-2` | 8px | 小 | 图标与文字间距 |
| `--space-3` | 12px | 中小 | 列表项内边距 |
| `--space-4` | 16px | 基础 | 卡片内边距 |
| `--space-5` | 20px | 中等 | 面板内边距 |
| `--space-6` | 24px | 常用 | 区块间距 |
| `--space-8` | 32px | 大 | 抽屉内边距 |
| `--space-10` | 40px | 较大 | - |
| `--space-12` | 48px | 大区块 | - |
| `--space-16` | 64px | 超大 | 页面级间距 |

### 2.4 圆角 Tokens

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 4px | 小标签 |
| `--radius-md` | 8px | 按钮、输入框 |
| `--radius-lg` | 12px | 卡片、面板 |
| `--radius-xl` | 16px | 抽屉头部 |
| `--radius-2xl` | 20px | 大面板 |
| `--radius-full` | 9999px | 药丸形、圆形 |

### 2.5 阴影 Tokens

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `0 2px 8px rgba(0, 0, 0, 0.15)` | 轻微抬起 |
| `--shadow-md` | `0 4px 16px rgba(0, 0, 0, 0.2)` | 卡片 |
| `--shadow-lg` | `0 8px 32px rgba(0, 0, 0, 0.25)` | 抽屉 |
| `--shadow-glow-cyan` | `0 0 20px rgba(0, 229, 255, 0.25)` | 青色发光 |
| `--shadow-glow-danger` | `0 0 20px rgba(239, 68, 68, 0.3)` | 危险发光 |

### 2.6 动画 Tokens

| Token | 值 | 用途 |
|-------|-----|------|
| `--duration-fast` | 150ms | Tooltip、悬停 |
| `--duration-normal` | 200ms | 按钮状态切换 |
| `--duration-slow` | 300ms | 抽屉展开 |
| `--easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | 标准缓动 |
| `--easing-bounce` | `cubic-bezier(0.68, -0.55, 0.265, 1.55)` | 弹性缓动 |

### 2.7 布局 Tokens

| Token | 值 | 用途 |
|-------|-----|------|
| `--drawer-width-sm` | 280px | 小抽屉 |
| `--drawer-width-md` | 320px | 中抽屉 |
| `--drawer-width-lg` | 360px | 大抽屉 |
| `--toolbar-btn-size` | 48px | 工具栏按钮 |
| `--event-card-width` | 280px | 事件卡片 |
| `--event-card-height` | 140px | 事件卡片 |

---

## 3. 整体布局

### 3.1 页面结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                                                                             │
│                                                                             │
│                          🌍 全屏 3D 地球                                     │
│                                                                             │
│                          (事件标记脉动动画)                                   │
│                                                                             │
│                                                                             │
│                                                                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ [≡]                                               当前事件: xxx    [⋯]      │
│ 工具栏                                            (点击展开面板)    更多      │
│ (左下角固定)                                                       (右下角)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 尺寸规格 (1920x1080 基准)

| 区域 | 尺寸 | 说明 |
|------|------|------|
| 地球区域 | 1920x1032px | 全屏减去底部栏 |
| 底部信息栏 | 1920x48px | 固定高度 |
| 工具栏位置 | left: 24px, bottom: 24px | 左下角 |
| 当前事件位置 | right: 80px, bottom: 24px | 右下角偏左 |
| 更多按钮位置 | right: 24px, bottom: 24px | 右下角 |

### 3.3 安全区域

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ← 24px →                                                          ← 24px →│
│   ┌─────┐                                                                   │
│   │ ≡   │                                           ┌──────────────┐        │
│   │工具栏│                                           │  当前事件     │  ┌───┐ │
│   └─────┘                                           │  xxx xxx     │  │⋯ │ │
│                                                     └──────────────┘  └───┘ │
│   ↑ 24px                                                              ↑ 24px│
│   ↓                                                              ↓         │
├─────────────────────────────────────────────────────────────────────────────┤
│                              48px 底部栏                                     │
└─────────────────────────────────────────────────────────────────────────────┘
         ↑ 24px
```

---

## 4. 组件系统

### 4.1 按钮组件

#### 4.1.1 按钮类型

| 类型 | 样式 | 使用场景 |
|------|------|----------|
| Primary | 渐变填充 | 主要操作 |
| Secondary | 描边 | 次要操作 |
| Ghost | 无背景 | 工具栏按钮 |
| Danger | 红色 | 危险操作 |

#### 4.1.2 按钮尺寸

| 尺寸 | 高度 | 内边距 | 字号 |
|------|------|--------|------|
| Small | 32px | 8px 12px | 12px |
| Medium | 40px | 10px 16px | 14px |
| Large | 48px | 12px 24px | 16px |

#### 4.1.3 按钮样式

```css
/* Primary 按钮 */
.btn-primary {
  height: 40px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all var(--duration-normal) var(--easing-default);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-cyan);
}

.btn-primary:active {
  transform: translateY(0) scale(0.98);
}

/* Secondary 按钮 */
.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  background: var(--cyan-10);
}

/* Ghost 按钮 */
.btn-ghost {
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.btn-ghost:hover {
  background: var(--cyan-10);
  border-color: var(--cyan-30);
  color: var(--accent-cyan);
}

/* Danger 按钮 */
.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--status-danger);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}
```

### 4.2 卡片组件

#### 4.2.1 事件卡片

```
┌─────────────────────────────────────┐
│ 🔴  美军航母进入南海                  │  ← 标题 (14px, 600)
│                                     │
│     南海海域 · 2小时前               │  ← 元信息 (12px, 400)
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 紧急                     查看 → │ │  ← 底部
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

尺寸: 280px × 140px
内边距: 16px
圆角: 12px
```

```css
.event-card {
  width: 280px;
  height: 140px;
  padding: 16px;
  border-radius: var(--radius-lg);
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-default);
  cursor: pointer;
  transition: all var(--duration-normal) var(--easing-default);
}

.event-card:hover {
  border-color: var(--border-light);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.event-card.selected {
  border-color: var(--accent-cyan);
  box-shadow:
    var(--shadow-md),
    0 0 0 1px var(--cyan-30);
}
```

### 4.3 标签组件

```css
/* 默认标签 */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
}

/* 严重程度标签 */
.tag-danger {
  background: rgba(239, 68, 68, 0.2);
  color: var(--status-danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.tag-warning {
  background: rgba(245, 158, 11, 0.2);
  color: var(--status-warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.tag-success {
  background: rgba(16, 185, 129, 0.2);
  color: var(--status-success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}
```

### 4.4 进度条组件

```css
/* 置信度进度条 */
.confidence-bar {
  height: 8px;
  border-radius: var(--radius-full);
  background: rgba(30, 41, 59, 0.8);
  overflow: hidden;
}

.confidence-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.5s var(--easing-default);
}

/* 低置信度 (< 50%) */
.confidence-bar-fill.low {
  background: linear-gradient(90deg, var(--status-danger), var(--status-warning));
}

/* 中置信度 (50% - 75%) */
.confidence-bar-fill.medium {
  background: linear-gradient(90deg, var(--status-warning), #EAB308);
}

/* 高置信度 (> 75%) */
.confidence-bar-fill.high {
  background: linear-gradient(90deg, var(--status-success), var(--accent-cyan));
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}
```

---

## 5. 抽屉系统

### 5.1 抽屉类型

| 类型 | 位置 | 宽度/高度 | 触发方式 |
|------|------|-----------|----------|
| 右侧抽屉 | right | 360px | 点击事件标记/当前事件 |
| 底部抽屉 | bottom | 48px→200px | 点击事件列表按钮 |
| 左侧抽屉 | left | 320px | 点击查看完整分析 |

### 5.2 右侧抽屉 - 分析面板

```
展开状态:

┌────────────────────────────────┐
│ ◀ 趋势预测              [×]   │  ← Header (56px)
├────────────────────────────────┤
│                                │
│  ↑ 上涨              75%       │  ← 趋势 + 置信度
│  ████████████████░░░           │
│                                │
├────────────────────────────────┤
│  📌 关键洞察                   │
│  • 美方可能增派舰艇             │
│  • 中方或将加强巡航             │
│                                │
├────────────────────────────────┤
│  ⚠️ 风险: 高                   │
│  🔥 冲突: 3                    │
│                                │
├────────────────────────────────┤
│  ⏱ 时间线                      │
│  ○ 24h: 舰艇集结 (85%)         │
│  ○ 72h: 外交磋商 (60%)         │
│                                │
├────────────────────────────────┤
│  [    查看完整分析 →    ]      │  ← Footer 按钮
└────────────────────────────────┘
```

### 5.3 底部抽屉 - 事件列表

```
收起状态 (48px):
┌────────────────────────────────────────────────────────────────┐
│  ▼ 事件列表 (5)                                        [×]     │
└────────────────────────────────────────────────────────────────┘

展开状态 (200px):
┌────────────────────────────────────────────────────────────────┐
│  ▲ 事件列表 (5)                                        [×]     │
├────────────────────────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │事件1│ │事件2│ │事件3│ │事件4│ │事件5│  ← 横向滚动          │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
└────────────────────────────────────────────────────────────────┘
```

### 5.4 左侧抽屉 - 角色详情

```
┌────────────────────────────────┐
│ [×]                    16角色  │
├────────────────────────────────┤
│ 🇨🇳 中国政府                   │
│    立场: 维护主权              │
│    行动: 加强巡航              │
│    置信度: 82%                 │
├────────────────────────────────┤
│ 🇺🇸 美国政府                   │
│    立场: 航行自由              │
│    行动: 继续存在              │
│    置信度: 78%                 │
├────────────────────────────────┤
│ ... 更多角色                   │
└────────────────────────────────┘
```

### 5.5 抽屉动画参数

| 抽屉 | 展开时长 | 收起时长 | 缓动函数 |
|------|----------|----------|----------|
| 右侧 | 300ms | 250ms | cubic-bezier(0.4, 0, 0.2, 1) |
| 底部 | 250ms | 200ms | 同上 |
| 左侧 | 280ms | 240ms | 同上 |

---

## 6. 工具栏系统

### 6.1 工具栏布局

```
收起状态:                    展开状态:

┌───┐                        ┌───┐
│ ≡ │                        │ ≡ │  ← 主菜单 (0ms)
└───┘                        ├───┤
                             │ 📊 │  ← 分析 (50ms)
                             ├───┤
                             │ 📋 │  ← 事件 (100ms)
                             ├───┤
                             │ 👥 │  ← 角色 (150ms)
                             ├───┤
                             │ 🌙 │  ← 主题 (200ms)
                             ├───┤
                             │ ⚙️ │  ← 设置 (250ms)
                             ├───┤
                             │ 🔄 │  ← 刷新 (300ms)
                             └───┘
```

### 6.2 按钮功能

| 按钮 | 图标 | 快捷键 | 功能 |
|------|------|--------|------|
| 主菜单 | ≡ | Esc | 展开/收起工具栏 |
| 分析面板 | 📊 | A | 切换右侧抽屉 |
| 事件列表 | 📋 | E | 切换底部抽屉 |
| 角色详情 | 👥 | R | 切换左侧抽屉 |
| 主题切换 | 🌙/☀️ | T | 深色/浅色主题 |
| 设置 | ⚙️ | S | 打开设置弹窗 |
| 刷新 | 🔄 | F5 | 重新获取数据 |

### 6.3 按钮状态

```css
/* 默认状态 */
.toolbar-btn {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-default);
}

/* 悬停状态 */
.toolbar-btn:hover {
  transform: translateY(-4px) scale(1.05);
  background: var(--cyan-10);
  border-color: var(--cyan-30);
  box-shadow: var(--shadow-glow-cyan);
}

/* 激活状态 (抽屉打开) */
.toolbar-btn.active {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border: none;
  box-shadow: var(--shadow-glow-cyan);
}

/* 禁用状态 */
.toolbar-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 加载状态 */
.toolbar-btn.loading svg {
  animation: spin 1s linear infinite;
}
```

---

## 7. 事件标记系统

### 7.1 标记结构

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

### 7.2 严重程度颜色

| 级别 | 颜色 | 色值 | 发光色 |
|------|------|------|--------|
| 5-紧急 | 🔴 红色 | #EF4444 | rgba(239, 68, 68, 0.6) |
| 4-高危 | 🟠 橙色 | #F97316 | rgba(249, 115, 22, 0.6) |
| 3-重要 | 🟡 黄色 | #F59E0B | rgba(245, 158, 11, 0.6) |
| 2-一般 | 🟢 绿色 | #22C55E | rgba(34, 197, 94, 0.6) |
| 1-低 | 🔵 蓝色 | #3B82F6 | rgba(59, 130, 246, 0.6) |

### 7.3 标记动画

```css
/* 脉动动画 */
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

.pulse-inner {
  animation: pulseInner 2s ease-out infinite;
}

.pulse-outer {
  animation: pulseOuter 2s ease-out infinite 0.5s;
}

/* 悬停加速 */
.event-marker:hover .pulse-inner,
.event-marker:hover .pulse-outer {
  animation-duration: 1s;
}
```

### 7.4 Tooltip

```
┌─────────────────────────────────┐
│ 美军航母进入南海                  │  ← 标题
│                                 │
│ 📍 南海海域 · 🕐 2小时前         │  ← 元信息
│                                 │
│ ┌──────────┐                    │
│ │  紧急    │                    │  ← 严重程度徽章
│ └──────────┘                    │
└─────────────────────────────────┘
         ▲
         │ 小三角
         │
      ● 事件标记
```

---

## 8. 动画规范

### 8.1 动画时长

| 类型 | 时长 | 使用场景 |
|------|------|----------|
| 极快 | 50ms | 点击反馈 |
| 快速 | 150ms | Tooltip、悬停 |
| 正常 | 200ms | 按钮状态 |
| 慢速 | 300ms | 抽屉展开 |
| 特慢 | 500ms | 进度条填充 |

### 8.2 缓动函数

```css
/* 标准缓动 */
--easing-default: cubic-bezier(0.4, 0, 0.2, 1);

/* 进入缓动 */
--easing-in: cubic-bezier(0.4, 0, 1, 1);

/* 退出缓动 */
--easing-out: cubic-bezier(0, 0, 0.2, 1);

/* 弹性缓动 */
--easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 8.3 动画类型

| 动画 | 时长 | 缓动 | 用途 |
|------|------|------|------|
| 抽屉展开 | 300ms | default | 右/左/底部抽屉 |
| 按钮悬停 | 200ms | default | 工具栏按钮 |
| 脉动 | 2000ms | ease-out | 事件标记 |
| 呼吸 | 3000ms | ease-in-out | 发光效果 |
| 流光 | 3000ms | linear | 按钮背景 |
| 淡入 | 150ms | ease | Tooltip |
| 滑入 | 200ms | default | 列表项 |

### 8.4 状态过渡

```css
/* 抽屉状态过渡 */
.drawer {
  transition:
    transform var(--duration-slow) var(--easing-default),
    opacity var(--duration-normal) var(--easing-default);
}

/* 按钮状态过渡 */
.btn {
  transition:
    background var(--duration-normal) var(--easing-default),
    border-color var(--duration-normal) var(--easing-default),
    box-shadow var(--duration-normal) var(--easing-default),
    transform var(--duration-fast) var(--easing-default);
}
```

---

## 9. 响应式设计

### 9.1 断点定义

| 断点 | 名称 | 宽度范围 | 布局变化 |
|------|------|----------|----------|
| xs | 手机 | <640px | 纯列表模式 |
| sm | 手机横屏 | 640-767px | 纯列表模式 |
| md | 平板竖屏 | 768-1023px | 2D地图 |
| lg | 平板横屏 | 1024-1279px | 简化3D |
| xl | 桌面 | 1280-1535px | 完整布局 |
| 2xl | 大屏 | 1536-1919px | 完整布局 |
| 3xl | 超大屏 | ≥1920px | 完整布局 |

### 9.2 响应式行为

```
超大屏 (≥1920px):
┌─────────────────────────────────────────────────────────────────┐
│                     ┌─────────────────────────┐                 │
│                     │                         │                 │
│    [抽屉]           │      3D 地球            │    [抽屉]       │
│    320px            │                         │    360px        │
│                     │                         │                 │
│                     └─────────────────────────┘                 │
│    [═══════════════════ 事件列表 ═══════════════════]          │
└─────────────────────────────────────────────────────────────────┘

平板 (768-1023px):
┌─────────────────────────────────────────────┐
│                                             │
│              2D 地图 (隐藏3D)                │
│                                             │
├─────────────────────────────────────────────┤
│ [═════════════ 事件列表 ═════════════]      │
├─────────────────────────────────────────────┤
│ [抽屉 - 全屏弹出]                            │
└─────────────────────────────────────────────┘

手机 (<640px):
┌───────────────────────┐
│                       │
│    事件列表           │
│    (主要视图)         │
│                       │
├───────────────────────┤
│ [抽屉 - 底部弹出]      │
├───────────────────────┤
│ [≡] [📊] [📋] [⋯]    │  ← 底部导航
└───────────────────────┘
```

### 9.3 响应式 CSS

```css
/* 超大屏 */
@media (min-width: 1920px) {
  .drawer-right { width: 360px; }
  .drawer-left { width: 320px; }
  .toolbar { left: 24px; bottom: 24px; }
}

/* 桌面 */
@media (max-width: 1535px) and (min-width: 1280px) {
  .drawer-right { width: 320px; }
  .drawer-left { width: 280px; }
}

/* 平板 */
@media (max-width: 1279px) {
  .globe-3d { display: none; }
  .globe-2d { display: block; }
  .toolbar-btn:not(.primary) { display: none; }
}

/* 手机 */
@media (max-width: 767px) {
  .globe-container { display: none; }

  .drawer-right,
  .drawer-left {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 80vh;
    transform: translateY(100%);
  }

  .toolbar { display: none; }
  .bottom-nav { display: flex; }
}
```

---

## 10. 可访问性规范

### 10.1 颜色对比度

| 文字类型 | 最小对比度 | 当前对比度 |
|----------|------------|------------|
| 主要文字 | 4.5:1 | 15.2:1 ✓ |
| 次要文字 | 4.5:1 | 5.1:1 ✓ |
| 辅助文字 | 3:1 | 3.5:1 ✓ |
| 禁用文字 | - | 2.4:1 (允许) |

### 10.2 焦点状态

```css
/* 焦点环 */
:focus-visible {
  outline: 2px solid var(--accent-cyan);
  outline-offset: 2px;
}

/* 按钮焦点 */
.btn:focus-visible {
  box-shadow:
    0 0 0 2px var(--bg-primary),
    0 0 0 4px var(--accent-cyan);
}
```

### 10.3 键盘导航

| 按键 | 功能 |
|------|------|
| Tab | 切换焦点 |
| Enter/Space | 激活按钮 |
| Esc | 关闭抽屉/弹窗 |
| Arrow Keys | 列表导航 |

### 10.4 动画减弱

```css
/* 尊重用户动画偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 附录: CSS 变量汇总

```css
:root {
  /* ===== Colors ===== */
  --bg-primary: #0A0E1A;
  --bg-secondary: #0F172A;
  --bg-tertiary: #1E293B;
  --bg-elevated: #1E293B;
  --bg-overlay: rgba(0, 0, 0, 0.4);

  --accent-cyan: #00E5FF;
  --accent-blue: #0077FF;
  --accent-purple: #8B5CF6;
  --accent-pink: #EC4899;

  --status-danger: #EF4444;
  --status-warning: #F59E0B;
  --status-success: #10B981;
  --status-info: #3B82F6;

  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-disabled: #475569;

  --border-default: #1E293B;
  --border-light: #334155;
  --border-accent: #00E5FF;

  /* ===== Typography ===== */
  --font-primary: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-chinese: 'PingFang SC', 'Microsoft YaHei', sans-serif;

  --text-xs: 10px;
  --text-sm: 12px;
  --text-base: 14px;
  --text-md: 16px;
  --text-lg: 20px;
  --text-xl: 24px;
  --text-2xl: 32px;
  --text-3xl: 48px;

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* ===== Spacing ===== */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* ===== Border Radius ===== */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 20px;
  --radius-full: 9999px;

  /* ===== Shadows ===== */
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.15);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.25);
  --shadow-glow-cyan: 0 0 20px rgba(0, 229, 255, 0.25);

  /* ===== Animation ===== */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);

  /* ===== Layout ===== */
  --drawer-width-sm: 280px;
  --drawer-width-md: 320px;
  --drawer-width-lg: 360px;
  --toolbar-btn-size: 48px;

  /* ===== Z-index ===== */
  --z-background: 0;
  --z-globe: 100;
  --z-marker: 400;
  --z-tooltip: 500;
  --z-toolbar: 600;
  --z-drawer-left: 700;
  --z-drawer-bottom: 800;
  --z-drawer-right: 900;
  --z-modal: 1000;
}
```

---

**文档完成** ✓

**版本历史:**
- v1.0 - 初始设计规范
- v2.0 - 添加动画细节
- v3.0 - 完整设计系统规范
