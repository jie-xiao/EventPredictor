# EventPredictor UI 动画与交互实现规范

> 版本: v2.2
> 日期: 2026-03-14
> 状态: 细化实现规范

---

## 1. 抽屉动画效果 - 详细实现

### 1.1 状态机设计

```
状态流转图:

                    ┌──────────────┐
                    │   CLOSED     │
                    │  (关闭状态)   │
                    └──────┬───────┘
                           │
                    open() │ 点击触发
                           ▼
                    ┌──────────────┐
              ┌────▶│  OPENING     │◀────┐
              │     │  (展开中)    │     │
              │     └──────┬───────┘     │
              │            │             │
              │     300ms  │ 完成        │
              │            ▼             │
              │     ┌──────────────┐     │
              │     │    OPEN      │     │
              │     │  (展开完成)   │     │
              │     └──────┬───────┘     │
              │            │             │
              │    close() │ 点击触发    │
              │            ▼             │
              │     ┌──────────────┐     │
              └─────│   CLOSING    │─────┘
              重置   │  (收起中)    │  取消
                    └──────────────┘
```

### 1.2 TypeScript 状态定义

```typescript
// 抽屉状态类型
type DrawerState = 'CLOSED' | 'OPENING' | 'OPEN' | 'CLOSING';

// 抽屉位置类型
type DrawerPosition = 'left' | 'right' | 'bottom';

// 抽屉配置接口
interface DrawerConfig {
  position: DrawerPosition;
  width?: number;           // left/right 抽屉宽度
  height?: number;          // bottom 抽屉高度
  openDuration: number;     // 展开动画时长 (ms)
  closeDuration: number;    // 收起动画时长 (ms)
  easing: string;           // 缓动函数
  overlay: boolean;         // 是否显示遮罩
  pushContent: boolean;     // 是否推动主内容
}

// 默认配置
const DRAWER_CONFIGS: Record<DrawerPosition, DrawerConfig> = {
  left: {
    position: 'left',
    width: 320,
    openDuration: 280,
    closeDuration: 240,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    overlay: true,
    pushContent: true,
  },
  right: {
    position: 'right',
    width: 360,
    openDuration: 300,
    closeDuration: 250,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    overlay: true,
    pushContent: true,
  },
  bottom: {
    position: 'bottom',
    height: 200,
    openDuration: 250,
    closeDuration: 200,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    overlay: false,
    pushContent: false,
  },
};
```

### 1.3 右侧抽屉详细动画时间线

```
右侧抽屉展开时间线 (300ms):

时间轴 (ms)
├────────┼────────┼────────┼────────┼────────┤
0       60       120      180      240      300

遮罩层 (Overlay):
├─ 0ms:   opacity: 0, visibility: hidden
├─ 50ms:  opacity: 0.4 (淡入完成 50%)
└─ 200ms: opacity: 0.4 (完全显示)

抽屉面板 (Panel):
├─ 0ms:   transform: translateX(100%)
├─ 60ms:  transform: translateX(75%)
├─ 120ms: transform: translateX(50%)
├─ 180ms: transform: translateX(25%)
├─ 240ms: transform: translateX(10%)
└─ 300ms: transform: translateX(0)

地球容器 (Globe):
├─ 0ms:   width: 100%
├─ 50ms:  width: calc(100% - 90px)   [延迟开始]
├─ 150ms: width: calc(100% - 180px)
└─ 300ms: width: calc(100% - 360px)

内容淡入 (Content):
├─ 0ms:   opacity: 0
├─ 150ms: opacity: 0 [等待]
└─ 300ms: opacity: 1 [完成后淡入]
```

### 1.4 CSS 动画关键帧 - 右侧抽屉

