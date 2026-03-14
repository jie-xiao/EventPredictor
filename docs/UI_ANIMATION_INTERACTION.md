# EventPredictor UI 动画与交互详细规范

> **版本**: v3.5 | **日期**: 2026-03-14 | **用途**: 前端开发精确参考

---

## 1. 抽屉动画效果

### 1.1 动画系统总览

```
抽屉动画三要素:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ① 面板移动          ② 内容淡入          ③ 背景响应        │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐        │
│  │transform│        │ opacity │        │  width  │        │
│  │translate│        │  delay  │        │ margin  │        │
│  │ 300ms   │        │ 150ms   │        │ 300ms   │        │
│  └─────────┘        └─────────┘        └─────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 1.2 右侧抽屉 - 分析面板 (360px)

#### 完整结构

```
┌────────────────────────────────────┐
│ ◀ 趋势预测                   [×]  │ ← Header (56px)
│   ┌──────────────────────────────┐│
│   │ 返回事件列表                 ││ ← Breadcrumb (可选)
│   └──────────────────────────────┘│
├────────────────────────────────────┤
│                                    │
│  ┌────────────┐     ┌─────────┐   │
│  │     ↑      │     │   75%   │   │ ← 趋势 + 置信度环
│  │    上涨    │     │   ○     │   │
│  │  [图标]    │     │ [圆环]  │   │
│  └────────────┘     └─────────┘   │
│                                    │
│  ████████████████████░░░░░░░░      │ ← 置信度进度条
│  置信度: 75%                       │
│                                    │
├────────────────────────────────────┤
│                                    │
│  📌 关键洞察                       │ ← Section 1
│  ┌──────────────────────────────┐ │
│  │ ✓ 美方可能增派舰艇进入南海    │ │
│  │ ✓ 中方或将加强巡航力度        │ │
│  │ ✓ 地区紧张局势可能升级        │ │
│  └──────────────────────────────┘ │
│                                    │
├────────────────────────────────────┤
│                                    │
│  ⚠️ 风险评估                       │ ← Section 2
│  ┌────────────┐ ┌────────────┐    │
│  │ 风险等级   │ │ 冲突数量   │    │
│  │    高      │ │     3      │    │
│  │   🔴      │ │   🟠       │    │
│  └────────────┘ └────────────┘    │
│                                    │
├────────────────────────────────────┤
│                                    │
│  ⏱ 时间线预测                      │ ← Section 3
│  ●────────○────────○               │
│  │ 24h    │ 72h    │ 7d           │
│  ▼        ▼        ▼               │
│  舰艇集结  外交磋商  局势稳定       │
│  (85%)    (60%)    (45%)           │
│                                    │
├────────────────────────────────────┤
│                                    │
│  📋 共识分析                       │ ← Section 4
│  ┌─────┐ ┌─────┐ ┌─────┐         │
│  │外交 │ │区域 │ │和平 │         │
│  │磋商 │ │稳定 │ │解决 │         │
│  └─────┘ └─────┘ └─────┘         │
│                                    │
├────────────────────────────────────┤
│                                    │
│  [     查看完整分析报告 →     ]    │ ← Footer (80px)
│                                    │
└────────────────────────────────────┘
          宽度: 360px
```

#### 毫秒级动画时间线

```
右侧抽屉展开动画 (总时长: 300ms)

时间轴:
0ms      50ms     100ms    150ms    200ms    250ms    300ms
|---------|---------|---------|---------|---------|---------|

【抽屉面板 translateX】
100%─────85%─────65%─────45%─────25%─────10%──────0%
          │                              │
          └─ 开始加速                     └─ 减速到达

【抽屉透明度 opacity】
0.9──────────────────────────────────────────────1

【遮罩层 opacity】
0─────────────────────────────────────────────0.4
│                                                │
└─ 延迟0ms开始                                   └─ 同步完成

【地球容器 width】
100%─────────────────────────────────────calc(100%-360px)
          │                              │
          └─ 延迟50ms开始                 └─ 同步完成

【内容区 opacity】
0─────────────────────(等待)──────────────1
          │                     │         │
          └─ 延迟150ms开始       │         └─ 350ms完成
                               │
【内容区 translateY】           └─ 开始淡入
10px─────────────────────────────────────0

