# EventPredictor UI 设计规范

> 版本: v2.1
> 日期: 2026-03-14
> 状态: 设计中

---

## 目录

1. [设计理念](#1-设计理念)
2. [整体布局](#2-整体布局)
3. [抽屉动画效果](#3-抽屉动画效果)
4. [悬浮工具栏](#4-悬浮工具栏)
5. [事件标记脉动](#5-事件标记脉动)
6. [颜色规范](#6-颜色规范)
7. [渐变与光效](#7-渐变与光效)
8. [字体规范](#8-字体规范)
9. [间距规范](#9-间距规范)
10. [响应式设计](#10-响应式设计)

---

## 1. 设计理念

### 1.1 核心原则

| 原则 | 描述 | 实现方式 |
|------|------|----------|
| **极简初始** | 打开时界面干净整洁 | 全屏地球 + 精简底部信息 |
| **按需展开** | 通过抽屉逐步显示内容 | 多级抽屉系统 |
| **层级叠加** | Z-index 层级管理 | 抽屉叠加显示 |
| **高大上风格** | 深色科技风 + 光效 | 渐变 + 发光动画 |
| **微动效** | 精细的交互反馈 | 200-300ms 过渡动画 |

### 1.2 层级架构 (Z-index)

```
┌─────────────────────────────────────────────┐
│  Z-1000  Toast / Modal 弹窗                 │ ← 最高层
├─────────────────────────────────────────────┤
│  Z-900   右侧抽屉 (分析结果)                 │
├─────────────────────────────────────────────┤
│  Z-800   底部抽屉 (事件列表)                 │
├─────────────────────────────────────────────┤
│  Z-700   左侧抽屉 (角色详情)                 │
├─────────────────────────────────────────────┤
│  Z-600   悬浮工具栏 / 按钮                   │
├─────────────────────────────────────────────┤
│  Z-500   事件 Tooltip                        │
├─────────────────────────────────────────────┤
│  Z-100   3D 地球                             │
├─────────────────────────────────────────────┤
│  Z-0     背景层                              │ ← 最低层
└─────────────────────────────────────────────┘
```

---

## 2. 整体布局

### 2.1 初始界面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                                                                             │
│                         🌍 全屏 3D 地球                                      │
│                                                                             │
│                      (事件标记脉动动画)                                       │
│                                                                             │
│                                                                             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [≡]                                    当前事件: xxx xxx    [⋯]            │
│ 悬浮工具栏                              (点击展开右侧抽屉)     更多菜单       │
│ (左下角固定)                                              (右下角固定)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 展开抽屉后

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ╔════════════╗                                              ╔══════════════╗│
│ ║            ║                                              ║              ║│
│ ║  左侧抽屉   ║              3D 地球 (压缩)                   ║   右侧抽屉    ║│
│ ║  (角色)    ║                                              ║   (分析)     ║│
│ ║            ║                                              ║              ║│
│ ╚════════════╝                                              ╚══════════════╝│
├─────────────────────────────────────────────────────────────────────────────┤
│  ▲ 事件列表 (5)                                                     [×]     │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                   │
│  │事件1│ │事件2│ │事件3│ │事件4│ │事件5│                                   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 尺寸规格

| 元素 | 宽度/高度 | 说明 |
|------|-----------|------|
| 左侧抽屉 | 320px | 可拖拽调整 |
| 右侧抽屉 | 360px | 可拖拽调整 |
| 底部抽屉 | 48px → 200px | 收起/展开 |
| 工具栏按钮 | 48x48px | 圆角 12px |
| 事件卡片 | 280x140px | 横向排列 |

---

## 3. 抽屉动画效果

### 3.1 右侧抽屉 (分析面板)

#### 视觉效果

```
关闭状态                    展开中 (300ms)                  展开完成

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│                  │    │          ╔═══════│    │          ╔═══════│
│                  │    │          ║       ║    │          ║       ║
│    3D Globe      │ →  │  Globe  ║ Slide ║ →  │  Globe  ║ Panel ║
│                  │    │ (压缩)  ║ In    ║    │  (60%)  ║       ║
│                  │    │          ║       ║    │          ║       ║
└──────────────────┘    └──────────────────┘    └──────────────────┘
     100%                  动画进行中               calc(100% - 360px)
```

#### CSS 代码

```css
/* 右侧抽屉容器 */
.drawer-right {
  position: fixed;
  top: 0;
  right: 0;
  width: 360px;
  height: 100%;
  z-index: 900;

  /* 初始状态：屏幕外 */
  transform: translateX(100%);

  /* 动画参数 */
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);
}

/* 展开状态 */
.drawer-right.open {
  transform: translateX(0);
}

/* 地球容器响应 */
.globe-container {
  width: 100%;
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

.globe-container.drawer-right-open {
  width: calc(100% - 360px);
}

/* 遮罩层 */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  opacity: 0;
  visibility: hidden;
  transition: opacity 200ms ease, visibility 200ms ease;
  z-index: 850;
}

.overlay.visible {
  opacity: 1;
  visibility: visible;
}
```

#### 动画时间线

```
时间轴 (毫秒)
├─────────┼─────────┼─────────┼─────────┤
0        75        150       225       300

事件:
├─ 遮罩淡入开始
│  opacity: 0 → 0.4
│
   ├─ 抽屉开始滑入
   │  translateX: 100% → 0
   │
          ├─ 地球开始压缩
          │  width: 100% → calc(100% - 360px)
          │
                           └─ 动画完成
                              触发 onOpen 回调
```

---

### 3.2 底部抽屉 (事件列表)

#### 视觉效果

```
收起状态 (48px)                     展开状态 (200px)

┌────────────────────────────────────┐    ┌────────────────────────────────────┐
│  ▼ 事件列表 (5)           [×]      │    │  ▲ 事件列表 (5)           [×]      │
└────────────────────────────────────┘    ├────────────────────────────────────┤
                                          │                                    │
                                          │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │
                                          │  │     │ │     │ │     │ │     │  │
                                          │  │事件1│ │事件2│ │事件3│ │事件4│  │
                                          │  │     │ │     │ │     │ │     │  │
                                          │  └─────┘ └─────┘ └─────┘ └─────┘  │
                                          │  ←────────── 横向滚动 ──────────→  │
                                          └────────────────────────────────────┘
```

#### CSS 代码

```css
/* 底部抽屉容器 */
.drawer-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 800;

  /* 动画参数 */
  transition: height 250ms cubic-bezier(0.4, 0, 0.2, 1);

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);
}

/* 展开状态 */
.drawer-bottom.open {
  height: 200px;
}

/* 内容区域 */
.drawer-bottom .content {
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 200ms ease 50ms,
    transform 200ms ease 50ms;
}

.drawer-bottom.open .content {
  opacity: 1;
  transform: translateY(0);
}

/* 标题栏 */
.drawer-bottom .header {
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 展开指示器 */
.drawer-bottom .expand-icon {
  transition: transform 200ms ease;
}

.drawer-bottom.open .expand-icon {
  transform: rotate(180deg);
}
```

#### 动画时间线

```
时间轴 (毫秒)
├─────────┼─────────┼─────────┼─────────┤
0        62.5     125       187.5      250

事件:
├─ 开始展开
│  height: 48px
│
   ├─ 内容开始淡入 (延迟50ms)
   │  opacity: 0 → 1
   │  translateY: 10px → 0
   │
          ├─ 高度继续增加
          │  height: ~124px
          │
                   └─ 动画完成
                      height: 200px
                      触发 onOpen 回调
```

---

### 3.3 左侧抽屉 (角色详情)

#### 视觉效果

```
关闭状态                    展开中 (280ms)                  展开完成

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│                  │    │╔══════           │    │╔══════           │
│                  │    │║       │         │    │║       │         │
│    3D Globe      │ →  │║ Slide │ Globe   │ →  │║ Panel │ Globe   │
│                  │    │║ In    │ (压缩)  │    │║       │ (60%)   │
│                  │    │║       │         │    │║       │         │
└──────────────────┘    └──────────────────┘    └──────────────────┘
     100%                  动画进行中               calc(100% - 320px)
```

#### CSS 代码

```css
/* 左侧抽屉容器 */
.drawer-left {
  position: fixed;
  top: 0;
  left: 0;
  width: 320px;
  height: 100%;
  z-index: 700;

  /* 初始状态：屏幕外 */
  transform: translateX(-100%);

  /* 动画参数 - 比右侧稍快 */
  transition: transform 280ms cubic-bezier(0.4, 0, 0.2, 1);

  /* 样式 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);
}

/* 展开状态 */
.drawer-left.open {
  transform: translateX(0);
}

/* 地球容器响应 */
.globe-container.drawer-left-open {
  width: calc(100% - 320px);
  margin-left: 320px;
}
```

---

### 3.4 多抽屉叠加

#### 同时展开多个抽屉

```css
/* Z-index 层级 */
.drawer-left   { z-index: 700; }
.drawer-bottom { z-index: 800; }
.drawer-right  { z-index: 900; }
.overlay       { z-index: 600; }

/* 地球容器响应多个抽屉 */
.globe-container.drawer-left-open.drawer-right-open {
  width: calc(100% - 320px - 360px);
  margin-left: 320px;
}

/* 底部抽屉在左右抽屉打开时调整宽度 */
.drawer-left.open ~ .drawer-bottom,
.drawer-right.open ~ .drawer-bottom {
  left: 320px;   /* 或根据实际状态 */
  right: 360px;
  width: calc(100% - 320px - 360px);
}
```

#### 抽屉展开优先级

| 操作 | 结果 |
|------|------|
| 点击事件标记 | 右侧抽屉展开 |
| 点击"事件列表"按钮 | 底部抽屉展开 |
| 点击"查看完整分析" | 左侧抽屉展开 |
| 多个同时展开 | 按层级叠加显示 |

---

## 4. 悬浮工具栏

### 4.1 布局结构

```
收起状态:                    展开状态 (动画依次出现):

┌───┐                        ┌───┐
│ ≡ │  ← 主菜单              │ ≡ │  ← 主菜单 (切换)
└───┘                        ├───┤
                             │ 📊 │  ← 分析面板 (0ms 延迟)
(左下角固定)                  ├───┤
 24px from left              │ 📋 │  ← 事件列表 (50ms 延迟)
 24px from bottom            ├───┤
                             │ 👥 │  ← 角色详情 (100ms 延迟)
                             ├───┤
                             │ 🌙 │  ← 主题切换 (150ms 延迟)
                             ├───┤
                             │ ⚙️ │  ← 设置 (200ms 延迟)
                             ├───┤
                             │ 🔄 │  ← 刷新 (250ms 延迟)
                             └───┘
```

### 4.2 按钮功能定义

| 按钮 | 图标 | 快捷键 | 功能 | 状态指示 |
|------|------|--------|------|----------|
| 主菜单 | ≡ | `Esc` | 展开/收起工具栏 | - |
| 分析面板 | 📊 | `A` | 切换右侧抽屉 | 抽屉打开时高亮 |
| 事件列表 | 📋 | `E` | 切换底部抽屉 | 抽屉打开时高亮 |
| 角色详情 | 👥 | `R` | 切换左侧抽屉 | 抽屉打开时高亮 |
| 主题切换 | 🌙/☀️ | `T` | 深色/浅色主题 | 图标变化 |
| 设置 | ⚙️ | `S` | 打开设置弹窗 | - |
| 刷新 | 🔄 | `F5` | 重新获取数据 | 刷新时旋转 |

### 4.3 CSS 样式

```css
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

/* 单个按钮 */
.toolbar-btn {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 41, 59, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 初始隐藏 */
  opacity: 0;
  transform: translateX(-20px) scale(0.8);

  /* 过渡动画 */
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* 主按钮始终可见 */
.toolbar-btn.primary {
  opacity: 1;
  transform: none;
}

/* 展开动画 - 依次出现 */
.toolbar.expanded .toolbar-btn:nth-child(1) { animation: slideIn 200ms 0ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(2) { animation: slideIn 200ms 50ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(3) { animation: slideIn 200ms 100ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(4) { animation: slideIn 200ms 150ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(5) { animation: slideIn 200ms 200ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(6) { animation: slideIn 200ms 250ms forwards; }
.toolbar.expanded .toolbar-btn:nth-child(7) { animation: slideIn 200ms 300ms forwards; }

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

/* 悬停状态 */
.toolbar-btn:hover {
  transform: translateY(-4px) scale(1.05);
  background: rgba(0, 229, 255, 0.15);
  border-color: rgba(0, 229, 255, 0.5);
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

/* 按钮图标 */
.toolbar-btn svg {
  width: 24px;
  height: 24px;
  color: #94A3B8;
  transition: color 200ms ease;
}

.toolbar-btn:hover svg {
  color: #00E5FF;
}

.toolbar-btn.active svg {
  color: #FFFFFF;
}

/* 点击反馈 */
.toolbar-btn:active {
  transform: translateY(-2px) scale(0.98);
}
```

### 4.4 刷新按钮特殊动画

```css
/* 刷新中状态 */
.toolbar-btn.refreshing svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

---

## 5. 事件标记脉动

### 5.1 标记结构

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

### 5.2 CSS 实现

```css
/* 事件标记容器 */
.event-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 100;
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

/* 内层脉动光晕 */
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

/* 外层脉动光晕 */
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

/* 内层脉动动画 */
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

/* 外层脉动动画 */
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
```

### 5.3 严重程度着色

```css
/* ===== 紧急 (severity: 5) - 红色 ===== */
.event-marker[data-severity="5"] .core {
  background: #EF4444;
  box-shadow: 0 0 16px #EF4444, 0 0 32px rgba(239, 68, 68, 0.5);
}
.event-marker[data-severity="5"] .pulse-inner,
.event-marker[data-severity="5"] .pulse-outer {
  border: 2px solid #EF4444;
  background: radial-gradient(circle, rgba(239, 68, 68, 0.3) 0%, transparent 70%);
}

/* ===== 高危 (severity: 4) - 橙色 ===== */
.event-marker[data-severity="4"] .core {
  background: #F97316;
  box-shadow: 0 0 14px #F97316, 0 0 28px rgba(249, 115, 22, 0.5);
}
.event-marker[data-severity="4"] .pulse-inner,
.event-marker[data-severity="4"] .pulse-outer {
  border: 2px solid #F97316;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.3) 0%, transparent 70%);
}

/* ===== 重要 (severity: 3) - 黄色 ===== */
.event-marker[data-severity="3"] .core {
  background: #F59E0B;
  box-shadow: 0 0 12px #F59E0B, 0 0 24px rgba(245, 158, 11, 0.5);
}
.event-marker[data-severity="3"] .pulse-inner,
.event-marker[data-severity="3"] .pulse-outer {
  border: 2px solid #F59E0B;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.3) 0%, transparent 70%);
}

/* ===== 一般 (severity: 2) - 绿色 ===== */
.event-marker[data-severity="2"] .core {
  background: #22C55E;
  box-shadow: 0 0 10px #22C55E, 0 0 20px rgba(34, 197, 94, 0.5);
}
.event-marker[data-severity="2"] .pulse-inner,
.event-marker[data-severity="2"] .pulse-outer {
  border: 2px solid #22C55E;
  background: radial-gradient(circle, rgba(34, 197, 94, 0.3) 0%, transparent 70%);
}

/* ===== 低 (severity: 1) - 蓝色 ===== */
.event-marker[data-severity="1"] .core {
  background: #3B82F6;
  box-shadow: 0 0 8px #3B82F6, 0 0 16px rgba(59, 130, 246, 0.5);
}
.event-marker[data-severity="1"] .pulse-inner,
.event-marker[data-severity="1"] .pulse-outer {
  border: 2px solid #3B82F6;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, transparent 70%);
}
```

### 5.4 交互状态

```css
/* 悬停效果 */
.event-marker:hover {
  z-index: 110;
}

.event-marker:hover .core {
  transform: translate(-50%, -50%) scale(1.5);
  transition: transform 200ms ease;
}

.event-marker:hover .pulse-inner,
.event-marker:hover .pulse-outer {
  animation-duration: 1s;  /* 加速脉动 */
}

/* 选中状态 */
.event-marker.selected {
  z-index: 120;
}

.event-marker.selected .core {
  transform: translate(-50%, -50%) scale(1.8);
  box-shadow:
    0 0 24px currentColor,
    0 0 48px currentColor,
    0 0 72px currentColor;
}

.event-marker.selected .pulse-inner,
.event-marker.selected .pulse-outer {
  animation-duration: 1.5s;
  border-width: 3px;
}
```

### 5.5 Tooltip 样式

```css
/* 事件 Tooltip */
.event-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 16px;
  padding: 12px 16px;
  min-width: 200px;
  max-width: 280px;

  /* 背景 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);

  /* 边框 */
  border: 1px solid rgba(30, 41, 59, 0.8);
  border-radius: 12px;

  /* 阴影 */
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(0, 229, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);

  /* 初始隐藏 */
  opacity: 0;
  visibility: hidden;
  transform: translateX(-50%) translateY(8px);
  transition: all 200ms ease;

  /* 文字 */
  color: var(--text-primary);
  font-size: 14px;
}

/* 显示 Tooltip */
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

/* Tooltip 内容 */
.event-tooltip .title {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
  margin-bottom: 8px;
}

.event-tooltip .meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94A3B8;
}

.event-tooltip .severity-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}
```

---

## 6. 颜色规范

### 6.1 色彩系统

```css
:root {
  /* ===== 背景色 ===== */
  --bg-primary: #0A0E1A;        /* 主背景 - 深空蓝黑 */
  --bg-secondary: #0F172A;      /* 次级背景 - 卡片背景 */
  --bg-tertiary: #1E293B;       /* 第三级背景 */
  --bg-elevated: #1E293B;       /* 抬起元素背景 */
  --bg-overlay: rgba(0, 0, 0, 0.4);  /* 遮罩背景 */

  /* ===== 主色 (Accent) ===== */
  --accent-cyan: #00E5FF;       /* 科技青 - 主强调色 */
  --accent-blue: #0077FF;       /* 科技蓝 - 次强调色 */
  --accent-purple: #8B5CF6;     /* 科技紫 - 特殊强调 */
  --accent-pink: #EC4899;       /* 科技粉 - 点缀色 */

  /* ===== 状态色 ===== */
  --status-danger: #EF4444;     /* 危险/紧急 - 红 */
  --status-warning: #F59E0B;    /* 警告/重要 - 黄 */
  --status-success: #10B981;    /* 成功/正常 - 绿 */
  --status-info: #3B82F6;       /* 信息 - 蓝 */

  /* ===== 文字色 ===== */
  --text-primary: #F8FAFC;      /* 主要文字 */
  --text-secondary: #94A3B8;    /* 次要文字 */
  --text-muted: #64748B;        /* 弱化文字 */
  --text-disabled: #475569;     /* 禁用文字 */

  /* ===== 边框色 ===== */
  --border-default: #1E293B;    /* 默认边框 */
  --border-light: #334155;      /* 浅色边框 */
  --border-accent: #00E5FF;     /* 强调边框 */
}
```

### 6.2 透明色扩展

```css
:root {
  /* 黑色透明 */
  --black-5: rgba(0, 0, 0, 0.05);
  --black-10: rgba(0, 0, 0, 0.1);
  --black-20: rgba(0, 0, 0, 0.2);
  --black-40: rgba(0, 0, 0, 0.4);
  --black-60: rgba(0, 0, 0, 0.6);

  /* 白色透明 */
  --white-5: rgba(255, 255, 255, 0.05);
  --white-10: rgba(255, 255, 255, 0.1);
  --white-20: rgba(255, 255, 255, 0.2);
  --white-30: rgba(255, 255, 255, 0.3);

  /* 青色透明 */
  --cyan-5: rgba(0, 229, 255, 0.05);
  --cyan-10: rgba(0, 229, 255, 0.1);
  --cyan-20: rgba(0, 229, 255, 0.2);
  --cyan-30: rgba(0, 229, 255, 0.3);
  --cyan-40: rgba(0, 229, 255, 0.4);
  --cyan-50: rgba(0, 229, 255, 0.5);

  /* 蓝色透明 */
  --blue-10: rgba(0, 119, 255, 0.1);
  --blue-20: rgba(0, 119, 255, 0.2);
  --blue-30: rgba(0, 119, 255, 0.3);
}
```

### 6.3 颜色使用场景

| 场景 | 颜色变量 | 用途 |
|------|----------|------|
| 页面背景 | `--bg-primary` | 主背景 |
| 卡片背景 | `--bg-secondary` | 面板、卡片 |
| 悬浮元素 | `--bg-elevated` | 抽屉、弹窗 |
| 主按钮 | `--accent-cyan` | 主要操作 |
| 链接/强调 | `--accent-blue` | 文字链接 |
| 紧急状态 | `--status-danger` | severity=5 |
| 警告状态 | `--status-warning` | severity=3-4 |
| 正常状态 | `--status-success` | severity=1-2 |
| 主要文字 | `--text-primary` | 标题、正文 |
| 次要文字 | `--text-secondary` | 描述、标签 |
| 弱化文字 | `--text-muted` | 辅助信息 |

---

## 7. 渐变与光效

### 7.1 渐变规范

```css
/* ===== 主渐变 ===== */

/* 青蓝渐变 - 主按钮、标题 */
.gradient-primary {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
}

/* 蓝紫渐变 - 特殊强调 */
.gradient-accent {
  background: linear-gradient(135deg, #0077FF 0%, #8B5CF6 100%);
}

/* 青紫渐变 - 悬停效果 */
.gradient-hover {
  background: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%);
}

/* ===== 背景渐变 ===== */

/* 深色背景渐变 */
.gradient-bg-dark {
  background: linear-gradient(180deg, #0A0E1A 0%, #0F172A 100%);
}

/* 卡片背景渐变 */
.gradient-bg-card {
  background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
}

/* ===== 趋势渐变 ===== */

/* 上涨 - 绿色系 */
.gradient-up {
  background: linear-gradient(90deg, #10B981 0%, #22C55E 100%);
}

/* 下跌 - 红色系 */
.gradient-down {
  background: linear-gradient(90deg, #EF4444 0%, #F97316 100%);
}

/* 平稳 - 黄色系 */
.gradient-neutral {
  background: linear-gradient(90deg, #F59E0B 0%, #EAB308 100%);
}

/* ===== 边框渐变 ===== */
.gradient-border {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--bg-secondary), var(--bg-secondary)) padding-box,
    linear-gradient(135deg, rgba(0, 229, 255, 0.3) 0%, rgba(0, 119, 255, 0.3) 100%) border-box;
}

/* ===== 文字渐变 ===== */
.gradient-text {
  background: linear-gradient(90deg, #00E5FF 0%, #0077FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### 7.2 光效规范

```css
/* ===== 发光效果 ===== */

/* 青色发光 - 主要 */
.glow-cyan {
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.25);
}

.glow-cyan-strong {
  box-shadow:
    0 0 20px rgba(0, 229, 255, 0.25),
    0 0 40px rgba(0, 229, 255, 0.15),
    0 0 60px rgba(0, 229, 255, 0.1);
}

/* 蓝色发光 */
.glow-blue {
  box-shadow: 0 0 20px rgba(0, 119, 255, 0.25);
}

/* 紫色发光 */
.glow-purple {
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.25);
}

/* 危险发光 - 红色 */
.glow-danger {
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
}

/* 成功发光 - 绿色 */
.glow-success {
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

/* 警告发光 - 黄色 */
.glow-warning {
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
}

/* ===== 边框发光 ===== */
.glow-border-cyan {
  box-shadow:
    inset 0 0 0 1px rgba(0, 229, 255, 0.3),
    0 0 12px rgba(0, 229, 255, 0.15);
}

/* ===== 内发光 ===== */
.glow-inner {
  box-shadow: inset 0 0 40px rgba(0, 229, 255, 0.05);
}

/* ===== 文字发光 ===== */
.text-glow-cyan {
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.text-glow-white {
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}
```

### 7.3 光效动画

```css
/* ===== 呼吸发光动画 ===== */
@keyframes breathe {
  0%, 100% {
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
  }
  50% {
    box-shadow: 0 0 40px rgba(0, 229, 255, 0.4);
  }
}

.breathe-glow {
  animation: breathe 3s ease-in-out infinite;
}

/* ===== 流光效果 ===== */
@keyframes flowing {
  0% {
    background-position: 200% center;
  }
  100% {
    background-position: -200% center;
  }
}

.flowing-light {
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 229, 255, 0.4) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: flowing 3s linear infinite;
}

/* ===== 扫光效果 ===== */
@keyframes scan {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.scan-light {
  position: relative;
  overflow: hidden;
}

.scan-light::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 229, 255, 0.1) 50%,
    transparent 100%
  );
  animation: scan 4s ease-in-out infinite;
  pointer-events: none;
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
  background: radial-gradient(
    circle,
    rgba(0, 229, 255, 0.15) 0%,
    rgba(0, 229, 255, 0) 70%
  );
  pointer-events: none;
  z-index: -1;
}
```

### 7.4 毛玻璃效果

```css
/* 标准毛玻璃 */
.glass {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* 浅色毛玻璃 */
.glass-light {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* 深色毛玻璃 (抽屉用) */
.glass-dark {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
```

---

## 8. 字体规范

### 8.1 字体家族

```css
:root {
  /* 主要字体 - 英文/数字 */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* 等宽字体 - 数字/代码 */
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', Consolas, monospace;

  /* 中文显示字体 */
  --font-chinese: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;

  /* 标题字体 */
  --font-display: 'Inter', 'PingFang SC', sans-serif;

  /* 全局字体回退 */
  --font-system: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
                 'Apple Color Emoji', 'Segoe UI Emoji';
}

/* 字体引用 */
body {
  font-family: var(--font-primary), var(--font-chinese);
}

/* 数字使用等宽字体 */
.mono, .number {
  font-family: var(--font-mono);
}
```

### 8.2 字体大小

```css
:root {
  /* 大小级别 */
  --text-xs: 10px;      /* 极小 - 标签、辅助 */
  --text-sm: 12px;      /* 小号 - 次要信息 */
  --text-base: 14px;    /* 基础 - 正文 */
  --text-md: 16px;      /* 中号 - 小标题 */
  --text-lg: 20px;      /* 大号 - 标题 */
  --text-xl: 24px;      /* 超大 - 主标题 */
  --text-2xl: 32px;     /* 巨大 - 数字展示 */
  --text-3xl: 48px;     /* 特大 - 关键数据 */
  --text-4xl: 64px;     /* 超特大 - 大屏数字 */
}
```

### 8.3 字重

```css
:root {
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

### 8.4 行高

```css
:root {
  --leading-none: 1;        /* 无行高 */
  --leading-tight: 1.25;    /* 紧凑 */
  --leading-snug: 1.375;    /* 较紧凑 */
  --leading-normal: 1.5;    /* 正常 */
  --leading-relaxed: 1.625; /* 宽松 */
  --leading-loose: 2;       /* 很宽松 */
}
```

### 8.5 字间距

```css
:root {
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}
```

### 8.6 字体样式预设

```css
/* ===== 标题层级 ===== */

/* H1 - 页面主标题 */
.text-h1 {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
  color: var(--text-primary);
}

/* H2 - 区块标题 */
.text-h2 {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
}

/* H3 - 卡片标题 */
.text-h3 {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
  color: var(--text-primary);
}

/* H4 - 小标题 */
.text-h4 {
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  color: var(--text-primary);
}

/* ===== 正文层级 ===== */

/* 正文 - 主要 */
.text-body {
  font-family: var(--font-primary);
  font-size: var(--text-base);
  font-weight: var(--font-normal);
  line-height: var(--leading-relaxed);
  color: var(--text-primary);
}

/* 正文 - 次要 */
.text-body-secondary {
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-normal);
  line-height: var(--leading-normal);
  color: var(--text-secondary);
}

/* 标签文字 */
.text-label {
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  color: var(--text-muted);
}

/* ===== 数字展示 ===== */

/* 大数字 */
.text-number-lg {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-none);
  letter-spacing: var(--tracking-tighter);
}

/* 数据数字 */
.text-number-md {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-none);
}

/* 小数字 */
.text-number-sm {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  line-height: var(--leading-tight);
}

/* 百分比 */
.text-percentage {
  font-family: var(--font-mono);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
}
```

---

## 9. 间距规范

### 9.1 间距单位 (4px 基准)

```css
:root {
  --space-0: 0;
  --space-px: 1px;
  --space-0-5: 2px;    /* 2px */
  --space-1: 4px;      /* 4px - 极小间距 */
  --space-2: 8px;      /* 8px - 小间距 */
  --space-3: 12px;     /* 12px - 中小间距 */
  --space-4: 16px;     /* 16px - 基础间距 */
  --space-5: 20px;     /* 20px - 中等间距 */
  --space-6: 24px;     /* 24px - 常用间距 */
  --space-8: 32px;     /* 32px - 大间距 */
  --space-10: 40px;    /* 40px - 较大间距 */
  --space-12: 48px;    /* 48px - 大区块间距 */
  --space-16: 64px;    /* 64px - 超大间距 */
  --space-20: 80px;    /* 80px - 区块间距 */
  --space-24: 96px;    /* 96px - 页面级间距 */
}
```

### 9.2 组件内边距

```css
/* 紧凑型 */
.p-compact {
  padding: var(--space-2) var(--space-3);
}

/* 默认型 */
.p-default {
  padding: var(--space-4);
}

/* 宽松型 */
.p-relaxed {
  padding: var(--space-6);
}

/* 卡片内边距 */
.p-card {
  padding: var(--space-5);
}

/* 面板内边距 */
.p-panel {
  padding: var(--space-6);
}

/* 按钮内边距 */
.p-btn-sm {
  padding: var(--space-1) var(--space-3);
}

.p-btn-md {
  padding: var(--space-2) var(--space-4);
}

.p-btn-lg {
  padding: var(--space-3) var(--space-6);
}
```

### 9.3 元素间距 (Gap)

```css
.gap-xs { gap: var(--space-1); }    /* 4px */
.gap-sm { gap: var(--space-2); }    /* 8px */
.gap-md { gap: var(--space-3); }    /* 12px */
.gap-lg { gap: var(--space-4); }    /* 16px */
.gap-xl { gap: var(--space-6); }    /* 24px */
.gap-2xl { gap: var(--space-8); }   /* 32px */
```

### 9.4 圆角规范

```css
:root {
  --radius-none: 0;
  --radius-sm: 4px;      /* 小圆角 - 标签、小按钮 */
  --radius-md: 8px;      /* 中圆角 - 按钮、输入框 */
  --radius-lg: 12px;     /* 大圆角 - 卡片、面板 */
  --radius-xl: 16px;     /* 超大圆角 - 抽屉头部 */
  --radius-2xl: 20px;    /* 特大圆角 - 大面板 */
  --radius-full: 9999px; /* 全圆 - 药丸形、圆形 */
}

/* 使用示例 */
.rounded-sm { border-radius: var(--radius-sm); }
.rounded-md { border-radius: var(--radius-md); }
.rounded-lg { border-radius: var(--radius-lg); }
.rounded-xl { border-radius: var(--radius-xl); }
.rounded-full { border-radius: var(--radius-full); }
```

### 9.5 布局尺寸

```css
:root {
  /* ===== 抽屉尺寸 ===== */
  --drawer-width-sm: 280px;
  --drawer-width-md: 320px;
  --drawer-width-lg: 360px;
  --drawer-width-xl: 420px;

  --drawer-height-sm: 120px;
  --drawer-height-md: 200px;
  --drawer-height-lg: 320px;

  /* ===== 工具栏尺寸 ===== */
  --toolbar-btn-size: 48px;
  --toolbar-gap: 12px;

  /* ===== 事件卡片尺寸 ===== */
  --event-card-width: 280px;
  --event-card-height: 140px;
  --event-card-gap: 16px;

  /* ===== 头部/底部高度 ===== */
  --header-height: 68px;
  --footer-height: 40px;
  --bottom-bar-height: 48px;

  /* ===== 事件标记尺寸 ===== */
  --marker-core-size: 12px;
  --marker-pulse-inner: 24px;
  --marker-pulse-outer: 40px;
}
```

---

## 10. 响应式设计

### 10.1 断点定义

```css
:root {
  --breakpoint-sm: 640px;   /* 手机横屏 */
  --breakpoint-md: 768px;   /* 平板竖屏 */
  --breakpoint-lg: 1024px;  /* 平板横屏 */
  --breakpoint-xl: 1280px;  /* 桌面 */
  --breakpoint-2xl: 1536px; /* 大屏 */
  --breakpoint-3xl: 1920px; /* 超大屏 */
}

/* 媒体查询 */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
@media (min-width: 1920px) { /* 3xl */ }
```

### 10.2 响应式行为

| 断点 | 宽度范围 | 地球 | 抽屉 | 工具栏 |
|------|----------|------|------|--------|
| 超大屏 | ≥1920px | 全屏 + 抽屉自适应 | 全尺寸 | 全部展开 |
| 大屏 | 1536-1919px | 全屏 + 抽屉自适应 | 全尺寸 | 全部展开 |
| 桌面 | 1280-1535px | 压缩 | 中等宽度 | 折叠部分 |
| 平板横屏 | 1024-1279px | 隐藏3D，显示2D | 全屏 | 仅主按钮 |
| 平板竖屏 | 768-1023px | 隐藏3D，显示2D | 全屏 | 仅主按钮 |
| 手机 | <768px | 纯列表模式 | 全屏 | 底部固定栏 |

### 10.3 响应式 CSS

```css
/* 超大屏 (≥1920px) */
@media (min-width: 1920px) {
  .drawer-right { width: var(--drawer-width-lg); }  /* 360px */
  .drawer-left { width: var(--drawer-width-md); }   /* 320px */
}

/* 桌面 (1280-1535px) */
@media (max-width: 1535px) and (min-width: 1280px) {
  .drawer-right { width: var(--drawer-width-md); }  /* 320px */
  .drawer-left { width: var(--drawer-width-sm); }   /* 280px */
}

/* 平板 (768-1279px) */
@media (max-width: 1279px) {
  /* 隐藏3D地球，显示2D地图 */
  .globe-3d { display: none; }
  .globe-2d { display: block; }

  /* 抽屉全屏 */
  .drawer-right,
  .drawer-left {
    width: 100%;
    max-width: 480px;
  }

  /* 工具栏简化 */
  .toolbar-btn:not(.primary) { display: none; }
}

/* 手机 (<768px) */
@media (max-width: 767px) {
  /* 纯列表模式 */
  .globe-container { display: none; }

  /* 抽屉改为底部弹出 */
  .drawer-right,
  .drawer-left {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    top: auto;
    height: 80vh;
    width: 100%;
    transform: translateY(100%);
  }

  .drawer-right.open,
  .drawer-left.open {
    transform: translateY(0);
  }

  /* 底部固定导航栏 */
  .bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-default);
  }

  /* 隐藏桌面工具栏 */
  .toolbar { display: none; }
}
```

---

## 附录: CSS 变量完整清单

```css
/* ============================================
   EventPredictor UI Design System
   Version: 2.1
   ============================================ */

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
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
  --font-chinese: 'PingFang SC', 'Microsoft YaHei', sans-serif;

  --text-xs: 10px;
  --text-sm: 12px;
  --text-base: 14px;
  --text-md: 16px;
  --text-lg: 20px;
  --text-xl: 24px;
  --text-2xl: 32px;
  --text-3xl: 48px;

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

  /* ===== Layout ===== */
  --drawer-width-sm: 280px;
  --drawer-width-md: 320px;
  --drawer-width-lg: 360px;
  --toolbar-btn-size: 48px;
  --event-card-width: 280px;
  --event-card-height: 140px;

  /* ===== Z-index ===== */
  --z-background: 0;
  --z-globe: 100;
  --z-tooltip: 500;
  --z-toolbar: 600;
  --z-drawer-left: 700;
  --z-drawer-bottom: 800;
  --z-drawer-right: 900;
  --z-modal: 1000;

  /* ===== Animation ===== */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

**文档完成** ✓

下一步建议：
1. 将 CSS 变量集成到项目中
2. 创建抽屉组件
3. 实现工具栏交互
4. 添加事件标记脉动效果