```css
/* 右侧抽屉展开动画 */
@keyframes drawerRightOpen {
  0% {
    transform: translateX(100%);
    opacity: 0.9;
  }
  20% {
    opacity: 1;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 右侧抽屉收起动画 */
@keyframes drawerRightClose {
  0% {
    transform: translateX(0);
    opacity: 1;
  }
  100% {
    transform: translateX(100%);
    opacity: 0.9;
  }
}

/* 遮罩淡入 */
@keyframes overlayFadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 0.4;
  }
}

/* 遮罩淡出 */
@keyframes overlayFadeOut {
  0% {
    opacity: 0.4;
  }
  100% {
    opacity: 0;
  }
}

/* 地球容器压缩 */
@keyframes globeShrink {
  0% {
    width: 100%;
  }
  100% {
    width: calc(100% - 360px);
  }
}

/* 地球容器恢复 */
@keyframes globeExpand {
  0% {
    width: calc(100% - 360px);
  }
  100% {
    width: 100%;
  }
}
```

### 1.5 底部抽屉详细动画

```
底部抽屉展开时间线 (250ms):

时间轴 (ms)
├────────┼────────┼────────┼────────┼────────┤
0       50       100      150      200      250

高度变化:
├─ 0ms:   height: 48px (仅标题栏)
├─ 50ms:  height: 80px
├─ 100ms: height: 120px
├─ 150ms: height: 160px
├─ 200ms: height: 185px
└─ 250ms: height: 200px

内容淡入 (延迟50ms开始):
├─ 0ms:   opacity: 0, transform: translateY(10px)
├─ 50ms:  opacity: 0, transform: translateY(10px) [开始]
├─ 150ms: opacity: 0.6, transform: translateY(4px)
└─ 250ms: opacity: 1, transform: translateY(0)

图标旋转:
├─ 0ms:   transform: rotate(0deg)
└─ 200ms: transform: rotate(180deg)
```

### 1.6 抽屉动画 CSS 类

```css
/* ===== 基础抽屉样式 ===== */
.drawer {
  position: fixed;
  z-index: var(--z-drawer);

  /* 动画配置 */
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;

  /* 毛玻璃效果 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

/* ===== 右侧抽屉 ===== */
.drawer-right {
  top: 0;
  right: 0;
  width: 360px;
  height: 100%;
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);
}

/* 关闭状态 */
.drawer-right.closed {
  transform: translateX(100%);
  pointer-events: none;
}

/* 展开中 */
.drawer-right.opening {
  animation: drawerRightOpen 300ms forwards;
}

/* 展开完成 */
.drawer-right.open {
  transform: translateX(0);
  pointer-events: auto;
}

/* 收起中 */
.drawer-right.closing {
  animation: drawerRightClose 250ms forwards;
}

/* ===== 左侧抽屉 ===== */
.drawer-left {
  top: 0;
  left: 0;
  width: 320px;
  height: 100%;
  border-right: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);
}

.drawer-left.closed {
  transform: translateX(-100%);
  pointer-events: none;
}

.drawer-left.opening {
  animation: drawerLeftOpen 280ms forwards;
}

.drawer-left.open {
  transform: translateX(0);
  pointer-events: auto;
}

.drawer-left.closing {
  animation: drawerLeftClose 240ms forwards;
}

@keyframes drawerLeftOpen {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(0); }
}

@keyframes drawerLeftClose {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

/* ===== 底部抽屉 ===== */
.drawer-bottom {
  left: 0;
  right: 0;
  bottom: 0;
  height: 48px;
  border-top: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.2);
}

.drawer-bottom.closed {
  height: 48px;
}

.drawer-bottom.opening {
  animation: drawerBottomOpen 250ms forwards;
}

.drawer-bottom.open {
  height: 200px;
}

.drawer-bottom.closing {
  animation: drawerBottomClose 200ms forwards;
}

@keyframes drawerBottomOpen {
  0% { height: 48px; }
  100% { height: 200px; }
}

@keyframes drawerBottomClose {
  0% { height: 200px; }
  100% { height: 48px; }
}

/* ===== 内容淡入 ===== */
.drawer-content {
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 200ms ease 50ms,
    transform 200ms ease 50ms;
}

.drawer.open .drawer-content {
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
  z-index: calc(var(--z-drawer) - 1);
  transition:
    opacity 200ms ease,
    visibility 200ms ease;
}

.drawer-overlay.visible {
  opacity: 1;
  visibility: visible;
}

/* 点击遮罩关闭 */
.drawer-overlay.visible:hover {
  cursor: pointer;
}
```