【Section 依次出现】
Section1: 300ms 开始, 150ms 动画
Section2: 350ms 开始, 150ms 动画
Section3: 400ms 开始, 150ms 动画
Section4: 450ms 开始, 150ms 动画
Footer:   500ms 开始, 150ms 动画
```

#### 缓动曲线详解

```css
/* 主缓动函数: cubic-bezier(0.4, 0, 0.2, 1)
   也称为 "standard easing" 或 "ease-out" */

/* 曲线特征:
   - 开始: 快速启动
   - 中间: 匀速运动
   - 结束: 平滑减速
   - 适合: UI 元素入场动画
*/

/* 关键点:
   0%:  速度 = 1.0 (快速开始)
   25%: 速度 = 0.9
   50%: 速度 = 0.7
   75%: 速度 = 0.4 (开始减速)
   100%: 速度 = 0   (平滑停止)
*/

/* CSS 变量 */
--easing-standard: cubic-bezier(0.4, 0, 0.2, 1);
--easing-decelerate: cubic-bezier(0, 0, 0.2, 1);
--easing-accelerate: cubic-bezier(0.4, 0, 1, 1);
```

#### 完整 CSS 代码

```css
/* ================================================
   右侧抽屉 - 分析面板
   ================================================ */

.drawer-right {
  /* ===== 定位 ===== */
  position: fixed;
  top: 0;
  right: 0;
  width: 360px;
  height: 100vh;
  z-index: 900;

  /* ===== 初始状态 ===== */
  transform: translateX(100%);
  opacity: 0.9;
  visibility: hidden;
  pointer-events: none;

  /* ===== 样式 ===== */
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-left: 1px solid rgba(30, 41, 59, 0.8);
  box-shadow:
    -8px 0 32px rgba(0, 0, 0, 0.3),
    -4px 0 16px rgba(0, 0, 0, 0.2);

  /* ===== 过渡动画 ===== */
  transition:
    transform 300ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 200ms ease,
    visibility 0ms linear 300ms;

  /* ===== 性能优化 ===== */
  will-change: transform, opacity;
  contain: layout style;
  overscroll-behavior: contain;
}

/* ===== 展开状态 ===== */
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

/* ===== 收起状态 (反向) ===== */
.drawer-right:not(.open) {
  transition:
    transform 250ms cubic-bezier(0.4, 0, 0.2, 1),
    opacity 150ms ease,
    visibility 0ms linear 250ms;
}

/* ================================================
   Header
   ================================================ */
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

.drawer-right .drawer-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-right .drawer-back {
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

.drawer-right .drawer-back:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #F8FAFC;
  transform: translateX(-2px);
}

.drawer-right .drawer-title {
  font-size: 16px;
  font-weight: 600;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 8px;
}

.drawer-right .drawer-title svg {
  width: 20px;
  height: 20px;
  color: #00E5FF;
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
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

/* ================================================
   Content
   ================================================ */
.drawer-right .drawer-content {
  flex: 1;
  padding: 20px;
  height: calc(100vh - 56px - 80px);
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
  transition: background 150ms ease;
}

.drawer-right .drawer-content::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}

/* ================================================
   Section 动画
   ================================================ */
.drawer-section {
  margin-bottom: 24px;
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 150ms ease,
    transform 150ms ease;
}

.drawer-right.open .drawer-section {
  opacity: 1;
  transform: translateY(0);
}

.drawer-right.open .drawer-section:nth-child(1) { transition-delay: 300ms; }
.drawer-right.open .drawer-section:nth-child(2) { transition-delay: 350ms; }
.drawer-right.open .drawer-section:nth-child(3) { transition-delay: 400ms; }
.drawer-right.open .drawer-section:nth-child(4) { transition-delay: 450ms; }

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

.drawer-section-title svg {
  width: 16px;
  height: 16px;
}

/* ================================================
   Footer
   ================================================ */
.drawer-right .drawer-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  flex-shrink: 0;

  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(30, 41, 59, 0.6);

  /* 动画 */
  opacity: 0;
  transform: translateY(10px);
  transition:
    opacity 150ms ease 500ms,
    transform 150ms ease 500ms;
}

.drawer-right.open .drawer-footer {
  opacity: 1;
  transform: translateY(0);
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
  box-shadow:
    0 8px 24px rgba(0, 229, 255, 0.3),
    0 0 0 1px rgba(0, 229, 255, 0.2);
}

