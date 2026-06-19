# MediNexus 前端 UI 设计方案

> **版本**: v1.0  
> **日期**: 2026-06-12  
> **用途**: 从 0 构建可交互 MediNexus 医疗 AI 平台完整前端  
> **覆盖范围**: 5 个核心页面 + 全局组件 + 交互系统 + 响应式方案

---

## 目录

1. [项目架构总览](#一项目架构总览)
2. [设计令牌 Design Tokens](#二设计令牌-design-tokens)
3. [全局布局系统](#三全局布局系统)
4. [页面 1: 个人健康中心 /profile](#四页面-1-个人健康中心-profile)
5. [页面 2: 健康记录 /records](#五页面-2-健康记录-records)
6. [页面 3: 数字孪生全景视图 /dashboard](#六页面-3-数字孪生全景视图-dashboard)
7. [页面 4: AI 问诊 - 方案合规复核 /consultation/review](#七页面-4-ai-问诊---方案合规复核-consultationreview)
8. [页面 5: AI 问诊 - 多维知识源分析 /consultation/analysis](#八页面-5-ai-问诊---多维知识源分析-consultationanalysis)
9. [共享组件库](#九共享组件库)
10. [交互规范](#十交互规范)
11. [响应式设计](#十一响应式设计)
12. [文件结构与开发顺序](#十二文件结构与开发顺序)

---

## 一、项目架构总览

### 1.1 页面路由映射

| 路由 | 页面名称 | 截图对应 | 用户角色 | 核心功能 |
|------|---------|---------|---------|---------|
| `/dashboard` | 数字孪生全景视图 | 图3 | 患者 | 3D 健康可视化、实时体征监测 |
| `/consultation` | AI 智能问诊 | 图4、图5 | 医生/患者 | 多 Agent 协作诊断、合规复核 |
| `/consultation/analysis` | 知识源分析 | 图5 | 医生 | 多维知识库交叉验证 |
| `/consultation/review` | 方案合规复核 | 图4 | 医生 | 治疗方案安全审查 |
| `/records` | 健康记录 | 图2 | 患者 | 医疗时间线、影像查看 |
| `/profile` | 个人健康中心 | 图1 | 患者 | 健康档案、设备集成、偏好设置 |

### 1.2 双视角架构

系统存在 **患者视角** (图1/2/3) 和 **医生视角** (图4/5) 两种界面模式：

- **患者视角**: 侧边栏导航项为「控制台 / AI 问诊 / 健康记录 / 个人中心」，底部 CTA 为「开始新分析」
- **医生视角**: 侧边栏导航项为「Dashboard / AI Consultation / Health Records / Personal Hub」，底部 CTA 为「New Analysis」，顶部显示「患者: 张三」面包屑

### 1.3 技术栈

```
Next.js 14 (App Router) + React 18 + TypeScript 5 + Tailwind CSS 3
```

---

## 二、设计令牌 (Design Tokens)

### 2.1 颜色系统

基于截图精确采样 + 设计文档融合：

| 令牌名 | 色值 | Tailwind 扩展 | 用途 |
|--------|------|--------------|------|
| `--color-primary` | `#2563EB` | `medical-primary` | 主按钮、链接、高亮背景、进度条填充 |
| `--color-primary-hover` | `#1D4ED8` | `medical-primary-hover` | 按钮悬停态 |
| `--color-primary-light` | `#EFF4FF` | `medical-primary-light` | 侧边栏背景、选中态背景 |
| `--color-primary-subtle` | `#DBEAFE` | `medical-primary-subtle` | 标签背景、轻量高亮 |
| `--color-accent` | `#10B981` | `medical-accent` | 成功状态、健康指标、完成标记 |
| `--color-accent-light` | `#D1FAE5` | `medical-accent-light` | 成功标签背景 |
| `--color-warning` | `#F59E0B` | `medical-warning` | 警告、待办、同步中状态 |
| `--color-warning-light` | `#FEF3C7` | `medical-warning-light` | 警告标签背景 |
| `--color-danger` | `#DC2626` | `medical-danger` | 错误、紧急、禁忌症警报 |
| `--color-danger-light` | `#FEE2E2` | `medical-danger-light` | 危险标签背景 |
| `--color-bg-main` | `#F8FAFF` | `medical-bg` | 主内容区背景 |
| `--color-bg-sidebar` | `#EFF4FF` | `medical-sidebar` | 侧边栏背景 |
| `--color-bg-card` | `#FFFFFF` | `medical-card` | 卡片背景 |
| `--color-bg-elevated` | `#F0F5FF` | `medical-elevated` | 悬浮面板、下拉背景 |
| `--color-text-primary` | `#1E293B` | `medical-text-primary` | 主标题、重要文本 |
| `--color-text-secondary` | `#475569` | `medical-text-secondary` | 副标题、描述文本 |
| `--color-text-muted` | `#94A3B8` | `medical-text-muted` | 时间戳、次要信息 |
| `--color-border` | `#E2E8F0` | `medical-border` | 卡片边框、分割线 |
| `--color-border-light` | `#F1F5F9` | `medical-border-light` | 内部分割线 |

### 2.2 字体系统

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
```

| 层级 | 尺寸 | 字重 | 行高 | 字间距 | 用途 |
|------|------|------|------|--------|------|
| Display | `2.5rem` (40px) | 700 | 1.2 | -0.02em | 页面大标题 |
| H1 | `1.875rem` (30px) | 700 | 1.3 | -0.01em | 区块标题 |
| H2 | `1.25rem` (20px) | 600 | 1.4 | 0 | 卡片标题 |
| H3 | `1rem` (16px) | 600 | 1.5 | 0 | 小标题、列表项 |
| Body | `0.875rem` (14px) | 400 | 1.6 | 0 | 正文 |
| Body-sm | `0.8125rem` (13px) | 400 | 1.5 | 0 | 卡片内描述 |
| Caption | `0.75rem` (12px) | 500 | 1.4 | 0.01em | 标签、时间戳 |
| Mono | `0.75rem` (12px) | 500 | 1.4 | 0 | 编号、代码 |

### 2.3 间距系统

基于 4px 基准单位：

| 令牌 | 值 | 用途 |
|------|-----|------|
| `space-1` | 4px | 图标与文字间距 |
| `space-2` | 8px | 紧凑内边距 |
| `space-3` | 12px | 标准组件内边距 |
| `space-4` | 16px | 卡片内边距 |
| `space-5` | 20px | 卡片间距 |
| `space-6` | 24px | 区块间距 |
| `space-8` | 32px | 大区块间距 |
| `space-10` | 40px | 页面级间距 |

### 2.4 圆角系统

| 令牌 | 值 | 用途 |
|------|-----|------|
| `radius-sm` | 8px | 按钮、输入框 |
| `radius-md` | 12px | 小卡片、标签 |
| `radius-lg` | 16px | 标准卡片 |
| `radius-xl` | 20px | 大卡片、模态框 |
| `radius-full` | 9999px | 头像、徽章、药丸按钮 |

### 2.5 阴影系统

| 令牌 | 值 | 用途 |
|------|-----|------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.04)` | 默认卡片 |
| `shadow-md` | `0 4px 12px rgba(0,0,0,0.06)` | 悬停卡片 |
| `shadow-lg` | `0 8px 24px rgba(0,0,0,0.08)` | 下拉菜单、浮层 |
| `shadow-xl` | `0 16px 40px rgba(0,0,0,0.1)` | 模态框 |
| `shadow-primary` | `0 4px 16px rgba(37,99,235,0.15)` | 主按钮 |

---

## 三、全局布局系统

### 3.1 页面骨架 (Page Skeleton)

所有页面共享统一骨架：

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar (240px fixed)  │  TopBar (64px fixed)               │
│                         ├──────────────────────────────────────┤
│  ┌─────────────────┐    │                                      │
│  │   Brand Logo    │    │  Main Content Area                   │
│  ├─────────────────┤    │  (scrollable, padding: 32px 40px)     │
│  │   Navigation    │    │                                      │
│  │   - Dashboard   │    │  ┌──────────────────────────────┐  │
│  │   - AI Consult  │    │  │   Page Header                  │  │
│  │   - Records     │    │  │   Title + Subtitle + Actions   │  │
│  │   - Profile     │    │  └──────────────────────────────┘  │
│  ├─────────────────┤    │                                      │
│  │   CTA Button    │    │  ┌──────────────────────────────┐  │
│  └─────────────────┘    │  │   Content Grid / Cards         │  │
│                         │  └──────────────────────────────┘  │
│  ┌─────────────────┐    │                                      │
│  │  Settings       │    │                                      │
│  │  Help           │    │                                      │
│  └─────────────────┘    │                                      │
└─────────────────────────┴──────────────────────────────────────┘
```

### 3.2 侧边栏 (Sidebar)

**尺寸**: 宽 240px，高 100vh，固定定位  
**背景**: `#EFF4FF` (`medical-sidebar`)  
**边框**: 右侧 1px solid `#E2E8F0`

**结构层级**:
```
Sidebar
├── Brand Section (padding: 20px 16px)
│   ├── Logo Icon (32x32, rounded-lg, bg-primary)
│   ├── Brand Name "MediNexus" (font-semibold, text-lg)
│   └── Tagline "AI Healthcare Systems" (text-xs, text-muted)
│
├── Navigation (padding: 8px 12px, gap: 4px)
│   ├── NavItem - 控制台 (icon: layout-dashboard)
│   ├── NavItem - AI 问诊 (icon: brain)
│   ├── NavItem - 健康记录 (icon: file-text)
│   └── NavItem - 个人中心 (icon: user-circle)
│       └── [Active State: bg-primary, text-white, shadow-sm]
│
├── Spacer (flex-1)
│
├── CTA Section (padding: 16px 12px)
│   └── Button "+ 开始新分析" (w-full, bg-primary, text-white, rounded-xl)
│
└── Bottom Actions (padding: 12px, gap: 8px)
    ├── ActionItem - 设置 (icon: settings)
    └── ActionItem - 帮助与支持 (icon: help-circle)
```

**NavItem 组件规范**:
- 默认态: `padding: 10px 14px`, `rounded-xl`, `text-secondary`, `hover:bg-white/60`
- 激活态: `bg-primary`, `text-white`, `shadow-sm`, `font-medium`
- 图标: `w-5 h-5`, `strokeWidth: 1.5`, `margin-right: 12px`
- 过渡: `transition-all duration-200`

### 3.3 顶部栏 (TopBar)

**尺寸**: 高 64px，固定定位，z-index: 50  
**背景**: `#F8FAFF` (带 `backdrop-blur-md` 毛玻璃效果)  
**边框**: 底部 1px solid `#E2E8F0`

**结构**:
```
TopBar
├── Left (flex-1)
│   └── Search Input
│       ├── Icon: search (w-4 h-4, text-muted)
│       ├── Placeholder: "搜索医疗记录、见解..." (患者) / "搜索患者、诊断建议或医学文献..." (医生)
│       ├── bg: white, border: 1px solid #E2E8F0, rounded-full
│       └── padding: 8px 16px, width: 400px
│
├── Right (gap: 12px, align-items: center)
│   ├── IconButton - 通知 (bell, 带红点徽标)
│   ├── IconButton - 帮助 (help-circle)
│   ├── IconButton - 设置 (settings)
│   └── UserAvatar (32x32, rounded-full, border: 2px solid white, shadow-sm)
│       └── [医生模式显示 "Dr. Smith 神经内科主任"]
```

### 3.4 面包屑 (Breadcrumb)

仅医生视角页面显示：
- 位置: TopBar 下方，主内容区顶部
- 结构: `问诊 #4092  >  患者: 张三`
- 样式: `text-sm`, 当前项 `text-primary font-medium`, 分隔符 `text-muted`
- 间距: `padding: 16px 0`

---

## 四、页面 1: 个人健康中心 /profile

### 4.1 页面信息架构

```
Profile Page
├── PageHeader
│   ├── Title: "个人健康中心" (text-3xl, font-bold)
│   ├── Subtitle: "管理您的全面数字健康身份。" (text-secondary)
│   └── Action: "导出报告" Button (outline style, icon: download)
│
├── ProfileCard (full-width, rounded-2xl, bg-white, shadow-sm, padding: 24px)
│   ├── AvatarSection (flex, gap: 20px)
│   │   ├── Avatar Placeholder (96x96, rounded-2xl, bg-gray-200, centered "img" text)
│   │   │   └── Online Indicator (12x12, bg-primary, rounded-full, border: 2px white, bottom-right)
│   │   └── InfoStack
│   │       ├── NameRow (flex, align-center, gap: 8px)
│   │       │   ├── "Dr. Lin" (text-xl, font-semibold)
│   │       │   ├── Badge "高级会员" (bg-primary-subtle, text-primary, text-xs, rounded-full, px-2 py-0.5)
│   │       │   └── Icon: map-pin + "Stanford Med" (text-sm, text-muted)
│   │       └── EditIcon (absolute top-right, w-8 h-8, rounded-full, hover:bg-gray-100)
│   └── MetricsRow (flex, gap: 32px, margin-top: 20px)
│       ├── MetricCard
│       │   ├── Label: "综合健康评分" (text-sm, text-muted)
│       │   └── Value: "92" (text-4xl, font-bold, text-primary) + "/100" (text-lg, text-muted)
│       └── MetricCard
│           ├── Label: "生物学年龄" (text-sm, text-muted)
│           ├── Value: "34" (text-4xl, font-bold, text-primary)
│           └── DeltaBadge: "↓ -2岁" (bg-accent-light, text-accent, text-xs, rounded-full)
│
├── ContentGrid (grid-cols-3, gap: 20px, margin-top: 24px)
│   ├── LeftColumn
│   │   └── AIHealthMemoryCard
│   ├── CenterColumn
│   │   └── RecentRecordsCard
│   └── RightColumn
│       ├── DigitalTwinPreview
│       ├── AIPreferencesCard
│       └── SecurityCard
│
└── DeviceIntegrationSection (margin-top: 24px)
    └── DeviceIntegrationCard
```

### 4.2 AI 健康记忆卡片

**尺寸**: 占左列，高度自适应  
**背景**: 白色卡片，圆角 16px，阴影 sm

```
AIHealthMemoryCard
├── Header (flex, justify-between, align-center)
│   ├── Left (flex, align-center, gap: 12px)
│   │   ├── IconCircle (40x40, rounded-full, bg-primary-light, icon: brain)
│   │   └── TitleStack
│   │       ├── "AI 健康记忆" (text-lg, font-semibold)
│   │       └── "最后同步: 2小时前" (text-xs, text-muted)
│   └── Right: empty
│
├── Description (text-sm, text-secondary, margin-top: 12px)
│   └── "Nexus AI 综合您的病史以提供个性化咨询。"
│
├── MemoryList (margin-top: 16px, space-y: 12px)
│   ├── MemoryItem
│   │   ├── Title: "慢性偏头痛史 (先兆型)" (text-sm, font-medium)
│   │   └── Tag: "高置信度" (bg-primary-subtle, text-primary, text-xs, rounded-md, px-2 py-0.5)
│   ├── MemoryItem
│   │   ├── Title: "轻度青霉素过敏" (text-sm, font-medium)
│   │   └── Tag: "医生已验证" (bg-warning-light, text-warning, text-xs, rounded-md, px-2 py-0.5)
│   └── MemoryItem
│       ├── Title: "倾向于清晨预约" (text-sm, font-medium)
│       └── Tag: "推断行为" (bg-gray-100, text-gray-600, text-xs, rounded-md, px-2 py-0.5)
│
└── FooterButton (margin-top: 16px)
    └── "查看所有 AI 记忆" (w-full, text-center, py-2.5, rounded-xl, border, text-sm, hover:bg-gray-50)
```

### 4.3 近期健康记录卡片

```
RecentRecordsCard
├── Header (flex, justify-between, align-center)
│   ├── "近期健康记录" (text-lg, font-semibold)
│   └── Link: "查看完整账单 →" (text-sm, text-primary)
│
└── Timeline (margin-top: 16px, space-y: 0)
    ├── TimelineItem
    │   ├── Left: Dot (8x8, rounded-full, bg-primary, ring: 4px solid white)
    │   ├── Center: Content
    │   │   ├── Title: "综合代谢功能检查" (text-sm, font-medium)
    │   │   ├── Source: "Quest Diagnostics" (text-xs, text-muted, icon: building)
    │   │   └── DetailCard (margin-top: 8px, bg-primary-light/50, rounded-xl, p-3)
    │   │       ├── Icon: check-circle (w-4 h-4, text-primary)
    │   │       └── "所有 14 项生物标志物均在正常范围内。" (text-xs)
    │   └── Right: Date "Oct 12" (text-xs, text-muted, bg-gray-100, rounded-full, px-2 py-0.5)
    ├── TimelineItem
    │   ├── Dot (bg-gray-300)
    │   ├── Title: "流感疫苗 (四价)" (text-sm, font-medium)
    │   ├── Source: "CVS Pharmacy" (text-xs, text-muted)
    │   └── Date: "Sep 28"
    └── TimelineItem
        ├── Dot (bg-gray-300)
        ├── Title: "舒马曲坦 50mg" (text-sm, font-medium)
        ├── Source: "处方续方" (text-xs, text-muted, icon: file-text)
        └── Date: "Aug 15"
```

**时间线样式**:
- 左侧竖线: `width: 2px`, `bg-gray-200`, 绝对定位
- 节点圆点: `8x8px`, `rounded-full`, 当前项 `bg-primary`, 历史项 `bg-gray-300`
- 节点与竖线对齐: `left: -5px` (圆点半宽偏移)
- 内容区: `padding-left: 20px`

### 4.4 数字孪生预览卡片

```
DigitalTwinPreview
├── Header (flex, justify-between, align-center)
│   ├── Left (flex, align-center, gap: 8px)
│   │   ├── Icon: activity (w-5 h-5, text-primary)
│   │   └── "数字孪生" (text-lg, font-semibold)
│   └── Link: "查看 3D →" (text-sm, text-primary)
│
├── ImageContainer (margin-top: 12px, rounded-xl, overflow-hidden, aspect-ratio: 4/3, bg-gray-900)
│   ├── Image: 3D人体模型 (object-fit: cover)
│   └── OverlayBadge (absolute bottom-left, margin: 12px)
│       └── "系统状态正常" (bg-black/50, text-white, text-xs, rounded-lg, px-2 py-1, backdrop-blur)
│
└── MetricsRow (margin-top: 12px, grid-cols-2, gap: 8px)
    ├── MetricPill
    │   ├── "炎症水平" (text-xs, text-muted)
    │   ├── "低" (text-sm, font-semibold, text-accent)
    │   └── DotIndicator (6x6, bg-accent, rounded-full)
    └── MetricPill
        ├── "代谢率" (text-xs, text-muted)
        └── "优" (text-sm, font-semibold, text-primary)
```

### 4.5 AI 偏好设置卡片

```
AIPreferencesCard (margin-top: 16px)
├── Header
│   ├── "AI 偏好设置" (text-lg, font-semibold)
│
├── CommunicationStyle (margin-top: 12px)
│   ├── Label: "沟通风格" (text-sm, text-muted, margin-bottom: 8px)
│   └── ToggleGroup (flex, gap: 8px)
│       ├── Option "临床级" (flex-1, text-center, py-2, rounded-lg, bg-primary, text-white, font-medium)
│       └── Option "通俗易懂" (flex-1, text-center, py-2, rounded-lg, bg-gray-100, text-secondary)
│
└── DetailLevel (margin-top: 16px)
    ├── LabelRow (flex, justify-between)
    │   ├── "详细程度" (text-sm, text-muted)
    │   └── "全面" (text-sm, text-primary, font-medium)
    └── Slider (w-full, margin-top: 8px)
        ├── Track: h-2, bg-gray-200, rounded-full
        ├── Fill: h-2, bg-primary, rounded-full, width: 75%
        └── Thumb: 16x16, bg-primary, rounded-full, shadow, absolute, left: 75%
    └── LabelsRow (flex, justify-between, margin-top: 4px)
        ├── "简述" (text-xs, text-muted)
        └── "详尽" (text-xs, text-muted)
```

### 4.6 安全与隐私卡片

```
SecurityCard (margin-top: 16px)
├── Header (flex, align-center, gap: 8px)
│   ├── Icon: shield (w-5 h-5, text-primary)
│   └── "安全与隐私" (text-lg, font-semibold)
│
└── SecurityList (margin-top: 12px, space-y: 8px)
    ├── SecurityItem (flex, justify-between, align-center, py-2)
    │   ├── Left (flex, align-center, gap: 8px)
    │   │   ├── Icon: key (w-4 h-4, text-muted)
    │   │   └── "双重身份验证" (text-sm)
    │   └── Badge: "已开启" (bg-accent-light, text-accent, text-xs, rounded-full, px-2 py-0.5)
    ├── SecurityItem
    │   ├── Icon: file-check (w-4 h-4, text-muted)
    │   ├── "知情同意管理" (text-sm)
    │   └── Icon: chevron-right (w-4 h-4, text-muted)
    └── SecurityItem
        ├── Icon: archive (w-4 h-4, text-muted)
        ├── "数据归档" (text-sm)
        └── Icon: chevron-right (w-4 h-4, text-muted)
```

### 4.7 设备与数据集成区域

```
DeviceIntegrationSection
├── Header (flex, justify-between, align-center)
│   ├── TitleStack
│   │   ├── "设备与数据集成" (text-lg, font-semibold)
│   │   └── "同步实时生物标志物以进行动态分析。" (text-sm, text-muted)
│   └── Link: "添加来源" (text-sm, text-primary, icon: link)
│
└── DeviceGrid (margin-top: 16px, grid-cols-3, gap: 16px)
    ├── DeviceCard (bg-white, rounded-2xl, p-4, shadow-sm, border)
    │   ├── Header (flex, align-center, gap: 8px)
    │   │   ├── Icon: heart (w-5 h-5, text-danger, fill: currentColor)
    │   │   └── "Apple Health" (text-sm, font-semibold)
    │   ├── DataTypes (text-xs, text-muted, margin-top: 4px)
    │   │   └── "Steps, Vitals, Sleep"
    │   └── StatusRow (margin-top: 12px, flex, justify-between, align-center)
    │       ├── Status (flex, align-center, gap: 4px)
    │       │   ├── Dot (6x6, bg-accent, rounded-full)
    │       │   └── "已连接" (text-xs, text-accent)
    │       └── "活跃" (text-xs, text-muted)
    ├── DeviceCard
    │   ├── Icon: circle-dot (w-5 h-5, text-warning)
    │   ├── "Oura Ring"
    │   ├── "HRV, Temp, Sleep"
    │   └── Status: "同步中..." (text-xs, text-warning) + "刚刚"
    └── DeviceCard
        ├── Icon: watch (w-5 h-5, text-primary)
        ├── "Garmin"
        ├── "Activity, VO2 Max"
        └── Button: "连接" (w-full, mt-2, py-1.5, rounded-lg, border, text-sm, hover:bg-gray-50)
```

---

## 五、页面 2: 健康记录 /records

### 5.1 页面信息架构

```
Records Page
├── PageHeader
│   ├── Title: "健康记录" (text-3xl, font-bold)
│   ├── Subtitle: "综合医疗史、检验报告及AI智能分析档案。" (text-secondary)
│   └── Actions (flex, gap: 12px)
│       ├── Button "筛选" (outline, icon: filter)
│       └── Button "上传新报告" (primary, icon: upload)
│
├── ContentGrid (grid-cols-12, gap: 20px)
│   ├── LeftColumn (col-span-5, space-y: 20px)
│   │   ├── AIArchiveSummaryCard
│   │   └── FollowUpPlanCard
│   ├── CenterColumn (col-span-4)
│   │   └── MedicalTimelineCard
│   └── RightColumn (col-span-3)
│       └── MedicalImagingViewer
```

### 5.2 AI 档案摘要卡片

```
AIArchiveSummaryCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, align-center, gap: 12px)
│   ├── IconCircle (40x40, rounded-full, bg-primary-light, icon: sparkle)
│   └── TitleStack
│       ├── "AI 档案摘要" (text-lg, font-semibold)
│       └── "基于近期 12 份报告生成的临床评估" (text-xs, text-muted)
│
├── SummaryText (margin-top: 16px, text-sm, text-secondary, leading-relaxed)
│   └── "患者整体指标保持平稳。最新全血细胞计数 (CBC) 显示血红蛋白水平已恢复至正常区间 (13.5 g/dL)，前期轻度贫血已改善。近期心电图 (ECG) 提示正常窦性心律。建议继续当前心血管管理方案，并在一周后复查血脂四项。"
│
└── TagsRow (margin-top: 16px, flex, flex-wrap, gap: 8px)
    ├── Tag "贫血改善" (bg-accent-light, text-accent, text-xs, rounded-full, px-3 py-1)
    ├── Tag "ECG 正常" (bg-primary-light, text-primary, text-xs, rounded-full, px-3 py-1)
    └── Tag "需复查血脂" (bg-warning-light, text-warning, text-xs, rounded-full, px-3 py-1)
```

### 5.3 后续跟进计划卡片

```
FollowUpPlanCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, align-center, gap: 12px)
│   ├── IconCircle (40x40, rounded-full, bg-warning-light, icon: clipboard-list)
│   └── "后续跟进计划" (text-lg, font-semibold)
│
└── TodoList (margin-top: 16px, space-y: 12px)
    ├── TodoItem (flex, gap: 12px, align-start)
    │   ├── Checkbox (w-5 h-5, rounded-md, border-2, border-gray-300, mt-0.5)
    │   │   └── [Checked: bg-primary, border-primary, icon: check]
    │   └── Content
    │       ├── Title: "复查空腹血脂" (text-sm, font-medium)
    │       └── Description: "建议在 10月22日 前完成，需空腹 8-12 小时。" (text-xs, text-muted)
    ├── TodoItem
    │   ├── Checkbox (checked state, bg-primary)
    │   ├── Title: "更新心内科处方" (text-sm, font-medium, line-through, text-muted)
    │   └── Description: "已于 10月16日 完成线上续方。" (text-xs, text-muted)
    └── TodoItem
        ├── Checkbox (unchecked)
        ├── Title: "预约内分泌科咨询" (text-sm, font-medium)
        └── ActionButton: "立即预约" (margin-top: 4px, text-xs, text-primary, bg-primary-light, rounded-lg, px-3 py-1)
```

### 5.4 医疗时间线卡片

```
MedicalTimelineCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, justify-between, align-center)
│   ├── "医疗时间线" (text-lg, font-semibold)
│   └── Link: "查看全部 →" (text-sm, text-primary)
│
└── Timeline (margin-top: 20px, space-y: 0, position: relative)
    ├── TimelineVerticalLine (absolute, left: 15px, top: 0, bottom: 0, width: 2px, bg-gray-200)
    │
    ├── TimelineItem (padding-left: 40px, position: relative, padding-bottom: 24px)
    │   ├── Node (absolute, left: 10px, top: 4px, w-5 h-5, rounded-full, bg-primary, ring-4 ring-primary-light)
    │   ├── HeaderRow (flex, justify-between, align-start)
    │   │   ├── Title: "综合代谢组图 (CMP)" (text-base, font-semibold)
    │   │   └── Date: "2023年10月15日" (text-xs, text-muted)
    │   ├── Source: "瑞金医院 · 检验科" (text-xs, text-muted, margin-top: 4px)
    │   └── AttachmentCard (margin-top: 12px, bg-gray-50, rounded-xl, p-3, flex, align-center, gap: 8px)
    │       ├── Icon: file-text (w-5 h-5, text-primary)
    │       ├── "综合代谢组图报告.pdf" (text-sm)
    │       └── Icon: download (w-4 h-4, text-muted, ml-auto)
    │
    ├── TimelineItem
    │   ├── Node (bg-gray-300, ring-gray-100)
    │   ├── Title: "胸部 X 光片 (正侧位)"
    │   ├── Date: "2023年9月28日"
    │   ├── Source: "中山医院 · 影像中心"
    │   └── Tag: "无异常发现" (margin-top: 8px, bg-gray-100, text-gray-600, text-xs, rounded-full, px-2 py-0.5)
    │
    └── TimelineItem
        ├── Node (bg-gray-300, ring-gray-100)
        ├── Title: "专科复诊 - 心血管内科"
        ├── Date: "2023年9月10日"
        └── Description: "李医生记录了血压控制情况，调整了用药剂量。" (text-sm, text-secondary, margin-top: 4px)
```

### 5.5 影像查看器卡片

```
MedicalImagingViewer (bg-white, rounded-2xl, overflow-hidden, shadow-sm)
├── ImageContainer (aspect-ratio: 1/1, bg-gray-900, position: relative)
│   ├── Image: MRI 脑部扫描 (object-fit: cover, opacity: 0.9)
│   ├── TopOverlay (absolute, top: 12px, left: 12px, flex, gap: 8px)
│   │   ├── Badge "MRI" (bg-black/60, text-white, text-xs, rounded-md, px-2 py-1, backdrop-blur)
│   │   └── Badge "脑部" (bg-black/60, text-white, text-xs, rounded-md, px-2 py-1, backdrop-blur)
│   ├── RegionMarker (absolute, top: 40%, left: 55%, w-4 h-4, rounded-full, bg-primary/80, ring-4 ring-primary/30, animate-pulse)
│   └── RegionLabel (absolute, top: calc(40% + 20px), left: 55%, bg-primary/90, text-white, text-xs, rounded-md, px-2 py-1)
│       └── "正常区域"
│
└── InfoSection (padding: 16px)
    ├── Title: "头部核磁共振成像" (text-lg, font-semibold)
    ├── Meta: "2023-10-05 · 包含 142 张切片" (text-xs, text-muted, margin-top: 4px)
    └── ActionButton (margin-top: 12px, w-full, py-2.5, rounded-xl, bg-gray-100, text-sm, text-secondary, hover:bg-gray-200)
        └── "在高级查看器中打开"
```

---

## 六、页面 3: 数字孪生全景视图 /dashboard

### 6.1 页面信息架构

```
Dashboard Page
├── PageHeader
│   ├── Title: "数字孪生全景视图" (text-3xl, font-bold)
│   ├── Subtitle: "实时健康状态监测与预测分析" (text-secondary)
│   └── StatusBadge (flex, align-center, gap: 6px, bg-accent-light, rounded-full, px-3 py-1)
│       ├── Dot (6x6, bg-accent, rounded-full, animate-pulse)
│       └── "实时同步" (text-xs, text-accent, font-medium)
│
├── ContentGrid (grid-cols-12, gap: 20px)
│   ├── LeftColumn (col-span-3, space-y: 16px)
│   │   ├── BiologicalAgeCard
│   │   ├── DualMetricsCard
│   │   └── VitalSignsCard
│   ├── CenterColumn (col-span-6)
│   │   └── DigitalTwinViewer
│   └── RightColumn (col-span-3, space-y: 16px)
│       ├── AIAnalysisCard
│       ├── RiskMapCard
│       └── InterventionCard
```

### 6.2 生物学年龄卡片

```
BiologicalAgeCard (bg-white, rounded-2xl, p-5, shadow-sm)
├── Header (flex, align-center, gap: 8px)
│   ├── Icon: dna (w-5 h-5, text-primary)
│   └── "生物学年龄" (text-base, font-semibold)
│
├── AgeDisplay (margin-top: 12px)
│   ├── Number: "34" (text-5xl, font-bold, text-primary)
│   └── Unit: "岁" (text-lg, text-muted, margin-left: 4px)
│
├── DeltaBadge (margin-top: 8px, flex, align-center, gap: 4px)
│   ├── Icon: arrow-down (w-3 h-3, text-accent)
│   └── "低于实际年龄 2 岁" (text-sm, text-accent, font-medium)
│
└── ProgressSection (margin-top: 16px)
    ├── Track (h-2, bg-gray-200, rounded-full, overflow-hidden)
    ├── Fill (h-full, bg-primary, rounded-full, width: 85%)
    └── LabelRow (flex, justify-between, margin-top: 6px)
        ├── "年轻化轨迹" (text-xs, text-muted)
        └── "优" (text-xs, text-primary, font-medium)
```

### 6.3 双指标卡片

```
DualMetricsCard (grid-cols-2, gap: 12px)
├── MetricCard (bg-white, rounded-2xl, p-4, shadow-sm, text-center)
│   ├── IconCircle (40x40, rounded-full, bg-danger-light, mx-auto, icon: flame)
│   ├── Label: "炎症指数" (text-xs, text-muted, margin-top: 8px)
│   ├── Value: "1.2" (text-2xl, font-bold, text-primary, margin-top: 4px)
│   └── Status: "正常" (text-xs, text-accent, margin-top: 2px)
└── MetricCard
    ├── IconCircle (40x40, rounded-full, bg-primary-light, mx-auto, icon: shield-check)
    ├── Label: "免疫评分" (text-xs, text-muted, margin-top: 8px)
    ├── Value: "92" (text-2xl, font-bold, text-primary, margin-top: 4px)
    └── StatusBadge: "极佳" (text-xs, text-primary, bg-primary-light, rounded-full, px-2 py-0.5, margin-top: 4px, inline-block)
```

### 6.4 核心体征卡片

```
VitalSignsCard (bg-white, rounded-2xl, p-5, shadow-sm)
├── Header
│   └── "核心体征" (text-base, font-semibold)
│
└── VitalList (margin-top: 12px, space-y: 12px)
    ├── VitalItem (flex, justify-between, align-center)
    │   ├── Left (flex, align-center, gap: 10px)
    │   │   ├── Icon: heart-pulse (w-5 h-5, text-muted)
    │   │   └── "静息心率" (text-sm, text-secondary)
    │   └── Right (flex, align-center, gap: 4px)
    │       ├── "62" (text-lg, font-semibold, text-primary)
    │       └── "次/分" (text-xs, text-muted)
    ├── VitalItem
    │   ├── Icon: activity (w-5 h-5, text-muted)
    │   ├── "血压"
    │   └── "118/77" (text-lg, font-semibold, text-primary) + "mmHg" (text-xs, text-muted)
    └── VitalItem
        ├── Icon: droplet (w-5 h-5, text-muted)
        ├── "血氧饱和"
        └── "99" (text-lg, font-semibold, text-primary) + "%" (text-xs, text-muted)
```

### 6.5 数字孪生 3D 查看器

```
DigitalTwinViewer (bg-white, rounded-2xl, overflow-hidden, shadow-sm, position: relative)
├── ViewerContainer (aspect-ratio: 3/4, bg-gradient-to-b from-gray-100 to-gray-200, position: relative, overflow-hidden)
│   ├── BackgroundGrid (absolute, inset-0, opacity-30)
│   │   └── CSS Grid Pattern (repeating-linear-gradient)
│   ├── BodyModel (absolute, inset-0, flex, items-center, justify-center)
│   │   └── SVG/Canvas 3D人体模型 (半透明蓝色调, 中心对齐)
│   ├── HotspotMarkers
│   │   ├── HeadHotspot (absolute, top: 8%, left: 50%, transform: translateX(-50%))
│   │   │   ├── PulseRing (w-8 h-8, rounded-full, bg-danger/30, animate-ping)
│   │   │   └── Core (w-3 h-3, rounded-full, bg-danger, ring-2 ring-white)
│   │   ├── LungHotspot (absolute, top: 28%, left: 45%)
│   │   │   └── [同上脉冲样式]
│   │   └── GutHotspot (absolute, top: 55%, left: 50%, transform: translateX(-50%))
│   │       └── [同上脉冲样式]
│   ├── FloatingPanels (absolute, positioned near hotspots)
│   │   ├── Panel (top: 5%, right: 8%, bg-white/90, backdrop-blur, rounded-lg, p-2, shadow-lg)
│   │   │   └── "PATIENT DIGITAL TWIN" + mini chart
│   │   └── Panel (top: 30%, right: 5%, bg-white/90, backdrop-blur, rounded-lg, p-2, shadow-lg)
│   │       └── "MEDICAL PATHWAY ANALYSIS"
│   └── BottomControls (absolute, bottom: 20px, left: 50%, transform: translateX(-50%))
│       └── ControlBar (bg-white/90, backdrop-blur, rounded-full, px-4 py-2, shadow-lg, flex, gap: 12px)
│           ├── Button: icon: rotate-cw (w-8 h-8, rounded-full, hover:bg-gray-100)
│           ├── Button: icon: layers (w-8 h-8, rounded-full, bg-primary, text-white)
│           └── Button: icon: search (w-8 h-8, rounded-full, hover:bg-gray-100)
│
└── [无底部信息区，纯可视化]
```

### 6.6 AI 综合研判卡片

```
AIAnalysisCard (bg-white, rounded-2xl, p-5, shadow-sm)
├── Header (flex, align-center, gap: 8px)
│   ├── Icon: sparkle (w-5 h-5, text-primary)
│   └── "AI 综合研判" (text-base, font-semibold)
│
└── AnalysisText (margin-top: 12px, text-sm, text-secondary, leading-relaxed)
    └── "基于最新的全息数据模型，您的整体健康状况极佳。心血管系统表现稳定，但需注意近期轻微的呼吸道敏感波动。建议维持当前的运动习惯。"
```

### 6.7 风险图谱卡片

```
RiskMapCard (bg-white, rounded-2xl, p-5, shadow-sm)
├── Header
│   └── "风险图谱" (text-base, font-semibold)
│
└── RiskList (margin-top: 12px, space-y: 12px)
    ├── RiskItem
    │   ├── HeaderRow (flex, justify-between, align-center, margin-bottom: 6px)
    │   │   ├── Left (flex, align-center, gap: 6px)
    │   │   │   ├── Icon: dna (w-4 h-4, text-muted)
    │   │   │   └── "基因遗传风险" (text-sm)
    │   │   └── Status: "低风险" (text-xs, text-accent, font-medium)
    │   └── ProgressBar (h-2, bg-gray-100, rounded-full, overflow-hidden)
    │       └── Fill (h-full, bg-accent, rounded-full, width: 25%)
    ├── RiskItem
    │   ├── Icon: heart (w-4 h-4, text-muted)
    │   ├── "心血管负荷"
    │   ├── Status: "正常" (text-xs, text-primary, font-medium)
    │   └── ProgressBar (bg-primary, width: 60%)
    └── RiskItem
        ├── Icon: wind (w-4 h-4, text-muted)
        ├── "呼吸道敏感度"
        ├── Status: "需关注" (text-xs, text-danger, font-medium)
        └── ProgressBar (bg-danger, width: 78%)
```

### 6.8 干预建议卡片

```
InterventionCard (bg-white, rounded-2xl, p-5, shadow-sm)
├── Label: "干预建议" (text-xs, text-muted, uppercase, tracking-wider, margin-bottom: 8px)
│
├── SuggestionCard (bg-gray-50, rounded-xl, p-4, border)
│   ├── Header (flex, align-center, gap: 8px)
│   │   ├── IconCircle (32x32, rounded-full, bg-primary-light, icon: shield)
│   │   └── "呼吸系统防护计划" (text-sm, font-semibold)
│   └── Description (margin-top: 6px, text-xs, text-secondary, leading-relaxed)
│       └── "查看针对近期花粉季的个性化防护及营养补充建议。"
```

---

## 七、页面 4: AI 问诊 - 方案合规复核 /consultation/review

### 7.1 页面信息架构 (医生视角)

```
ConsultationReview Page
├── Breadcrumb: "问诊 #4092  >  患者: 张三"
├── TopBar (医生模式: 搜索框 + 通知 + 设置 + 帮助 + Dr.Smith头像)
│
├── StageProgressBar (margin-bottom: 24px)
│
├── PageHeader
│   ├── StatusBadge: "合规复核智能体  阶段 3/4" (text-xs, text-primary, bg-primary-light, rounded-full, px-3 py-1)
│   ├── Title: "方案合规复核" (text-3xl, font-bold, margin-top: 12px)
│   ├── Subtitle: "根据临床指南、禁忌症和安全协议，对医生智能体提出的治疗方案进行自动验证。"
│   └── Actions (flex, gap: 12px, margin-top: 16px)
│       ├── Button "查看原始输出" (outline, text-sm)
│       └── Button "批准方案" (primary, icon: check-circle, text-sm)
│
├── ContentGrid (grid-cols-12, gap: 20px)
│   ├── LeftColumn (col-span-8, space-y: 20px)
│   │   ├── TreatmentPlanCard
│   │   └── ContraindicationAlertCard
│   └── RightColumn (col-span-4, space-y: 20px)
│       ├── ReviewFlagCard
│       └── GuidelineTestCard
```

### 7.2 阶段进度条 (StageProgressBar)

```
StageProgressBar (bg-white, rounded-2xl, p-6, shadow-sm)
├── ProgressTrack (flex, align-center, justify-between, position: relative)
│   ├── BackgroundLine (absolute, top: 20px, left: 40px, right: 40px, h-1, bg-gray-200, rounded-full, z-0)
│   ├── ActiveLine (absolute, top: 20px, left: 40px, width: 50%, h-1, bg-primary, rounded-full, z-0)
│   │
│   ├── StageItem (flex-1, flex, flex-col, align-center, gap: 8px, z-10)
│   │   ├── StageNumber (w-10 h-10, rounded-full, flex, items-center, justify-center, font-bold)
│   │   │   └── [Completed: bg-primary, text-white] / [Active: bg-primary, text-white, ring-4 ring-primary-light] / [Pending: bg-gray-200, text-gray-500]
│   │   └── StageLabel (text-xs, text-center, max-width: 80px)
│   │       └── [Active: text-primary font-medium] / [Pending: text-muted]
│   │
│   ├── Stage 1: "分诊与接诊" (completed)
│   ├── Stage 2: "诊断映射" (completed)
│   ├── Stage 3: "评估复核" (active, with red dot indicator top-right of number)
│   └── Stage 4: "治疗方案" (pending)
```

### 7.3 建议治疗方案卡片

```
TreatmentPlanCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, justify-between, align-center)
│   ├── Left (flex, align-center, gap: 8px)
│   │   ├── Icon: clipboard-list (w-5 h-5, text-primary)
│   │   └── "建议治疗方案" (text-lg, font-semibold)
│   └── Source: "来源: 医生智能体" (text-xs, text-muted)
│
└── PlanGrid (margin-top: 16px, grid-cols-2, gap: 16px)
    ├── LeftPlan
    │   ├── PrimaryDrugCard (bg-gray-50, rounded-xl, p-4)
    │   │   ├── Label: "主要药物" (text-xs, text-muted, uppercase)
    │   │   ├── DrugName: "阿哌沙班 (Eliquis) 5mg" (text-base, font-semibold, margin-top: 4px)
    │   │   └── Dosage: "BID (每日两次), 口服" (text-sm, text-secondary, margin-top: 2px)
    │   └── AdjuvantCard (bg-gray-50, rounded-xl, p-4, margin-top: 12px)
    │       ├── Label: "辅助治疗" (text-xs, text-muted, uppercase)
    │       ├── DrugName: "阿托伐他汀 40mg" (text-base, font-semibold)
    │       └── Dosage: "QHS (每晚), 口服" (text-sm, text-secondary)
    └── RightContext
        └── ClinicalContextCard (bg-gray-50, rounded-xl, p-4)
            ├── Label: "临床背景" (text-xs, text-muted, uppercase, margin-bottom: 8px)
            ├── ContextItem (flex, align-center, gap: 6px, margin-bottom: 6px)
            │   ├── Icon: check-circle (w-4 h-4, text-primary)
            │   └── "诊断: 非瓣膜性心房颤动 (AFib)" (text-sm)
            ├── ContextItem
            │   ├── Icon: check-circle (w-4 h-4, text-primary)
            │   └── "CHA2DS2-VASc 评分: 3 (中风高风险)" (text-sm)
            └── ContextItem
                ├── Icon: check-circle (w-4 h-4, text-primary)
                └── "肾功能: CrCl 45 mL/min (中度损伤)" (text-sm)
```

### 7.4 标记需复核卡片

```
ReviewFlagCard (bg-white, rounded-2xl, p-6, shadow-sm, border, border-warning/30)
├── IconSection (flex, justify-center, margin-bottom: 12px)
│   └── IconPair (position: relative, w-16 h-16)
│       ├── ShieldIcon (absolute, w-12 h-12, text-gray-300)
│       └── AlertTriangle (absolute, bottom-0, right-0, w-6 h-6, text-warning, fill: currentColor)
│
├── Title: "标记需复核" (text-lg, font-semibold, text-center)
├── Subtitle: "检测到 1 个严重相互作用" (text-sm, text-muted, text-center, margin-top: 4px)
│
└── RiskScoreSection (margin-top: 16px)
    ├── Label: "风险评分" (text-xs, text-muted, text-center)
    ├── Score: "高 (8.5/10)" (text-lg, font-bold, text-danger, text-center, margin-top: 4px)
    └── ProgressBar (margin-top: 8px, h-2, bg-gray-200, rounded-full)
        └── Fill (h-full, bg-danger, rounded-full, width: 85%)
```

### 7.5 指南基准测试卡片

```
GuidelineTestCard (bg-white, rounded-2xl, p-6, shadow-sm, margin-top: 16px)
├── Header (flex, align-center, gap: 8px)
│   ├── Icon: book-open (w-5 h-5, text-primary)
│   └── "指南基准测试" (text-base, font-semibold)
│
└── GuidelineList (margin-top: 12px, space-y: 12px)
    ├── GuidelineItem (bg-gray-50, rounded-xl, p-4)
    │   ├── HeaderRow (flex, justify-between, align-center)
    │   │   ├── Badge: "AHA/ACC 2019 指南" (bg-primary-light, text-primary, text-xs, rounded-md, px-2 py-0.5)
    │   │   └── Icon: check-circle (w-5 h-5, text-accent)
    │   ├── Content (margin-top: 8px, text-sm, text-secondary)
    │   │   └── "对于符合条件的 AFib 患者，推荐使用 DOACs 而非华法林 (I 类, A 级)。选择阿哌沙班是合适的。"
    │   └── Citation (margin-top: 8px, text-xs, text-primary)
    │       └── "Circulation. 2019;140:e125-e151"
    │
    └── GuidelineItem (bg-warning-light/30, rounded-xl, p-4, border, border-warning/20)
        ├── HeaderRow
        │   ├── Badge: "FDA 剂量方案" (bg-warning-light, text-warning, text-xs, rounded-md, px-2 py-0.5)
        │   └── Icon: alert-circle (w-5 h-5, text-warning)
        ├── Content (text-sm, text-secondary)
        │   └── "如果满足至少两项标准，需将剂量减至 2.5mg BID: 年龄 ≥80 岁，体重 ≤60kg，血清肌酐 ≥1.5 mg/dL。"
        └── AlertBox (margin-top: 8px, bg-warning-light, rounded-lg, p-3, flex, gap: 8px)
            ├── Icon: alert-triangle (w-4 h-4, text-warning, flex-shrink-0, margin-top: 2px)
            └── AlertText (text-xs, text-warning)
                └── "患者符合 1 项标准 (年龄 82)。标准的 5mg 剂量在技术上是合规的，但由于相互作用，建议谨慎使用。"
```

### 7.6 禁忌症警报卡片 (核心交互)

```
ContraindicationAlertCard (bg-white, rounded-2xl, p-6, shadow-sm, border-l-4, border-l-danger)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── Icon: alert-triangle (w-5 h-5, text-danger, fill: currentColor)
│   └── "禁忌症警报" (text-lg, font-semibold, text-danger)
│
├── AlertContent (bg-danger-light/50, rounded-xl, p-5, border, border-danger/20)
│   ├── AlertHeader (flex, align-center, gap: 8px)
│   │   ├── Icon: pill (w-5 h-5, text-danger)
│   │   └── "药物相互作用: 严重" (text-base, font-semibold, text-danger)
│   ├── DrugPair (margin-top: 4px, text-sm, font-medium)
│   │   └── "阿哌沙班 + 克拉霉素 (患者病史中存在)。"
│   └── DetailBox (margin-top: 12px, bg-white, rounded-lg, p-4)
│       └── "同时使用强效 CYP3A4 和 P-gp 抑制剂 (克拉霉素) 会增加阿哌沙班暴露量，显著增加大出血风险。" (text-sm, text-secondary, leading-relaxed)
│
└── ActionRow (margin-top: 16px, flex, gap: 12px)
    ├── Button "忽略风险" (flex-1, outline, border-gray-300, text-secondary, hover:bg-gray-50, py-2.5, rounded-xl)
    └── Button "修改剂量为 2.5mg BID" (flex-1, bg-danger, text-white, hover:bg-red-700, py-2.5, rounded-xl, shadow-sm)
```

---

## 八、页面 5: AI 问诊 - 多维知识源分析 /consultation/analysis

### 8.1 页面信息架构

```
ConsultationAnalysis Page
├── Breadcrumb: "问诊 #4092  >  患者: 张三"
├── TopBar (医生模式)
├── StageProgressBar (当前阶段 2: 诊断映射, 高亮)
│
├── AnalysisHeader (margin-top: 24px)
│   ├── TitleRow (flex, align-center, gap: 12px)
│   │   ├── Icon: network (w-6 h-6, text-primary)
│   │   ├── "多维知识源深度分析" (text-2xl, font-bold)
│   │   └── "(Knowledge Source Analysis)" (text-lg, text-muted, font-normal)
│   └── LiveBadge (margin-left: auto, bg-primary, text-white, text-xs, rounded-full, px-3 py-1, flex, align-center, gap: 4px)
│       ├── Dot (w-2 h-2, bg-white, rounded-full, animate-pulse)
│       └── "AI 正在实时检索与分析..."
│
├── Description (margin-top: 8px, text-sm, text-secondary)
│   └── "MediNexus 正在基于以下三个专业知识库对当前病例进行多维度交叉验证:"
│
└── KnowledgeGrid (margin-top: 24px, grid-cols-3, gap: 20px)
    ├── ClinicalCaseCard
    ├── MedicalEthicsCard
    └── FrontierPaperCard
```

### 8.2 临床案例卡片

```
ClinicalCaseCard (bg-white, rounded-2xl, p-6, shadow-sm, hover:shadow-md, transition)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── IconCircle (36x36, rounded-lg, bg-primary-light, icon: hospital)
│   └── "临床案例" (text-lg, font-semibold, text-primary)
│
├── CaseCard (bg-gray-50, rounded-xl, p-4, border)
│   ├── CaseID: "病例 #2023-0912:" (text-sm, font-semibold)
│   ├── CaseTitle: "复杂性偏头痛临床路径" (text-base, font-semibold, margin-top: 2px)
│   ├── SourceRow (margin-top: 8px, flex, align-center, gap: 4px)
│   │   ├── "来源: 协和医院" (text-xs, text-muted)
│   │   └── "临床数据库" (text-xs, text-muted)
│   └── MatchRow (margin-top: 8px, flex, align-center, gap: 6px)
│       ├── "匹配度:" (text-xs, text-muted)
│       ├── "94%" (text-lg, font-bold, text-primary)
│       └── ProgressMini (w-16, h-1.5, bg-gray-200, rounded-full)
│           └── Fill (w-full, h-full, bg-primary, rounded-full)
│
└── ActionLink (margin-top: 12px, text-sm, text-primary, flex, align-center, gap: 4px)
    └── "查看完整病例" + Icon: external-link (w-3 h-3)
```

### 8.3 医学伦理卡片

```
MedicalEthicsCard (bg-white, rounded-2xl, p-6, shadow-sm, hover:shadow-md, transition)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── IconCircle (36x36, rounded-lg, bg-warning-light, icon: scale)
│   └── "医学伦理" (text-lg, font-semibold, text-warning)
│
├── EthicsCard (bg-gray-50, rounded-xl, p-4, border)
│   ├── Title: "知情同意与辅助诊断责任归属指南" (text-base, font-semibold, leading-snug)
│   └── SourceRow (margin-top: 8px)
│       ├── "来源: 国家卫健委医疗伦理委员会" (text-xs, text-muted)
│
└── ActionLink (margin-top: 12px, text-sm, text-primary, flex, align-center, gap: 4px)
    └── "法律条文详述" + Icon: external-link (w-3 h-3)
```

### 8.4 前沿论文卡片

```
FrontierPaperCard (bg-white, rounded-2xl, p-6, shadow-sm, hover:shadow-md, transition)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── IconCircle (36x36, rounded-lg, bg-accent-light, icon: book-open)
│   └── "前沿论文" (text-lg, font-semibold, text-accent)
│
├── PaperCard (bg-gray-50, rounded-xl, p-4, border)
│   ├── JournalBadge (bg-accent-light, text-accent, text-xs, rounded-md, px-2 py-0.5, inline-block, margin-bottom: 8px)
│   │   └── "Nature Medicine"
│   ├── Title: "基于多智能体架构的罕见病诊断逻辑分析 (2024)" (text-base, font-semibold, leading-snug)
│   └── Source: "Nature Medicine Journal" (text-xs, text-muted, margin-top: 8px)
│
└── ActionLink (margin-top: 12px, text-sm, text-primary, flex, align-center, gap: 4px)
    └── "访问原文" + Icon: external-link (w-3 h-3)
```

---

## 九、共享组件库

### 9.1 图标系统 (SVG)

所有图标使用 Lucide-React 风格，strokeWidth=1.5：

| 图标名 | 用途 | 尺寸 |
|--------|------|------|
| `LayoutDashboard` | 控制台导航 | 20px |
| `Brain` | AI 问诊导航 | 20px |
| `FileText` | 健康记录导航 | 20px |
| `UserCircle` | 个人中心导航 | 20px |
| `Stethoscope` | 开始问诊 CTA | 20px |
| `Search` | 搜索框 | 16px |
| `Bell` | 通知 | 20px |
| `HelpCircle` | 帮助 | 20px |
| `Settings` | 设置 | 20px |
| `Download` | 导出报告 | 16px |
| `Upload` | 上传报告 | 16px |
| `Filter` | 筛选 | 16px |
| `ChevronRight` | 展开/链接 | 16px |
| `CheckCircle` | 完成/正常 | 16px |
| `AlertTriangle` | 警告/紧急 | 20px |
| `Heart` | 健康/心率 | 20px |
| `Activity` | 体征/数字孪生 | 20px |
| `Shield` | 安全/隐私 | 20px |
| `Sparkles` | AI 分析 | 20px |
| `Pill` | 药物 | 20px |
| `ClipboardList` | 计划/记录 | 20px |
| `ExternalLink` | 外部链接 | 14px |
| `Link` | 添加来源 | 16px |
| `RotateCw` | 3D 旋转 | 20px |
| `Layers` | 3D 图层 | 20px |
| `Dna` | 生物学年龄 | 20px |
| `Flame` | 炎症指数 | 20px |
| `Wind` | 呼吸道 | 16px |
| `Droplet` | 血氧 | 20px |
| `Scale` | 伦理/法律 | 20px |
| `BookOpen` | 论文/指南 | 20px |
| `Hospital` | 医院/临床 | 20px |
| `Network` | 知识图谱 | 24px |
| `MapPin` | 位置 | 16px |
| `Edit` | 编辑 | 16px |
| `Check` | 勾选 | 16px |
| `X` | 关闭 | 16px |
| `Plus` | 添加 | 16px |
| `ArrowDown` | 下降 | 12px |
| `ArrowUp` | 上升 | 12px |

### 9.2 卡片组件 (Card)

```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';  // 0, 16px, 24px, 32px
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  border?: boolean;
  borderColor?: string;
  hover?: boolean;
}

// 默认: bg-white, rounded-2xl (16px), shadow-sm, p-6
// hover=true: hover:shadow-md transition-shadow duration-200
```

### 9.3 按钮组件 (Button)

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

// Primary: bg-primary, text-white, rounded-xl, shadow-primary, hover:bg-primary-hover
// Secondary: bg-gray-100, text-secondary, rounded-xl, hover:bg-gray-200
// Outline: border, bg-transparent, text-secondary, rounded-xl, hover:bg-gray-50
// Ghost: bg-transparent, text-secondary, hover:bg-gray-100
// Danger: bg-danger, text-white, rounded-xl, hover:bg-red-700
```

### 9.4 徽章组件 (Badge)

```typescript
interface BadgeProps {
  variant: 'primary' | 'accent' | 'warning' | 'danger' | 'muted';
  size: 'sm' | 'md';
  children: React.ReactNode;
}

// 样式: rounded-full, px-2 py-0.5 (sm) / px-3 py-1 (md)
// primary: bg-primary-light, text-primary
// accent: bg-accent-light, text-accent
// warning: bg-warning-light, text-warning
// danger: bg-danger-light, text-danger
// muted: bg-gray-100, text-gray-600
```

### 9.5 进度条组件 (ProgressBar)

```typescript
interface ProgressBarProps {
  value: number;        // 0-100
  max?: number;
  variant: 'primary' | 'accent' | 'warning' | 'danger';
  size: 'sm' | 'md' | 'lg';  // h-1.5, h-2, h-3
  showLabel?: boolean;
  labelPosition?: 'left' | 'right' | 'top';
}

// Track: bg-gray-200, rounded-full, overflow-hidden
// Fill: rounded-full, transition-all duration-300
```

### 9.6 时间线组件 (Timeline)

```typescript
interface TimelineProps {
  items: TimelineItem[];
  lineColor?: string;
  activeColor?: string;
}

interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  date?: string;
  status: 'active' | 'completed' | 'pending';
  icon?: React.ReactNode;
  content?: React.ReactNode;  // 自定义内容区
}

// 竖线: absolute, left: 15px, w-0.5, bg-gray-200
// 节点: absolute, left: 10px, w-5 h-5, rounded-full
// 内容区: pl-10
```

### 9.7 滑块组件 (Slider)

```typescript
interface SliderProps {
  min: number;
  max: number;
  value: number;
  step?: number;
  onChange: (value: number) => void;
  showLabels?: boolean;
  leftLabel?: string;
  rightLabel?: string;
}

// Track: h-2, bg-gray-200, rounded-full
// Fill: h-2, bg-primary, rounded-full, absolute
// Thumb: w-4 h-4, bg-primary, rounded-full, shadow, cursor-pointer
```

### 9.8 复选框组件 (Checkbox)

```typescript
interface CheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
}

// 未选中: w-5 h-5, rounded-md, border-2, border-gray-300, bg-white
// 选中: bg-primary, border-primary, 内部白色 check icon
// 过渡: transition-colors duration-150
```

---

## 十、交互规范

### 10.1 全局交互

| 交互类型 | 触发 | 反馈 | 时长 | 缓动 |
|---------|------|------|------|------|
| 按钮悬停 | mouseenter | 背景色变化 / 阴影提升 | 150ms | ease-out |
| 按钮点击 | mousedown | scale(0.98) | 100ms | ease-in-out |
| 卡片悬停 | mouseenter | shadow-md | 200ms | ease-out |
| 导航切换 | click | 背景色填充 + 文字变白 | 200ms | ease-out |
| 页面加载 | mount | 内容淡入 + 上移 8px | 300ms | ease-out |
| 数据加载 | 异步请求 | 骨架屏闪烁 | 1.5s | linear infinite |
| 实时同步 | WebSocket | 脉冲动画 dot | 2s | ease-in-out infinite |
| 进度条 | 数值变化 | 宽度平滑过渡 | 500ms | ease-out |
| 警报出现 | 检测到风险 | 红色边框 + 轻微震动 | 300ms | ease-out |
| 模态框 | 打开 | 背景淡黑 + 内容缩放 | 200ms | ease-out |
| 下拉菜单 | 点击 | 展开 + 淡入 | 150ms | ease-out |
| 折叠展开 | 点击 | 高度过渡 + 旋转箭头 | 300ms | ease-in-out |

### 10.2 状态管理

```typescript
// 全局 UI 状态
interface UIState {
  sidebarCollapsed: boolean;      // 侧边栏折叠 (移动端)
  currentTheme: 'light' | 'dark'; // 主题模式
  notifications: Notification[];   // 通知列表
  userRole: 'patient' | 'doctor'; // 当前用户角色
  language: 'zh' | 'en';          // 语言
}

// 问诊流程状态
interface ConsultationState {
  sessionId: string;
  currentStage: 1 | 2 | 3 | 4;
  stages: {
    1: { status: 'completed' | 'active' | 'pending'; data: TriageData };
    2: { status: 'completed' | 'active' | 'pending'; data: DiagnosisData };
    3: { status: 'completed' | 'active' | 'pending'; data: ReviewData };
    4: { status: 'completed' | 'active' | 'pending'; data: TreatmentData };
  };
  knowledgeSources: KnowledgeSource[];
  alerts: Alert[];
  isLoading: boolean;
}

// 数字孪生状态
interface DigitalTwinState {
  isSyncing: boolean;
  lastSyncTime: Date;
  hotspots: Hotspot[];
  selectedLayer: 'all' | 'cardiovascular' | 'respiratory' | 'neural';
  rotation: { x: number; y: number; z: number };
  zoom: number;
}
```

### 10.3 动画关键帧

```css
/* 脉冲动画 - 用于实时同步指示器 */
@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

/* 骨架屏闪烁 */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 警报震动 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

/* 内容淡入上移 */
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 进度条流动 */
@keyframes progress-flow {
  0% { background-position: 0 0; }
  100% { background-position: 40px 0; }
}
```

### 10.4 键盘导航

- `Tab`: 顺序遍历所有可交互元素
- `Shift + Tab`: 反向遍历
- `Enter` / `Space`: 激活按钮/链接/复选框
- `Escape`: 关闭模态框/下拉菜单
- `Arrow Keys`: 在滑块、单选组、下拉菜单中导航
- 所有可交互元素必须有 `focus-visible` 环: `ring-2 ring-primary ring-offset-2`

### 10.5 无障碍要求

- 颜色对比度: 正文 ≥ 4.5:1，大文字 ≥ 3:1
- 所有图标按钮必须有 `aria-label`
- 表单输入必须有关联 `label`
- 动态内容更新使用 `aria-live` 区域
- 支持 `prefers-reduced-motion`: 禁用动画，使用即时过渡
- 图片必须有 `alt` 文本

---

## 十一、响应式设计

### 11.1 断点系统

| 断点 | 宽度 | 代号 | 布局变化 |
|------|------|------|---------|
| `sm` | 640px | 手机横屏 | 侧边栏隐藏，顶部栏简化 |
| `md` | 768px | 平板竖屏 | 2列网格，侧边栏可折叠 |
| `lg` | 1024px | 平板横屏/小笔记本 | 3列网格，侧边栏固定 |
| `xl` | 1280px | 桌面 | 完整布局，最大内容宽度 |
| `2xl` | 1536px | 大桌面 | 更宽间距，更大字体 |

### 11.2 移动端适配 (< 768px)

**侧边栏**:
- 默认隐藏，通过汉堡菜单触发
- 滑入动画: `translateX(-100%)` → `translateX(0)`, 300ms
- 遮罩层: `bg-black/50`, 点击关闭
- 宽度: 280px (占屏宽 70%)

**顶部栏**:
- 搜索框收缩为图标，点击展开全屏搜索
- 用户头像保留，名称隐藏
- 通知/设置/帮助合并为更多菜单

**内容区**:
- 所有网格变为单列
- 卡片全宽，减少内边距 (p-4)
- 页面标题字号缩小: text-2xl
- 数字孪生 3D 查看器高度固定 400px

**底部导航** (仅移动端):
```
┌─────────────────────────────────────────┐
│  控制台  │  AI问诊  │  记录  │  我的   │
└─────────────────────────────────────────┘
```
- 固定底部，高度 56px
- 图标 + 文字，选中态颜色变化

### 11.3 平板适配 (768px - 1024px)

**侧边栏**:
- 可折叠为 64px 宽图标栏
- 悬停展开显示文字
- 导航项仅显示图标，tooltip 显示名称

**内容区**:
- 3列网格变为 2列
- 个人健康中心: 左列(个人信息+AI记忆) / 右列(记录+数字孪生+偏好+安全)
- 健康记录: 左列(AI摘要+跟进计划+时间线) / 右列(影像查看器)
- 数字孪生: 左列(年龄+指标+体征) / 右列(3D模型+分析+风险+建议)

### 11.4 桌面适配 (> 1024px)

- 完整布局，所有列展开
- 侧边栏 240px 固定
- 内容区最大宽度: `calc(100vw - 240px)`
- 内边距: `px-10 py-8`

---

## 十二、文件结构与开发顺序

### 12.1 文件结构

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # 根布局 (Sidebar + TopBar)
│   │   ├── globals.css                   # Tailwind + 设计令牌 + 动画
│   │   ├── page.tsx                      # 重定向到 /dashboard
│   │   ├── dashboard/
│   │   │   └── page.tsx                  # 数字孪生全景视图
│   │   ├── consultation/
│   │   │   ├── page.tsx                  # AI 问诊主入口
│   │   │   ├── analysis/
│   │   │   │   └── page.tsx              # 知识源分析
│   │   │   └── review/
│   │   │       └── page.tsx              # 方案合规复核
│   │   ├── records/
│   │   │   └── page.tsx                  # 健康记录
│   │   └── profile/
│   │       └── page.tsx                  # 个人健康中心
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx               # 侧边栏
│   │   │   ├── TopBar.tsx                # 顶部栏
│   │   │   ├── Breadcrumb.tsx            # 面包屑
│   │   │   └── MobileNav.tsx             # 移动端底部导航
│   │   │
│   │   ├── ui/
│   │   │   ├── Card.tsx                  # 卡片容器
│   │   │   ├── Button.tsx                # 按钮
│   │   │   ├── Badge.tsx                 # 徽章
│   │   │   ├── ProgressBar.tsx           # 进度条
│   │   │   ├── Timeline.tsx              # 时间线
│   │   │   ├── Slider.tsx                # 滑块
│   │   │   ├── Checkbox.tsx              # 复选框
│   │   │   ├── SearchInput.tsx           # 搜索输入
│   │   │   ├── IconButton.tsx            # 图标按钮
│   │   │   └── Avatar.tsx                # 头像
│   │   │
│   │   ├── dashboard/
│   │   │   ├── BiologicalAgeCard.tsx     # 生物学年龄
│   │   │   ├── DualMetricsCard.tsx       # 双指标
│   │   │   ├── VitalSignsCard.tsx        # 核心体征
│   │   │   ├── DigitalTwinViewer.tsx     # 3D 查看器
│   │   │   ├── AIAnalysisCard.tsx        # AI 综合研判
│   │   │   ├── RiskMapCard.tsx           # 风险图谱
│   │   │   └── InterventionCard.tsx      # 干预建议
│   │   │
│   │   ├── consultation/
│   │   │   ├── StageProgressBar.tsx      # 阶段进度条
│   │   │   ├── TreatmentPlanCard.tsx     # 治疗方案
│   │   │   ├── ContraindicationAlert.tsx # 禁忌症警报
│   │   │   ├── ReviewFlagCard.tsx        # 需复核标记
│   │   │   ├── GuidelineTestCard.tsx     # 指南测试
│   │   │   ├── KnowledgeSourceCard.tsx   # 知识源卡片
│   │   │   └── LiveBadge.tsx             # 实时徽章
│   │   │
│   │   ├── records/
│   │   │   ├── AIArchiveSummary.tsx      # AI 档案摘要
│   │   │   ├── FollowUpPlan.tsx          # 跟进计划
│   │   │   ├── MedicalTimeline.tsx       # 医疗时间线
│   │   │   └── ImagingViewer.tsx         # 影像查看器
│   │   │
│   │   └── profile/
│   │       ├── ProfileCard.tsx           # 个人信息卡片
│   │       ├── AIHealthMemory.tsx        # AI 健康记忆
│   │       ├── RecentRecords.tsx         # 近期记录
│   │       ├── DigitalTwinPreview.tsx    # 数字孪生预览
│   │       ├── AIPreferences.tsx         # AI 偏好设置
│   │       ├── SecurityPrivacy.tsx       # 安全隐私
│   │       └── DeviceIntegration.tsx     # 设备集成
│   │
│   ├── hooks/
│   │   ├── useConsultation.ts            # 问诊状态管理
│   │   ├── useDigitalTwin.ts             # 数字孪生状态
│   │   ├── useMediaQuery.ts              # 响应式断点
│   │   └── useWebSocket.ts               # WebSocket 连接
│   │
│   ├── lib/
│   │   ├── utils.ts                      # 工具函数
│   │   ├── api.ts                        # REST API 客户端
│   │   └── websocket.ts                  # WebSocket 客户端
│   │
│   ├── types/
│   │   ├── index.ts                      # 全局类型
│   │   ├── consultation.ts               # 问诊类型
│   │   ├── dashboard.ts                  # 数字孪生类型
│   │   └── records.ts                    # 记录类型
│   │
│   └── data/
│       └── mock.ts                       # Mock 数据
│
├── public/
│   ├── images/
│   │   ├── avatar-placeholder.jpg
│   │   ├── digital-twin-body.png
│   │   └── mri-scan.jpg
│   └── icons/
│       └── (SVG icons if needed)
│
├── tailwind.config.ts                    # Tailwind 配置 + 医疗主题
├── postcss.config.js                     # PostCSS
├── next.config.js                          # Next.js 配置
├── tsconfig.json                           # TypeScript 配置
└── package.json
```

### 12.2 开发顺序建议

**Phase 1: 基础搭建 (Day 1-2)**
1. 初始化 Next.js 项目 + Tailwind CSS
2. 配置 `tailwind.config.ts` - 添加所有医疗颜色令牌
3. 创建 `globals.css` - 导入字体 + 定义动画关键帧
4. 创建基础 UI 组件: Card, Button, Badge, ProgressBar
5. 创建布局组件: Sidebar, TopBar

**Phase 2: 页面骨架 (Day 3-4)**
6. 实现 `/profile` 页面 - 个人健康中心 (最复杂的患者页面)
7. 实现 `/records` 页面 - 健康记录
8. 实现 `/dashboard` 页面 - 数字孪生 (3D 部分用占位图)

**Phase 3: 问诊流程 (Day 5-6)**
9. 实现 `/consultation/analysis` - 知识源分析
10. 实现 `/consultation/review` - 方案合规复核
11. 实现 StageProgressBar 组件
12. 连接 Mock 数据

**Phase 4: 交互完善 (Day 7-8)**
13. 添加所有 hover/active/focus 状态
14. 实现移动端响应式适配
15. 添加动画过渡效果
16. 实现键盘导航

**Phase 5: 数据连接 (Day 9-10)**
17. 创建 API 客户端
18. 创建 WebSocket 连接
19. 连接真实数据流
20. 测试所有交互场景

### 12.3 Tailwind 配置核心

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        medical: {
          primary: '#2563EB',
          'primary-hover': '#1D4ED8',
          'primary-light': '#EFF4FF',
          'primary-subtle': '#DBEAFE',
          accent: '#10B981',
          'accent-light': '#D1FAE5',
          warning: '#F59E0B',
          'warning-light': '#FEF3C7',
          danger: '#DC2626',
          'danger-light': '#FEE2E2',
          bg: '#F8FAFF',
          sidebar: '#EFF4FF',
          card: '#FFFFFF',
          elevated: '#F0F5FF',
          'text-primary': '#1E293B',
          'text-secondary': '#475569',
          'text-muted': '#94A3B8',
          border: '#E2E8F0',
          'border-light': '#F1F5F9',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'medical-sm': '0 1px 2px rgba(0,0,0,0.04)',
        'medical-md': '0 4px 12px rgba(0,0,0,0.06)',
        'medical-lg': '0 8px 24px rgba(0,0,0,0.08)',
        'medical-primary': '0 4px 16px rgba(37,99,235,0.15)',
      },
      borderRadius: {
        'medical-sm': '8px',
        'medical-md': '12px',
        'medical-lg': '16px',
        'medical-xl': '20px',
      },
      animation: {
        'pulse-ring': 'pulse-ring 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s linear infinite',
        'shake': 'shake 0.3s ease-in-out',
        'fade-in-up': 'fade-in-up 0.3s ease-out',
      },
      keyframes: {
        'pulse-ring': {
          '0%': { transform: 'scale(0.8)', opacity: '1' },
          '100%': { transform: 'scale(2)', opacity: '0' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '25%': { transform: 'translateX(-4px)' },
          '75%': { transform: 'translateX(4px)' },
        },
        'fade-in-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

---

## 附录 A: Mock 数据示例

```typescript
// src/data/mock.ts

export const mockProfile = {
  name: 'Dr. Lin',
  avatar: '/images/avatar-placeholder.jpg',
  membership: '高级会员',
  institution: 'Stanford Med',
  healthScore: 92,
  biologicalAge: 34,
  ageDelta: -2,
  isOnline: true,
};

export const mockHealthMemory = [
  { id: '1', title: '慢性偏头痛史 (先兆型)', confidence: 'high', tag: '高置信度' },
  { id: '2', title: '轻度青霉素过敏', confidence: 'verified', tag: '医生已验证' },
  { id: '3', title: '倾向于清晨预约', confidence: 'inferred', tag: '推断行为' },
];

export const mockRecentRecords = [
  { id: '1', title: '综合代谢功能检查', source: 'Quest Diagnostics', date: 'Oct 12', status: 'active', detail: '所有 14 项生物标志物均在正常范围内。' },
  { id: '2', title: '流感疫苗 (四价)', source: 'CVS Pharmacy', date: 'Sep 28', status: 'completed' },
  { id: '3', title: '舒马曲坦 50mg', source: '处方续方', date: 'Aug 15', status: 'completed' },
];

export const mockTimeline = [
  { id: '1', title: '综合代谢组图 (CMP)', source: '瑞金医院 · 检验科', date: '2023年10月15日', status: 'active', hasAttachment: true, attachmentName: '综合代谢组图报告.pdf' },
  { id: '2', title: '胸部 X 光片 (正侧位)', source: '中山医院 · 影像中心', date: '2023年9月28日', status: 'completed', tag: '无异常发现' },
  { id: '3', title: '专科复诊 - 心血管内科', source: '', date: '2023年9月10日', status: 'completed', description: '李医生记录了血压控制情况，调整了用药剂量。' },
];

export const mockTreatmentPlan = {
  primaryDrug: { name: '阿哌沙班 (Eliquis)', dosage: '5mg', frequency: 'BID (每日两次)', route: '口服' },
  adjuvantDrug: { name: '阿托伐他汀', dosage: '40mg', frequency: 'QHS (每晚)', route: '口服' },
  clinicalContext: [
    { label: '诊断', value: '非瓣膜性心房颤动 (AFib)' },
    { label: 'CHA2DS2-VASc 评分', value: '3 (中风高风险)' },
    { label: '肾功能', value: 'CrCl 45 mL/min (中度损伤)' },
  ],
};

export const mockKnowledgeSources = [
  { id: '1', type: 'clinical', title: '复杂性偏头痛临床路径', caseId: '#2023-0912', source: '协和医院', matchRate: 94, database: '临床数据库' },
  { id: '2', type: 'ethics', title: '知情同意与辅助诊断责任归属指南', source: '国家卫健委医疗伦理委员会' },
  { id: '3', type: 'paper', title: '基于多智能体架构的罕见病诊断逻辑分析 (2024)', journal: 'Nature Medicine', source: 'Nature Medicine Journal' },
];

export const mockDevices = [
  { id: '1', name: 'Apple Health', icon: 'heart', dataTypes: 'Steps, Vitals, Sleep', status: 'connected', lastSync: '活跃', color: 'danger' },
  { id: '2', name: 'Oura Ring', icon: 'circle-dot', dataTypes: 'HRV, Temp, Sleep', status: 'syncing', lastSync: '刚刚', color: 'warning' },
  { id: '3', name: 'Garmin', icon: 'watch', dataTypes: 'Activity, VO2 Max', status: 'disconnected', color: 'primary' },
];

export const mockAlerts = [
  { id: '1', type: 'contraindication', severity: 'high', title: '药物相互作用: 严重', drugs: ['阿哌沙班', '克拉霉素'], description: '同时使用强效 CYP3A4 和 P-gp 抑制剂 (克拉霉素) 会增加阿哌沙班暴露量，显著增加大出血风险。', riskScore: 8.5 },
];

export const mockGuidelines = [
  { id: '1', name: 'AHA/ACC 2019 指南', status: 'pass', content: '对于符合条件的 AFib 患者，推荐使用 DOACs 而非华法林 (I 类, A 级)。选择阿哌沙班是合适的。', citation: 'Circulation. 2019;140:e125-e151' },
  { id: '2', name: 'FDA 剂量方案', status: 'warning', content: '如果满足至少两项标准，需将剂量减至 2.5mg BID: 年龄 ≥80 岁，体重 ≤60kg，血清肌酐 ≥1.5 mg/dL。', alert: '患者符合 1 项标准 (年龄 82)。标准的 5mg 剂量在技术上是合规的，但由于相互作用，建议谨慎使用。' },
];
```

---

## 附录 B: 图标映射表 (Lucide React)

```typescript
// 安装: npm install lucide-react
// 导入示例:
import {
  LayoutDashboard, Brain, FileText, UserCircle, Stethoscope,
  Search, Bell, HelpCircle, Settings, Download, Upload,
  Filter, ChevronRight, CheckCircle, AlertTriangle, Heart,
  Activity, Shield, Sparkles, Pill, ClipboardList, ExternalLink,
  Link, RotateCw, Layers, Dna, Flame, Wind, Droplet, Scale,
  BookOpen, Hospital, Network, MapPin, Edit, Check, X, Plus,
  ArrowDown, ArrowUp, HeartPulse, CircleDot, Watch, Key,
  FileCheck, Archive, Building, CheckSquare, Calendar,
  Clock, Eye, MoreHorizontal, Menu, XCircle, AlertCircle,
  Info, TrendingUp, TrendingDown, Minus, Maximize2, Minimize2,
  RefreshCw, Play, Pause, Stop, SkipForward, SkipBack,
  Volume2, VolumeX, Mic, MicOff, Camera, CameraOff, Send,
  Paperclip, Smile, AtSign, Hash, Lock, Unlock, EyeOff,
  Trash2, Copy, Share2, Flag, Bookmark, Star, ThumbsUp,
  MessageCircle, Mail, Phone, Video, Map, Navigation,
  Compass, Globe, Home, Inbox, LogOut, LogIn, UserPlus,
  Users, UserMinus, UserCheck, UserX, Briefcase, Award,
  Certificate, GraduationCap, School, Library, BookMarked,
  BookOpenCheck, ScrollText, FileCheck2, FileClock, FileCode,
  FileJson, FileSpreadsheet, FileImage, FileAudio, FileVideo,
  Folder, FolderOpen, FolderMinus, FolderPlus, FolderGit,
  Folders, HardDrive, Database, Server, Cloud, CloudRain,
  Sun, Moon, Thermometer, Gauge, Zap, Battery, BatteryCharging,
  BatteryWarning, BatteryFull, Wifi, WifiOff, Bluetooth, BluetoothOff,
  Radio, Signal, SignalHigh, SignalMedium, SignalLow, QrCode,
  Barcode, Scan, ScanLine, ScanFace, Fingerprint, KeyRound,
  ShieldAlert, ShieldCheck, ShieldX, ShieldOff, LockKeyhole,
  UnlockKeyhole, EyeIcon, EyeOffIcon, FingerprintIcon
} from 'lucide-react';
```

---

> **文档结束**  
> 此文档覆盖 MediNexus 前端全部 5 个核心页面的 UI 设计方案，包含精确的布局结构、组件层级、样式参数、交互规范和响应式策略。开发者可依据此文档从 0 构建完整的可交互医疗 AI 平台前端。