### 1.7 多抽屉协调

```typescript
// 抽屉协调器
class DrawerCoordinator {
  private openDrawers: Set<DrawerPosition> = new Set();
  private globeElement: HTMLElement | null = null;

  // 打开抽屉
  open(position: DrawerPosition) {
    this.openDrawers.add(position);
    this.updateGlobeSize();
  }

  // 关闭抽屉
  close(position: DrawerPosition) {
    this.openDrawers.delete(position);
    this.updateGlobeSize();
  }

  // 更新地球容器大小
  private updateGlobeSize() {
    if (!this.globeElement) return;

    let shrinkLeft = 0;
    let shrinkRight = 0;

    if (this.openDrawers.has('left')) {
      shrinkLeft = DRAWER_CONFIGS.left.width!;
    }
    if (this.openDrawers.has('right')) {
      shrinkRight = DRAWER_CONFIGS.right.width!;
    }

    this.globeElement.style.width =
      `calc(100% - ${shrinkLeft}px - ${shrinkRight}px)`;
    this.globeElement.style.marginLeft = `${shrinkLeft}px`;
  }
}
```

---

## 2. 悬浮工具栏 - 详细实现

### 2.1 工具栏状态机

```
状态流转图:

┌───────────────┐
│   COLLAPSED   │  收起状态，仅显示主按钮
└───────┬───────┘
        │
 click  │ toggle()
        ▼
┌───────────────┐
│   EXPANDING   │  展开中，按钮依次出现
└───────┬───────┘
        │
 300ms  │ animation complete
        ▼
┌───────────────┐
│   EXPANDED    │  展开完成，显示所有按钮
└───────┬───────┘
        │
 click  │ toggle() / click outside
        ▼
┌───────────────┐
│   COLLAPSING  │  收起中，按钮依次消失
└───────┬───────┘
        │
 300ms  │ animation complete
        ▼
┌───────────────┐
│   COLLAPSED   │
└───────────────┘
```

### 2.2 按钮配置接口

```typescript
// 工具栏按钮配置
interface ToolbarButton {
  id: string;
  icon: React.ComponentType;   // 图标组件
  label: string;               // 悬停提示
  shortcut?: string;           // 快捷键
  action: () => void;          // 点击回调
  active?: () => boolean;      // 是否激活状态
  disabled?: () => boolean;    // 是否禁用
  dividerAfter?: boolean;      // 后面加分隔线
}

// 工具栏配置
const TOOLBAR_BUTTONS: ToolbarButton[] = [
  {
    id: 'menu',
    icon: MenuIcon,
    label: '菜单',
    shortcut: 'Esc',
    action: () => toolbar.toggle(),
  },
  {
    id: 'analysis',
    icon: BarChartIcon,
    label: '分析面板',
    shortcut: 'A',
    action: () => drawers.right.toggle(),
    active: () => drawers.right.isOpen,
    dividerAfter: true,
  },
  {
    id: 'events',
    icon: ListIcon,
    label: '事件列表',
    shortcut: 'E',
    action: () => drawers.bottom.toggle(),
    active: () => drawers.bottom.isOpen,
  },
  {
    id: 'roles',
    icon: UsersIcon,
    label: '角色分析',
    shortcut: 'R',
    action: () => drawers.left.toggle(),
    active: () => drawers.left.isOpen,
    dividerAfter: true,
  },
  {
    id: 'theme',
    icon: () => theme.isDark ? MoonIcon : SunIcon,
    label: '切换主题',
    shortcut: 'T',
    action: () => theme.toggle(),
  },
  {
    id: 'settings',
    icon: SettingsIcon,
    label: '设置',
    shortcut: 'S',
    action: () => modals.settings.open(),
  },
  {
    id: 'refresh',
    icon: RefreshIcon,
    label: '刷新数据',
    shortcut: 'F5',
    action: () => data.refresh(),
  },
];
```