.drawer-right .drawer-footer button:active {
  transform: translateY(0);
}
```

---

### 1.3 左侧抽屉 - 角色详情 (320px)

#### 完整结构

```
┌────────────────────────────────┐
│ [×]                      16角色│ ← Header (56px)
├────────────────────────────────┤
│ 🔍 搜索角色...                 │ ← Search (48px)
├────────────────────────────────┤
│ [全部][政府][企业][民众][媒体] │ ← Tabs (40px)
├────────────────────────────────┤
│                                │
│ ┌────────────────────────────┐│
│ │ 🇨🇳 中国政府               ││
│ │ ───────────────────────── ││
│ │ 立场: 维护主权领土完整     ││ ← Role Card
│ │ 行动: 加强南海巡航力度     ││
│ │ 置信度: ████████░░ 82%    ││
│ └────────────────────────────┘│
│                                │
│ ┌────────────────────────────┐│
│ │ 🇺🇸 美国政府               ││
│ │ ───────────────────────── ││
│ │ 立场: 维护航行自由         ││ ← Role Card
│ │ 行动: 继续派遣舰艇         ││
│ │ 置信度: ███████░░░ 78%    ││
│ └────────────────────────────┘│
│                                │
│ ┌────────────────────────────┐│
│ │ 🇪🇺 欧盟                   ││
│ │ ───────────────────────── ││
│ │ 立场: 呼吁和平解决         ││ ← Role Card
│ │ 行动: 外交斡旋             ││
│ │ 置信度: ██████░░░░ 72%    ││
│ └────────────────────────────┘│
│                                │
│ ... 更多角色 (可滚动)          │
│                                │
│ ┌────────────────────────────┐│
│ │ 🏢 科技巨头                ││
│ │ 📰 主流媒体                ││
│ │ 👤 普通民众                ││
│ │ ...                        ││
│ └────────────────────────────┘│
│                                │
└────────────────────────────────┘
          宽度: 320px
```

#### 毫秒级动画时间线

```
左侧抽屉展开动画 (总时长: 280ms)

时间轴:
0ms      56ms     112ms    168ms    224ms    280ms
|---------|---------|---------|---------|---------|

【抽屉面板 translateX】
-100%────-75%────-50%────-25%────-10%─────0%

【地球容器】
width: 100% → calc(100%-320px)
margin-left: 0 → 320px
(延迟40ms开始)

【Search 淡入】
opacity: 0 → 1 (延迟140ms, 150ms动画)

【Tabs 淡入】
opacity: 0 → 1 (延迟160ms, 150ms动画)

【Content 淡入】
opacity: 0, translateY(10px) → opacity: 1, translateY(0)
(延迟180ms开始)

【角色卡片依次出现】
卡片1: 280ms 延迟, 150ms 动画 → 430ms 完成
卡片2: 330ms 延迟, 150ms 动画 → 480ms 完成
卡片3: 380ms 延迟, 150ms 动画 → 530ms 完成
卡片4: 430ms 延迟, 150ms 动画 → 580ms 完成
卡片5: 480ms 延迟, 150ms 动画 → 630ms 完成
...
每个卡片间隔 50ms
```

#### 完整 CSS 代码

```css
/* ================================================
   左侧抽屉 - 角色详情
   ================================================ */

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

/* ================================================
   Header
   ================================================ */
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
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ================================================
   Search
   ================================================ */
.drawer-left .drawer-search {
  padding: 12px 20px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);

  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 150ms ease 140ms, transform 150ms ease 140ms;
}

.drawer-left.open .drawer-search {
  opacity: 1;
  transform: translateY(0);
}

.drawer-left .search-wrapper {
  position: relative;
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
  box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
}

.drawer-left .search-input::placeholder {
  color: #64748B;
}

.drawer-left .search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748B;
}

/* ================================================
   Tabs
   ================================================ */
.drawer-left .drawer-tabs {
  padding: 12px 20px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  overflow-x: auto;

  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 150ms ease 160ms, transform 150ms ease 160ms;
}

.drawer-left.open .drawer-tabs {
  opacity: 1;
  transform: translateY(0);
}

.drawer-left .drawer-tabs::-webkit-scrollbar {
  display: none;
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

/* ================================================
   Content
   ================================================ */
.drawer-left .drawer-content {
  flex: 1;
  padding: 16px;
  height: calc(100vh - 144px);
  overflow-y: auto;

  opacity: 0;
  transform: translateY(10px);
  transition: opacity 180ms ease 180ms, transform 180ms ease 180ms;
}

.drawer-left.open .drawer-content {
  opacity: 1;
  transform: translateY(0);
}

/* ================================================
   Role Card
   ================================================ */
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
  transition:
    opacity 150ms ease,
    transform 150ms ease,
    background 150ms ease,
    border-color 150ms ease,
    box-shadow 150ms ease;
}