### 2.3 按钮展开动画详细时间线

```
展开动画时间线 (总计 350ms):

按钮1 (菜单): 0ms 延迟
├─ 0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
├─ 50ms:  opacity: 0.5, transform: translateX(-10px) scale(0.9)
└─ 200ms: opacity: 1, transform: translateX(0) scale(1)

按钮2 (分析): 50ms 延迟
├─ 0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
├─ 100ms: opacity: 0.5, transform: translateX(-10px) scale(0.9)
└─ 250ms: opacity: 1, transform: translateX(0) scale(1)

按钮3 (事件): 100ms 延迟
├─ 0ms:   opacity: 0, transform: translateX(-20px) scale(0.8)
├─ 150ms: opacity: 0.5, transform: translateX(-10px) scale(0.9)
└─ 300ms: opacity: 1, transform: translateX(0) scale(1)

按钮4 (角色): 150ms 延迟
... 以此类推

按钮5 (主题): 200ms 延迟
按钮6 (设置): 250ms 延迟
按钮7 (刷新): 300ms 延迟
```

### 2.4 按钮状态样式

```css
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
  border: 1px solid transparent;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  /* 动画初始状态 */
  opacity: 0;
  transform: translateX(-20px) scale(0.8);

  /* 过渡配置 */
  transition:
    opacity 200ms cubic-bezier(0.4, 0, 0.2, 1),
    transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
    background 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease;
}

/* ===== 主按钮 - 始终可见 ===== */
.toolbar-btn.primary {
  opacity: 1;
  transform: none;
  border-color: rgba(30, 41, 59, 0.8);
}

/* ===== 展开状态 ===== */
.toolbar.expanded .toolbar-btn {
  opacity: 1;
  transform: translateX(0) scale(1);
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
  background: rgba(0, 229, 255, 0.15);
  border-color: rgba(0, 229, 255, 0.5);
  box-shadow:
    0 8px 32px rgba(0, 229, 255, 0.2),
    0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* 悬停时图标颜色 */
.toolbar-btn:hover:not(.disabled) svg {
  color: var(--accent-cyan);
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

/* ===== 刷新按钮特殊动画 ===== */
.toolbar-btn.refreshing svg {
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

  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(30, 41, 59, 0.8);

  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;

  opacity: 0;
  visibility: hidden;
  transition: opacity 150ms ease, visibility 150ms ease;

  pointer-events: none;
}

.toolbar-btn:hover::after {
  opacity: 1;
  visibility: visible;
}

/* ===== 分隔线 ===== */
.toolbar-divider {
  width: 32px;
  height: 1px;
  margin: 4px auto;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(30, 41, 59, 0.8) 50%,
    transparent 100%
  );
}
```

### 2.5 快捷键处理

```typescript
// 快捷键映射
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

// 键盘事件处理
document.addEventListener('keydown', (e) => {
  // 如果焦点在输入框，忽略快捷键
  if (isInputFocused()) return;

  const buttonId = SHORTCUT_MAP[e.key];
  if (buttonId) {
    e.preventDefault();
    const button = TOOLBAR_BUTTONS.find(b => b.id === buttonId);
    if (button && !button.disabled?.()) {
      button.action();
    }
  }
});
```

---

## 3. 事件标记脉动 - 详细实现

### 3.1 标记组件结构

```tsx
// 事件标记组件
interface EventMarkerProps {
  event: Event;
  isSelected: boolean;
  onSelect: (event: Event) => void;
}

const EventMarker: React.FC<EventMarkerProps> = ({
  event,
  isSelected,
  onSelect
}) => {
  return (
    <div
      className={cn(
        'event-marker',
        `severity-${event.severity}`,
        { selected: isSelected }
      )}
      style={{
        left: `${event.location.lon}%`,
        top: `${event.location.lat}%`,
      }}
      onClick={() => onSelect(event)}
      data-severity={event.severity}
    >
      {/* 核心点 */}
      <div className="core" />

      {/* 内层脉动 */}
      <div className="pulse-inner" />

      {/* 外层脉动 */}
      <div className="pulse-outer" />

      {/* Tooltip */}
      <div className="event-tooltip">
        <div className="title">{event.title}</div>
        <div className="meta">
          <span className="location">{event.location.region}</span>
          <span className="time">{formatTime(event.timestamp)}</span>
        </div>
        <div className={cn('severity-badge', `severity-${event.severity}`)}>
          {getSeverityLabel(event.severity)}
        </div>
      </div>
    </div>
  );
};
```

### 3.2 脉动动画详细参数

```
脉动动画参数:

内层光晕 (pulse-inner):
┌────────────────────────────────────────────────────────────┐
│  周期: 2000ms (2秒)                                        │
│  缓动: ease-out                                            │
│  初始: scale(1), opacity: 0.8                              │
│  结束: scale(2.5), opacity: 0                              │
│  延迟: 0ms                                                 │
└────────────────────────────────────────────────────────────┘

外层光晕 (pulse-outer):
┌────────────────────────────────────────────────────────────┐
│  周期: 2000ms (2秒)                                        │
│  缓动: ease-out                                            │
│  初始: scale(1), opacity: 0.6                              │
│  结束: scale(2.5), opacity: 0                              │
│  延迟: 500ms (错峰，与内层形成波纹效果)                      │
└────────────────────────────────────────────────────────────┘

时间轴效果:
0ms      500ms    1000ms   1500ms   2000ms   2500ms
|---------|---------|---------|---------|---------|
[内层开始]          [内层完成]          [内层循环]
     [外层开始]          [外层完成]          [外层循环]
```

### 3.3 完整 CSS 实现

```css
/* ===== 事件标记容器 ===== */
.event-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: var(--z-marker);
  transition: z-index 0s;
}

.event-marker:hover {
  z-index: calc(var(--z-marker) + 10);
}

.event-marker.selected {
  z-index: calc(var(--z-marker) + 20);
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

/* ===== 脉动光晕基础样式 ===== */
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

/* ===== 悬停加速脉动 ===== */
.event-marker:hover .pulse-inner {
  animation-duration: 1s;
}

.event-marker:hover .pulse-outer {
  animation-duration: 1s;
  animation-delay: 0.25s;
}

/* ===== 选中状态 ===== */
.event-marker.selected .core {
  transform: translate(-50%, -50%) scale(1.5);
}

.event-marker.selected .pulse-inner {
  animation-duration: 1.5s;
  border-width: 3px;
}

.event-marker.selected .pulse-outer {
  animation-duration: 1.5s;
  animation-delay: 0.375s;
  border-width: 3px;
}
```

### 3.4 严重程度样式变体

```css
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
```

### 3.5 Tooltip 样式

```css
/* ===== Tooltip 容器 ===== */
.event-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(8px);
  margin-bottom: 16px;

  min-width: 200px;
  max-width: 280px;
  padding: 12px 16px;

  /* 背景 */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

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
  transition:
    opacity 150ms ease,
    visibility 150ms ease,
    transform 150ms ease;

  pointer-events: none;
}

/* 显示 Tooltip */
.event-marker:hover .event-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

/* 小三角 */
.event-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(15, 23, 42, 0.95);
}

/* ===== Tooltip 内容 ===== */
.event-tooltip .title {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
  margin-bottom: 8px;
  line-height: 1.4;
}

.event-tooltip .meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #94A3B8;
  margin-bottom: 8px;
}

.event-tooltip .location::before {
  content: '📍';
  margin-right: 4px;
}

.event-tooltip .time::before {
  content: '🕐';
  margin-right: 4px;
}

/* ===== 严重程度徽章 ===== */
.event-tooltip .severity-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.severity-badge[data-severity="5"] {
  background: rgba(239, 68, 68, 0.2);
  color: #EF4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.severity-badge[data-severity="4"] {
  background: rgba(249, 115, 22, 0.2);
  color: #F97316;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.severity-badge[data-severity="3"] {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.severity-badge[data-severity="2"] {
  background: rgba(34, 197, 94, 0.2);
  color: #22C55E;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.severity-badge[data-severity="1"] {
  background: rgba(59, 130, 246, 0.2);
  color: #3B82F6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
```