/* 卡片依次延迟 */
.drawer-left.open .role-card:nth-child(1) { transition-delay: 280ms; }
.drawer-left.open .role-card:nth-child(2) { transition-delay: 330ms; }
.drawer-left.open .role-card:nth-child(3) { transition-delay: 380ms; }
.drawer-left.open .role-card:nth-child(4) { transition-delay: 430ms; }
.drawer-left.open .role-card:nth-child(5) { transition-delay: 480ms; }
.drawer-left.open .role-card:nth-child(6) { transition-delay: 530ms; }
.drawer-left.open .role-card:nth-child(7) { transition-delay: 580ms; }
.drawer-left.open .role-card:nth-child(8) { transition-delay: 630ms; }

.role-card:hover {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(51, 65, 85, 0.8);
  transform: translateX(4px);
}

.role-card.selected {
  border-color: rgba(0, 229, 255, 0.5);
  background: rgba(0, 229, 255, 0.05);
  box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.2);
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.role-card-icon {
  font-size: 20px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-card-info {
  flex: 1;
}

.role-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #F8FAFC;
  margin-bottom: 2px;
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
  margin-bottom: 10px;
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

### 1.4 底部抽屉 - 事件列表 (48px → 200px)

#### 完整结构

```
收起状态 (48px):
┌────────────────────────────────────────────────────────────────┐
│  ▼ 事件列表 (5)   🔴2 紧急 · 🟡1 重要 · 🟢2 一般      [×]    │
└────────────────────────────────────────────────────────────────┘

展开状态 (200px):
┌────────────────────────────────────────────────────────────────┐
│  ▲ 事件列表 (5)   🔴2 紧急 · 🟡1 重要 · 🟢2 一般      [×]    │ ← Header
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐│
│  │ 🔴 紧急  │ │ 🔴 紧急  │ │ 🟡 重要  │ │ 🟢 一般  │ │ 🟢   ││
│  │          │ │          │ │          │ │          │ │      ││
│  │ 美军航母 │ │ 美联储   │ │ 中美贸易 │ │ 气候峰会 │ │科技  ││
│  │ 进入南海 │ │ 利率决议 │ │ 谈判     │ │          │ │合作  ││
│  │          │ │          │ │          │ │          │ │      ││
│  │ 📍 南海  │ │ 📍 美国  │ │ 📍 北京  │ │ 📍 日内瓦│ │📍... ││
│  │ 🕐 2h前  │ │ 🕐 5h前  │ │ 🕐 1d前  │ │ 🕐 2d前  │ │🕐... ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────┘│
│                                                                │
│  ←──────────────────── 横向滚动 ────────────────────→        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

#### 毫秒级动画时间线

```
底部抽屉展开动画 (总时长: 250ms)

时间轴:
0ms      50ms     100ms    150ms    200ms    250ms
|---------|---------|---------|---------|---------|

【抽屉高度】
48px─────80px─────120px────160px─────185px────200px

【展开图标旋转】
0deg──────────────────────────────────────180deg
(200ms内完成)

【内容淡入】
opacity: 0, translateY(10px) → opacity: 1, translateY(0)
(延迟50ms开始)

【事件卡片依次出现】
卡片1: 100ms 延迟, 150ms 动画
卡片2: 130ms 延迟, 150ms 动画
卡片3: 160ms 延迟, 150ms 动画
卡片4: 190ms 延迟, 150ms 动画
卡片5: 220ms 延迟, 150ms 动画
每个卡片间隔 30ms
```

#### 完整 CSS 代码

```css
/* ================================================
   底部抽屉 - 事件列表
   ================================================ */

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

/* ================================================
   Header
   ================================================ */
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
  margin-left: 4px;
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

/* ================================================
   Content
   ================================================ */
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

/* ================================================
   Event Card
   ================================================ */
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
  transition:
    opacity 150ms ease,
    transform 150ms ease,
    background 150ms ease,
    border-color 150ms ease,
    transform 150ms ease,
    box-shadow 150ms ease;
}