---

## 4. 颜色规范 - 使用场景详解

### 4.1 颜色使用场景速查表

| 场景 | 变量 | 值 | 示例 |
|------|------|-----|------|
| **背景** |
| 页面主背景 | `--bg-primary` | #0A0E1A | `<body>` |
| 卡片/面板背景 | `--bg-secondary` | #0F172A | 抽屉内部 |
| 抬起元素 | `--bg-tertiary` | #1E293B | 弹窗、下拉菜单 |
| 遮罩层 | `--bg-overlay` | rgba(0,0,0,0.4) | 抽屉背景 |
| **主色** |
| 主按钮 | `--accent-cyan` | #00E5FF | 确认按钮 |
| 链接/强调 | `--accent-blue` | #0077FF | 文字链接 |
| 特殊强调 | `--accent-purple` | #8B5CF6 | VIP标识 |
| **状态色** |
| 紧急/错误 | `--status-danger` | #EF4444 | severity=5 |
| 警告 | `--status-warning` | #F59E0B | severity=3-4 |
| 成功/正常 | `--status-success` | #10B981 | severity=1-2 |
| 信息 | `--status-info` | #3B82F6 | 提示信息 |
| **文字** |
| 标题/正文 | `--text-primary` | #F8FAFC | 主要内容 |
| 描述/标签 | `--text-secondary` | #94A3B8 | 次要信息 |
| 辅助信息 | `--text-muted` | #64748B | 时间戳 |
| **边框** |
| 默认边框 | `--border-default` | #1E293B | 分割线 |
| 强调边框 | `--border-light` | #334155 | 悬停边框 |

### 4.2 组件颜色规范

```css
/* ===== 按钮颜色 ===== */

/* 主按钮 */
.btn-primary {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  color: #FFFFFF;
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
  box-shadow: 0 0 24px rgba(0, 229, 255, 0.4);
}

/* 次要按钮 */
.btn-secondary {
  background: rgba(0, 229, 255, 0.1);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 229, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: rgba(0, 229, 255, 0.5);
}

/* 危险按钮 */
.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* 禁用按钮 */
.btn-disabled {
  background: rgba(30, 41, 59, 0.5);
  color: var(--text-disabled);
  cursor: not-allowed;
}

/* ===== 输入框颜色 ===== */
.input-default {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}

.input-default:focus {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.2);
}

.input-error {
  border-color: var(--status-danger);
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
}

/* ===== 卡片颜色 ===== */
.card-default {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-default);
}

.card-hover:hover {
  border-color: var(--border-light);
  background: rgba(15, 23, 42, 0.8);
}

.card-selected {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* ===== 标签颜色 ===== */
.tag-default {
  background: rgba(0, 229, 255, 0.1);
  color: var(--accent-cyan);
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.tag-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--status-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.tag-warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--status-warning);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.tag-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--status-danger);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* ===== 进度条颜色 ===== */
.progress-track {
  background: rgba(30, 41, 59, 0.8);
}

.progress-bar-low {
  /* < 50% */
  background: linear-gradient(90deg, var(--status-danger), var(--status-warning));
}

.progress-bar-medium {
  /* 50% - 75% */
  background: linear-gradient(90deg, var(--status-warning), #EAB308);
}

.progress-bar-high {
  /* > 75% */
  background: linear-gradient(90deg, var(--status-success), var(--accent-cyan));
}
```

### 4.3 渐变使用场景

```css
/* ===== 标题渐变 ===== */
.heading-gradient {
  background: linear-gradient(90deg, #00E5FF 0%, #0077FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ===== 按钮渐变 ===== */
.btn-gradient-primary {
  background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
}

.btn-gradient-hover {
  background: linear-gradient(135deg, #00E5FF 0%, #8B5CF6 100%);
}

/* ===== 背景渐变 ===== */
.bg-gradient-page {
  background: radial-gradient(
    ellipse at 50% 0%,
    rgba(0, 229, 255, 0.05) 0%,
    transparent 50%
  ),
  linear-gradient(180deg, #0A0E1A 0%, #0F172A 100%);
}

.bg-gradient-card {
  background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
}

/* ===== 边框渐变 ===== */
.border-gradient {
  border: 1px solid transparent;
  background:
    linear-gradient(var(--bg-secondary), var(--bg-secondary)) padding-box,
    linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 119, 255, 0.3)) border-box;
}

/* ===== 趋势渐变 ===== */
.trend-up {
  background: linear-gradient(90deg, #10B981 0%, #22C55E 50%, #10B981 100%);
  background-size: 200% 100%;
}

.trend-down {
  background: linear-gradient(90deg, #EF4444 0%, #F97316 50%, #EF4444 100%);
  background-size: 200% 100%;
}

.trend-neutral {
  background: linear-gradient(90deg, #F59E0B 0%, #EAB308 50%, #F59E0B 100%);
  background-size: 200% 100%;
}
```

### 4.4 透明色使用

```css
/* ===== 悬停背景 ===== */
.hover-bg {
  background: transparent;
  transition: background 150ms ease;
}

.hover-bg:hover {
  background: rgba(0, 229, 255, 0.1);
}

/* ===== 选中背景 ===== */
.selected-bg {
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.3);
}

/* ===== 禁用状态 ===== */
.disabled-bg {
  background: rgba(30, 41, 59, 0.5);
  opacity: 0.6;
}

/* ===== 遮罩层 ===== */
.overlay-light {
  background: rgba(0, 0, 0, 0.3);
}

.overlay-medium {
  background: rgba(0, 0, 0, 0.5);
}

.overlay-dark {
  background: rgba(0, 0, 0, 0.7);
}
```

---

## 5. 字体间距 - 组件级样式

### 5.1 组件字体规范

```css
/* ===== Header 组件 ===== */
.header-title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.025em;
}

.header-subtitle {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ===== 卡片标题 ===== */
.card-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.375;
}

.card-description {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
}

/* ===== 事件卡片 ===== */
.event-card-title {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  max-lines: 2;
}

.event-card-meta {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
  color: var(--text-secondary);
}

.event-card-time {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
}

/* ===== 数据展示 ===== */
.data-value-lg {
  /* 大数字 - 置信度等 */
  font-family: var(--font-mono);
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.05em;
}

.data-value-md {
  /* 中等数字 */
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.025em;
}

.data-value-sm {
  /* 小数字 */
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: 500;
  line-height: 1.25;
}

.data-label {
  /* 数据标签 */
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ===== 角色名称 ===== */
.role-name {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.role-category {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ===== 时间线 ===== */
.timeline-time {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
}

.timeline-event {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
}

.timeline-probability {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
}

/* ===== 标签 ===== */
.tag-text {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.25;
}

.tag-text-sm {
  font-family: var(--font-primary);
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ===== 按钮 ===== */
.btn-text {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.25;
}

.btn-text-sm {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.25;
}

/* ===== Tooltip ===== */
.tooltip-title {
  font-family: var(--font-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}

.tooltip-text {
  font-family: var(--font-primary);
  font-size: 12px;
  font-weight: 400;
  line-height: 1.5;
}
```

### 5.2 组件间距规范

```css
/* ===== Header 间距 ===== */
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

/* ===== 卡片间距 ===== */
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

/* ===== 事件卡片间距 ===== */
.event-card {
  width: 280px;
  height: 140px;
  padding: 16px;
  border-radius: 12px;
  margin-right: 16px;
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
  padding: 0 24px;
  margin-bottom: 0;
}

.drawer-body {
  padding: 24px;
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
```

### 5.3 圆角使用规范