/* 卡片依次延迟 */
.drawer-bottom.open .event-card:nth-child(1) { transition-delay: 100ms; }
.drawer-bottom.open .event-card:nth-child(2) { transition-delay: 130ms; }
.drawer-bottom.open .event-card:nth-child(3) { transition-delay: 160ms; }
.drawer-bottom.open .event-card:nth-child(4) { transition-delay: 190ms; }
.drawer-bottom.open .event-card:nth-child(5) { transition-delay: 220ms; }

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
  letter-spacing: 0.05em;
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

.event-card-severity.severity-1 {
  background: rgba(59, 130, 246, 0.2);
  color: #3B82F6;
}

.event-card-category {
  font-size: 10px;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
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
  padding-top: 8px;
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

## 2. 悬浮工具栏按钮功能

### 2.1 工具栏完整布局

```
位置: 左下角
坐标: left: 24px, bottom: 24px
Z-index: 600

收起状态:                    展开状态:
┌───┐                        ┌───┐
│ ≡ │                        │ ≡ │  0ms
└───┘                        ├───┤
                             │ 📊 │  50ms
                             ├───┤
                             │ 📋 │  100ms
                             ├───┤
                             │ 👥 │  150ms
                             ├───┤
                             │ 🌙 │  200ms
                             ├───┤
                             │ ⚙️ │  250ms
                             ├───┤
                             │ 🔄 │  300ms
                             └───┘
```

### 2.2 七个按钮详细功能

#### 按钮 1: 主菜单 (≡)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ Menu (≡)                                    │
│ 快捷键        │ Escape                                      │
│ 功能          │ 展开/收起整个工具栏                          │
│ 激活条件      │ 工具栏展开时显示激活状态                     │
│ 始终可见      │ 是 (不参与展开动画)                          │
│ 悬停提示      │ "菜单 (Esc)"                                │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  点击前:                    点击后:                         │
│  ┌───┐                      ┌───┐                           │
│  │ ≡ │                      │ ≡ │  ← 激活状态               │
│  └───┘                      ├───┤                           │
│   ▼                         │ 📊 │                          │
│   │                         │...│                           │
│   └─ 点击                   └───┘                           │
│                                ▲                             │
│                                │                             │
│                           再次点击收起                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

状态转换:
收起状态 ──[点击/ESC]──► 展开状态
展开状态 ──[点击/ESC]──► 收起状态
```

#### 按钮 2: 分析面板 (📊)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ BarChart2 (📊)                              │
│ 快捷键        │ A / a                                       │
│ 功能          │ 切换右侧抽屉 (分析结果面板)                  │
│ 激活条件      │ 右侧抽屉打开时                              │
│ 关联组件      │ DrawerRight                                 │
│ 悬停提示      │ "分析面板 (A)"                              │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  点击:                                                      │
│  ┌───┐                      ┌──────────────────────────┐   │
│  │📊│ ──────────────────►  │     右侧抽屉滑出         │   │
│  │  │                      │     360px, 300ms         │   │
│  └───┘                      └──────────────────────────┘   │
│                                                             │
│  激活状态:                                                  │
│  ┌───┐                                                      │
│  │📊│  ← 渐变背景 cyan→blue                                 │
│  │  │  ← 白色图标                                          │
│  └───┘  ← 发光阴影                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

状态判断:
const isActive = rightDrawer.isOpen || rightDrawer.state === 'opening';
```

#### 按钮 3: 事件列表 (📋)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ List (📋)                                   │
│ 快捷键        │ E / e                                       │
│ 功能          │ 切换底部抽屉 (事件列表)                      │
│ 激活条件      │ 底部抽屉打开时                              │
│ 关联组件      │ DrawerBottom                                │
│ 悬停提示      │ "事件列表 (E)"                              │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  点击:                                                      │
│  ┌───┐                      ┌──────────────────────────┐   │
│  │📋│ ──────────────────►  │     底部抽屉展开         │   │
│  │  │                      │     48px → 200px         │   │
│  └───┘                      └──────────────────────────┘   │
│                                                             │
│  特点:                                                      │
│  - 点击 Header 也可展开/收起                                │
│  - 展开图标旋转 180°                                        │
│  - 事件卡片依次出现                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

状态判断:
const isActive = bottomDrawer.isOpen || bottomDrawer.state === 'opening';
```

#### 按钮 4: 角色详情 (👥)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ Users (👥)                                  │
│ 快捷键        │ R / r                                       │
│ 功能          │ 切换左侧抽屉 (角色详情)                      │
│ 激活条件      │ 左侧抽屉打开时                              │
│ 关联组件      │ DrawerLeft                                  │
│ 悬停提示      │ "角色详情 (R)"                              │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  点击:                                                      │
│  ┌───┐    ┌──────────────────────────┐                      │
│  │👥│ ──►│     左侧抽屉滑出         │                      │
│  │  │    │     320px, 280ms         │                      │
│  └───┘    └──────────────────────────┘                      │
│                                                             │
│  特点:                                                      │
│  - 角色卡片依次出现 (每个延迟 50ms)                          │
│  - 包含搜索和标签筛选                                        │
│  - 点击卡片可选中高亮                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

触发方式:
1. 工具栏按钮点击
2. 快捷键 R
3. 右侧抽屉 Footer 按钮 "查看完整分析"
```

#### 按钮 5: 主题切换 (🌙/☀️)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标 (深色)    │ Moon (🌙)                                   │
│ 图标 (浅色)    │ Sun (☀️)                                    │
│ 快捷键        │ T / t                                       │
│ 功能          │ 深色/浅色主题切换                            │
│ 激活条件      │ 无 (无持续激活状态)                          │
│ 悬停提示      │ "切换主题 (T)"                              │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  深色主题:              浅色主题:                           │
│  ┌───┐                  ┌───┐                               │
│  │ 🌙│                  │ ☀️│                               │
│  └───┘                  └───┘                               │
│   │                       │                                  │
│   └── 点击 ───────────────┘                                  │
│                                                             │
│  动画效果:                                                  │
│  1. 图标缩放: scale(0.8) → scale(1.2) → scale(1)           │
│  2. 旋转: 0° → 180°                                         │
│  3. 时长: 300ms                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

状态管理:
const [theme, setTheme] = useState<'dark' | 'light'>('dark');

const toggleTheme = () => {
  setTheme(prev => prev === 'dark' ? 'light' : 'dark');
};

// 图标切换
const ThemeIcon = theme === 'dark' ? Moon : Sun;
```

#### 按钮 6: 设置 (⚙️)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ Settings (⚙️)                               │
│ 快捷键        │ S / s                                       │
│ 功能          │ 打开设置弹窗                                │
│ 激活条件      │ 设置弹窗打开时                              │
│ 关联组件      │ SettingsModal                               │
│ 悬停提示      │ "设置 (S)"                                  │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  点击:                                                      │
│  ┌───┐                      ┌──────────────────────────┐   │
│  │⚙️│ ──────────────────►  │     设置弹窗弹出         │   │
│  │  │                      │     (Modal)              │   │
│  └───┘                      └──────────────────────────┘   │
│                                                             │
│  弹窗内容:                                                  │
│  - API 配置 (LLM Provider, API Key)                         │
│  - 数据刷新间隔                                             │
│  - 分析深度设置                                             │
│  - 显示偏好                                                 │
│                                                             │
│  关闭方式:                                                  │
│  1. 点击弹窗外部                                            │
│  2. 点击关闭按钮                                            │
│  3. 按 ESC 键                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 按钮 7: 刷新 (🔄)

```
┌─────────────────────────────────────────────────────────────┐
│ 属性          │ 值                                          │
├─────────────────────────────────────────────────────────────┤
│ 图标          │ RefreshCw (🔄)                              │
│ 快捷键        │ F5                                          │
│ 功能          │ 重新获取数据并分析                           │
│ 激活条件      │ 无                                          │
│ 加载状态      │ 刷新时图标旋转                              │
│ 悬停提示      │ "刷新数据 (F5)"                             │
└─────────────────────────────────────────────────────────────┘

交互行为:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  正常状态:              刷新中:                             │
│  ┌───┐                  ┌───┐                               │
│  │ 🔄│                  │ 🔄│  ← 图标旋转                   │
│  │   │                  │ ↻ │  ← animation: spin           │
│  └───┘                  └───┘                               │
│                                                             │
│  刷新流程:                                                  │
│  1. 点击按钮                                                │
│  2. 按钮进入 loading 状态 (图标旋转)                        │
│  3. 清除当前数据                                            │
│  4. 重新获取事件列表                                        │
│  5. 重新运行多 Agent 分析                                   │
│  6. 更新 UI                                                 │
│  7. 按钮恢复正常状态                                        │
│                                                             │
│  防抖:                                                      │
│  - 刷新中再次点击无效                                        │
│  - 最小刷新间隔: 5 秒                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

代码实现:
const [isRefreshing, setIsRefreshing] = useState(false);
const [lastRefresh, setLastRefresh] = useState(0);

const handleRefresh = async () => {
  const now = Date.now();
  if (isRefreshing || now - lastRefresh < 5000) return;

  setIsRefreshing(true);
  try {
    await data.refresh();
    setLastRefresh(now);
  } finally {
    setIsRefreshing(false);
  }
};
```

### 2.3 按钮状态样式矩阵

| 状态 | 背景 | 边框 | 图标色 | 变换 | 阴影 |
|------|------|------|--------|------|------|
| **默认** | rgba(15,23,42,0.9) | rgba(30,41,59,0.8) | #94A3B8 | none | none |
| **悬停** | rgba(0,229,255,0.1) | rgba(0,229,255,0.3) | #00E5FF | translateY(-4px) scale(1.05) | 发光 |
| **激活** | 渐变 cyan→blue | none | #FFFFFF | none | 强发光 |
| **禁用** | rgba(30,41,59,0.5) | none | #475569 | none | none |
| **加载** | 默认 | 默认 | #94A3B8 | 图标旋转 | none |

### 2.4 完整 CSS 代码

```css
/* ================================================
   悬浮工具栏
   ================================================ */

.toolbar {
  position: fixed;
  left: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 600;
}

/* ================================================
   按钮基础
   ================================================ */
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

/* 主按钮始终可见 */
.toolbar-btn.primary {
  opacity: 1;
  transform: none;
  pointer-events: auto;
}

/* ================================================
   展开状态
   ================================================ */
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

/* ================================================
   收起动画 (反向)
   ================================================ */
.toolbar:not(.expanded) .toolbar-btn:not(.primary) {
  opacity: 0;
  transform: translateX(-20px) scale(0.8);
  pointer-events: none;
}

/* 收起时反向延迟 */
.toolbar:not(.expanded) .toolbar-btn:nth-child(7) { transition-delay: 0ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(6) { transition-delay: 30ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(5) { transition-delay: 60ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(4) { transition-delay: 90ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(3) { transition-delay: 120ms; }
.toolbar:not(.expanded) .toolbar-btn:nth-child(2) { transition-delay: 150ms; }

/* ================================================
   悬停状态
   ================================================ */
.toolbar-btn:hover:not(.disabled) {
  transform: translateY(-4px) scale(1.05);
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);

  box-shadow:
    0 8px 32px rgba(0, 229, 255, 0.2),
    0 0 0 1px rgba(0, 229, 255, 0.3);
}

/* 主按钮悬停保持变换 */
.toolbar-btn.primary:hover {
  opacity: 1;
  transform: translateY(-4px) scale(1.05);
}

/* ================================================
   激活状态
   ================================================ */
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

/* ================================================
   禁用状态
   ================================================ */
.toolbar-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* ================================================
   按下状态
   ================================================ */
.toolbar-btn:active:not(.disabled) {
  transform: translateY(-2px) scale(0.98);
  transition-duration: 50ms;
}

/* ================================================
   图标样式
   ================================================ */
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

/* ================================================
   加载状态
   ================================================ */
.toolbar-btn.loading svg {
  animation: toolbar-spin 1s linear infinite;
}

@keyframes toolbar-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ================================================
   Tooltip
   ================================================ */
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

.toolbar-btn:hover::after {
  opacity: 1;
  visibility: visible;
}
```

---

## 3. 快捷键处理

### 3.1 快捷键映射表

```typescript
// 快捷键 → 按钮ID 映射
const SHORTCUT_MAP: Record<string, ToolbarButtonId> = {
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
```

### 3.2 快捷键处理逻辑

```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    // 忽略输入框内的按键
    const target = e.target as HTMLElement;
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.isContentEditable
    ) {
      return;
    }

    // 查找对应的按钮ID
    const buttonId = SHORTCUT_MAP[e.key];
    if (!buttonId) return;

    // 阻止默认行为 (特别是 F5)
    e.preventDefault();

    // 执行对应动作
    const action = BUTTON_ACTIONS[buttonId];
    if (action) {
      action();
    }
  };

  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [/* 依赖项 */]);
```

---

**文档完成** ✓

**文件位置:** `E:\EventPredictor\docs\UI_ANIMATION_INTERACTION.md`