```css
/* ===== 容器圆角 ===== */
.container-radius-none { border-radius: 0; }
.container-radius-sm { border-radius: 8px; }
.container-radius-md { border-radius: 12px; }
.container-radius-lg { border-radius: 16px; }
.container-radius-xl { border-radius: 20px; }

/* ===== 按钮圆角 ===== */
.btn-radius-sm { border-radius: 6px; }
.btn-radius-md { border-radius: 8px; }
.btn-radius-lg { border-radius: 10px; }
.btn-radius-full { border-radius: 9999px; }

/* ===== 标签圆角 ===== */
.tag-radius-sm { border-radius: 4px; }
.tag-radius-md { border-radius: 6px; }
.tag-radius-full { border-radius: 9999px; }

/* ===== 输入框圆角 ===== */
.input-radius-sm { border-radius: 6px; }
.input-radius-md { border-radius: 8px; }
.input-radius-lg { border-radius: 10px; }

/* ===== 图片/头像圆角 ===== */
.avatar-radius-sm { border-radius: 50%; }
.avatar-radius-md { border-radius: 8px; }
.avatar-radius-lg { border-radius: 12px; }
```

---

## 附录: Tailwind 配置扩展

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // 背景
        'bg-primary': '#0A0E1A',
        'bg-secondary': '#0F172A',
        'bg-tertiary': '#1E293B',

        // 主色
        'accent-cyan': '#00E5FF',
        'accent-blue': '#0077FF',
        'accent-purple': '#8B5CF6',

        // 状态
        'status-danger': '#EF4444',
        'status-warning': '#F59E0B',
        'status-success': '#10B981',
        'status-info': '#3B82F6',

        // 文字
        'text-primary': '#F8FAFC',
        'text-secondary': '#94A3B8',
        'text-muted': '#64748B',
      },

      fontFamily: {
        'primary': ['Inter', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
        'chinese': ['PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },

      fontSize: {
        'xs': ['10px', { lineHeight: '1' }],
        'sm': ['12px', { lineHeight: '1.5' }],
        'base': ['14px', { lineHeight: '1.5' }],
        'md': ['16px', { lineHeight: '1.375' }],
        'lg': ['20px', { lineHeight: '1.25' }],
        'xl': ['24px', { lineHeight: '1.25' }],
        '2xl': ['32px', { lineHeight: '1' }],
        '3xl': ['48px', { lineHeight: '1' }],
      },

      spacing: {
        '0.5': '2px',
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
      },

      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '20px',
      },

      boxShadow: {
        'glow-cyan': '0 0 20px rgba(0, 229, 255, 0.25)',
        'glow-cyan-strong': '0 0 20px rgba(0, 229, 255, 0.25), 0 0 40px rgba(0, 229, 255, 0.15)',
        'glow-danger': '0 0 20px rgba(239, 68, 68, 0.3)',
        'glow-success': '0 0 20px rgba(16, 185, 129, 0.3)',
      },

      animation: {
        'pulse-inner': 'pulseInner 2s ease-out infinite',
        'pulse-outer': 'pulseOuter 2s ease-out infinite 0.5s',
        'breathe': 'breathe 3s ease-in-out infinite',
        'flowing': 'flowing 3s linear infinite',
      },

      keyframes: {
        pulseInner: {
          '0%': { transform: 'translate(-50%, -50%) scale(1)', opacity: '0.8' },
          '100%': { transform: 'translate(-50%, -50%) scale(2.5)', opacity: '0' },
        },
        pulseOuter: {
          '0%': { transform: 'translate(-50%, -50%) scale(1)', opacity: '0.6' },
          '100%': { transform: 'translate(-50%, -50%) scale(2.5)', opacity: '0' },
        },
        breathe: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 229, 255, 0.2)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 229, 255, 0.4)' },
        },
        flowing: {
          '0%': { backgroundPosition: '200% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
      },

      zIndex: {
        'background': '0',
        'globe': '100',
        'tooltip': '500',
        'toolbar': '600',
        'drawer-left': '700',
        'drawer-bottom': '800',
        'drawer-right': '900',
        'modal': '1000',
      },
    },
  },
};
```

---

**文档完成** ✓

文件已保存至: `E:\EventPredictor\docs\ui-animation-implementation.md`
