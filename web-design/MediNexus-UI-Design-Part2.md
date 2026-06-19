# MediNexus 前端 UI 设计方案 - 高优补充页面 (Part 2)

> **版本**: v1.1  
> **日期**: 2026-06-12  
> **补充页面**: 患者管理列表页、系统状态页、设置页、分诊接诊页、上传报告页  
> **基于**: 已有 5 页面设计文档 + Part 1 + 设计参考文档 + 截图分析

---

## 目录

1. [页面 9: 患者管理列表页 /patients](#一页面-9-患者管理列表页-patients)
2. [页面 10: 系统状态页 /system-status](#二页面-10-系统状态页-system-status)
3. [页面 11: 设置页 /settings](#三页面-11-设置页-settings)
4. [页面 12: 分诊与接诊页 /consultation/triage](#四页面-12-分诊与接诊页-consultationtriage)
5. [页面 13: 上传新报告页 /reports/new](#五页面-13-上传新报告页-reportsnew)
6. [全局交互补充](#六全局交互补充)

---

## 一、页面 9: 患者管理列表页 /patients

### 1.1 页面定位

医生视角的核心工作页面。展示医生负责的所有患者列表，支持按状态、科室、时间筛选，快速查看患者摘要信息，点击进入具体问诊流程。从图4/5的面包屑"问诊#4092 > 患者:张三"可推断此页面为医生选择患者的入口。

### 1.2 页面信息架构

```
Patients Page (医生视角, 带侧边栏+顶部栏)
├── PageHeader
│   ├── Title: "患者管理" (text-3xl, font-bold)
│   ├── Subtitle: "管理您的患者队列，查看问诊状态与历史记录。" (text-secondary)
│   └── Actions (flex, gap: 12px)
│       ├── Button "新建问诊" (primary, icon: plus)
│       └── Button "导出列表" (outline, icon: download)
│
├── FilterBar (bg-white, rounded-2xl, p-4, shadow-sm, margin-bottom: 24px, flex, flex-wrap, gap: 12px, align-center)
│   ├── SearchInput (flex-1, min-width: 240px, bg-gray-50, rounded-xl, border, px-4, py-2.5, text-sm)
│   │   ├── Icon: search (w-4 h-4, text-muted, margin-right: 8px)
│   │   └── Placeholder: "搜索患者姓名、ID、症状..."
│   ├── FilterDropdown "状态" (bg-gray-50, rounded-xl, border, px-3, py-2.5, text-sm, cursor-pointer)
│   │   └── [选项: 全部 / 待分诊 / 诊断中 / 待复核 / 已完成]
│   ├── FilterDropdown "科室" (同上)
│   │   └── [选项: 全部 / 内科 / 外科 / 心血管 / 神经科 / 皮肤科]
│   ├── FilterDropdown "时间" (同上)
│   │   └── [选项: 今天 / 近7天 / 近30天 / 全部]
│   └── SortButton (bg-gray-50, rounded-xl, border, px-3, py-2.5, text-sm, icon: arrow-up-down)
│       └── "排序"
│
├── StatsRow (grid-cols-4, gap: 16px, margin-bottom: 24px)
│   ├── StatCard (bg-white, rounded-2xl, p-5, shadow-sm, flex, align-center, gap: 16px)
│   │   ├── IconCircle (48x48, rounded-xl, bg-primary-light, icon: users, w-6 h-6, text-primary)
│   │   └── StatContent
│   │       ├── Value: "128" (text-2xl, font-bold, text-primary)
│   │       └── Label: "总患者数" (text-sm, text-muted)
│   ├── StatCard (icon: clock, bg-warning-light, text-warning)
│   │   ├── Value: "12" (text-2xl, font-bold, text-warning)
│   │   └── Label: "待处理" (text-sm, text-muted)
│   ├── StatCard (icon: activity, bg-accent-light, text-accent)
│   │   ├── Value: "86" (text-2xl, font-bold, text-accent)
│   │   └── Label: "本月新增" (text-sm, text-muted)
│   └── StatCard (icon: alert-triangle, bg-danger-light, text-danger)
│       ├── Value: "3" (text-2xl, font-bold, text-danger)
│       └── Label: "紧急标记" (text-sm, text-muted)
│
├── PatientTable (bg-white, rounded-2xl, shadow-sm, overflow-hidden)
│   ├── TableHeader (bg-gray-50, padding: 12px 24px, grid, grid-cols-12, gap-4, text-xs, text-muted, font-medium, uppercase, tracking-wider)
│   │   ├── Col "患者信息" (col-span-3)
│   │   ├── Col "当前阶段" (col-span-2)
│   │   ├── Col "症状摘要" (col-span-3)
│   │   ├── Col "更新时间" (col-span-2)
│   │   └── Col "操作" (col-span-2, text-right)
│   │
│   └── PatientRows (divide-y, divide-gray-100)
│       ├── PatientRow (padding: 16px 24px, grid, grid-cols-12, gap-4, align-center, hover:bg-gray-50, transition, cursor-pointer)
│       │   ├── PatientInfo (col-span-3, flex, align-center, gap- 12px)
│       │   │   ├── Avatar (w-10 h-10, rounded-full, bg-gray-200, flex, items-center, justify-center, text-sm, font-medium, text-gray-600)
│       │   │   │   └── "张" (患者姓氏)
│       │   │   └── InfoStack
│       │   │       ├── Name: "张三" (text-sm, font-semibold)
│       │   │       ├── ID: "#4092" (text-xs, text-muted, font-mono)
│       │   │       └── Tags (flex, gap: 4px, margin-top: 2px)
│       │   │           └── [Emergency: bg-danger-light, text-danger, text-xs, rounded-full, px-2 py-0.5]
│       │   │               └── "紧急"
│       │   ├── Stage (col-span-2)
│       │   │   └── StageBadge (bg-primary-light, text-primary, rounded-full, px-3 py-1, text-xs, font-medium, inline-flex, align-center, gap: 4px)
│       │   │       ├── Dot (w-2 h-2, bg-primary, rounded-full, animate-pulse)
│       │   │       └── "评估复核"
│       │   ├── Symptoms (col-span-3, text-sm, text-secondary, truncate)
│       │   │   └── "头痛、发热、心悸，持续3天..."
│       │   ├── UpdateTime (col-span-2, text-xs, text-muted)
│       │   │   └── "10分钟前"
│       │   └── Actions (col-span-2, flex, justify-end, gap: 8px)
│       │       ├── IconButton "查看" (w-8 h-8, rounded-lg, hover:bg-gray-100, icon: eye, w-4 h-4, text-muted)
│       │       ├── IconButton "编辑" (w-8 h-8, rounded-lg, hover:bg-gray-100, icon: edit, w-4 h-4, text-muted)
│       │       └── IconButton "更多" (w-8 h-8, rounded-lg, hover:bg-gray-100, icon: more-horizontal, w-4 h-4, text-muted)
│       │
│       ├── PatientRow [重复结构...]
│       └── PatientRow [重复结构...]
│
└── Pagination (flex, justify-between, align-center, margin-top: 24px, padding: 0 24px)
    ├── LeftInfo (text-sm, text-muted)
    │   └── "显示 1-10 条，共 128 条"
    └── PageButtons (flex, gap: 8px)
        ├── Button "上一页" (outline, text-sm, disabled:opacity-50)
        ├── PageNumber "1" (bg-primary, text-white, w-8 h-8, rounded-lg, text-sm, font-medium)
        ├── PageNumber "2" (hover:bg-gray-100, w-8 h-8, rounded-lg, text-sm, text-secondary)
        ├── PageNumber "3" (同上)
        ├── Ellipsis "..." (text-muted)
        ├── PageNumber "13" (同上)
        └── Button "下一页" (outline, text-sm)
```

### 1.3 患者卡片视图 (移动端/平板)

```
PatientCards (grid-cols-1 md:grid-cols-2, gap: 16px, lg:hidden)
├── PatientCard (bg-white, rounded-2xl, p-5, shadow-sm, border, border-gray-100, hover:shadow-md, transition)
│   ├── CardHeader (flex, justify-between, align-start, margin-bottom: 12px)
│   │   ├── PatientInfo (flex, align-center, gap: 12px)
│   │   │   ├── Avatar (w-12 h-12, rounded-full, bg-gray-200, flex, items-center, justify-center, text-lg, font-medium)
│   │   │   │   └── "张"
│   │   │   └── InfoStack
│   │   │       ├── Name: "张三" (text-base, font-semibold)
│   │   │       └── ID: "#4092" (text-xs, text-muted, font-mono)
│   │   └── StatusBadge (flex-shrink-0)
│   │       └── [Emergency: bg-danger-light, text-danger, rounded-full, px-2 py-0.5, text-xs]
│   │           └── "紧急"
│   ├── SymptomPreview (text-sm, text-secondary, margin-bottom: 12px, line-clamp-2)
│   │   └── "头痛、发热、心悸，持续3天，伴有恶心症状..."
│   ├── MetaRow (flex, justify-between, align-center, margin-bottom: 12px)
│   │   ├── StageBadge (bg-primary-light, text-primary, rounded-full, px-2 py-0.5, text-xs)
│   │   │   └── "评估复核"
│   │   └── Time: "10分钟前" (text-xs, text-muted)
│   └── ActionRow (flex, gap: 8px)
│       ├── Button "查看详情" (flex-1, bg-primary, text-white, rounded-xl, py-2, text-sm, text-center)
│       └── Button "继续问诊" (flex-1, border, rounded-xl, py-2, text-sm, text-center, text-secondary)
```

### 1.4 空状态

```
EmptyState (text-center, padding: 80px 24px)
├── IconCircle (w-20 h-20, mx-auto, rounded-full, bg-gray-100, flex, items-center, justify-center, margin-bottom: 20px)
│   └── icon: users (w-10 h-10, text-gray-300)
├── Title: "暂无患者" (text-xl, font-semibold, text-secondary, margin-bottom: 8px)
├── Description: "当前没有符合条件的患者记录。" (text-sm, text-muted, margin-bottom: 24px)
└── Button "新建问诊" (bg-primary, text-white, rounded-xl, px-6, py-3, text-sm)
```

---

## 二、页面 10: 系统状态页 /system-status

### 2.1 页面定位

平台运维监控页面，展示所有后端服务、AI 模型、API 接口的健康状态。供管理员和技术人员使用，也可向普通用户展示系统可用性。从图5侧边栏"System Status"导航项推断此页面存在。

### 2.2 页面信息架构

```
SystemStatus Page (管理员/医生视角)
├── PageHeader
│   ├── Title: "系统状态" (text-3xl, font-bold)
│   ├── Subtitle: "实时监控 MediNexus 各服务组件的运行状态。" (text-secondary)
│   └── Actions (flex, gap: 12px)
│       ├── Button "刷新状态" (outline, icon: refresh-cw)
│       └── Button "查看日志" (outline, icon: file-text)
│
├── OverviewCards (grid-cols-4, gap: 16px, margin-bottom: 24px)
│   ├── StatusCard (bg-white, rounded-2xl, p-5, shadow-sm, border-l-4, border-l-accent)
│   │   ├── Header (flex, justify-between, align-center, margin-bottom: 8px)
│   │   │   ├── "系统整体状态" (text-sm, text-muted)
│   │   │   └── StatusDot (w-3 h-3, bg-accent, rounded-full, animate-pulse)
│   │   └── Value: "正常运行" (text-xl, font-bold, text-accent)
│   ├── StatusCard (border-l-primary)
│   │   ├── "API 服务"
│   │   └── Value: "12/12 正常" (text-xl, font-bold, text-primary)
│   ├── StatusCard (border-l-warning)
│   │   ├── "AI 模型"
│   │   └── Value: "2/3 正常" (text-xl, font-bold, text-warning)
│   └── StatusCard (border-l-accent)
│       ├── "数据库"
│       └── Value: "连接正常" (text-xl, font-bold, text-accent)
│
├── ServiceGrid (grid-cols-2, gap: 20px)
│   ├── LeftColumn (space-y: 20px)
│   │   └── APIServicesCard
│   └── RightColumn (space-y: 20px)
│       ├── AIModelsCard
│       └── DatabaseCard
│
└── IncidentHistoryCard (margin-top: 20px)
```

### 2.3 API 服务状态卡片

```
APIServicesCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│   ├── Left (flex, align-center, gap: 8px)
│   │   ├── Icon: server (w-5 h-5, text-primary)
│   │   └── "API 服务" (text-lg, font-semibold)
│   └── StatusBadge (bg-accent-light, text-accent, rounded-full, px-3 py-1, text-xs, font-medium)
│       └── "全部正常"
│
└── ServiceList (space-y: 8px)
    ├── ServiceItem (flex, justify-between, align-center, py-3, border-b, border-gray-100)
    │   ├── Left (flex, align-center, gap- 12px)
    │   │   ├── StatusDot (w-2.5 h-2.5, rounded-full, bg-accent)
    │   │   ├── ServiceName: "用户认证服务" (text-sm, font-medium)
│   │   └── Endpoint: "/api/v1/auth" (text-xs, text-muted, font-mono)
    │   └── Right (flex, align-center, gap: 16px)
    │       ├── LatencyBadge (text-xs, text-muted)
    │       │   └── "12ms"
    │       └── UptimeBadge (text-xs, text-accent)
    │           └── "99.9%"
    ├── ServiceItem
    │   ├── StatusDot (bg-accent)
    │   ├── "问诊会话服务"
    │   ├── "/api/v1/consult"
    │   ├── "28ms"
    │   └── "99.8%"
    ├── ServiceItem
    │   ├── StatusDot (bg-accent)
    │   ├── "健康记录服务"
    │   ├── "/api/v1/records"
    │   ├── "15ms"
    │   └── "99.9%"
    ├── ServiceItem
    │   ├── StatusDot (bg-accent)
    │   ├── "WebSocket 服务"
    │   ├── "/ws"
    │   ├── "8ms"
    │   └── "99.7%"
    ├── ServiceItem
    │   ├── StatusDot (bg-accent)
    │   ├── "OCR 识别服务"
    │   ├── "/api/v1/ocr"
    │   ├── "145ms"
    │   └── "99.5%"
    └── ServiceItem
        ├── StatusDot (bg-warning)
        ├── "报告解析服务"
        ├── "/api/v1/parse"
        ├── "2.3s ⚠️"
        └── "98.2%"
```

### 2.4 AI 模型状态卡片

```
AIModelsCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│   ├── Left (flex, align-center, gap: 8px)
│   │   ├── Icon: brain (w-5 h-5, text-primary)
│   │   └── "AI 模型" (text-lg, font-semibold)
│   └── StatusBadge (bg-warning-light, text-warning, rounded-full, px-3 py-1, text-xs, font-medium)
│       └── "1 个异常"
│
└── ModelList (space-y: 8px)
    ├── ModelItem (flex, justify-between, align-center, py-3, border-b, border-gray-100)
    │   ├── Left (flex, align-center, gap- 12px)
    │   │   ├── StatusDot (w-2.5 h-2.5, rounded-full, bg-accent)
    │   │   ├── ModelName: "Triage Agent (导诊)" (text-sm, font-medium)
    │   │   └── ModelVersion: "v2.1.0" (text-xs, text-muted, font-mono)
    │   └── Right (flex, align-center, gap: 16px)
    │       ├── LoadBar (w-24, h-1.5, bg-gray-200, rounded-full)
    │       │   └── Fill (w-1/2, h-full, bg-accent, rounded-full)
    │       └── LoadText (text-xs, text-muted)
    │           └── "负载 45%"
    ├── ModelItem
    │   ├── StatusDot (bg-accent)
    │   ├── "Doctor Agent (诊断)"
    │   ├── "v3.0.2"
    │   ├── LoadBar (w-3/4, bg-accent)
    │   └── "负载 72%"
    ├── ModelItem
    │   ├── StatusDot (bg-accent)
    │   ├── "Review Agent (审方)"
    │   ├── "v2.0.1"
    │   ├── LoadBar (w-1/3, bg-accent)
    │   └── "负载 28%"
    └── ModelItem (bg-warning-light/30, rounded-lg, px-3, py-2, -mx-3)
        ├── StatusDot (bg-warning, animate-pulse)
        ├── ModelName: "Follow-up Agent (随访)" (text-sm, font-medium)
        ├── ModelVersion: "v1.5.0" (text-xs, text-muted, font-mono)
        ├── AlertText (text-xs, text-warning, margin-top: 2px)
        │   └── "模型加载超时，正在重试..."
        └── ActionButton (margin-top: 6px, text-xs, text-primary, bg-primary-light, rounded-lg, px-3 py-1)
            └── "重启服务"
```

### 2.5 数据库状态卡片

```
DatabaseCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── Icon: database (w-5 h-5, text-primary)
│   └── "数据库" (text-lg, font-semibold)
│
└── DBMetrics (grid-cols-2, gap: 16px)
    ├── MetricCard (bg-gray-50, rounded-xl, p-4)
    │   ├── Label: "连接池" (text-xs, text-muted, margin-bottom: 4px)
    │   └── Value: "8/20" (text-lg, font-bold, text-primary)
    ├── MetricCard (bg-gray-50, rounded-xl, p-4)
    │   ├── Label: "查询延迟" (text-xs, text-muted, margin-bottom: 4px)
    │   └── Value: "4.2ms" (text-lg, font-bold, text-accent)
    ├── MetricCard (bg-gray-50, rounded-xl, p-4)
    │   ├── Label: "存储使用" (text-xs, text-muted, margin-bottom: 4px)
    │   └── Value: "67%" (text-lg, font-bold, text-primary)
    └── MetricCard (bg-gray-50, rounded-xl, p-4)
        ├── Label: "活跃会话" (text-xs, text-muted, margin-bottom: 4px)
        └── Value: "142" (text-lg, font-bold, text-primary)
```

### 2.6 事件历史卡片

```
IncidentHistoryCard (bg-white, rounded-2xl, p-6, shadow-sm, margin-top: 20px)
├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│   ├── "事件历史" (text-lg, font-semibold)
│   └── Link: "查看全部" (text-sm, text-primary)
│
└── EventList (space-y: 0, divide-y, divide-gray-100)
    ├── EventItem (flex, align-center, gap: 12px, py-3)
    │   ├── StatusDot (w-2 h-2, rounded-full, bg-accent, flex-shrink-0)
    │   ├── EventText (flex-1, text-sm, text-secondary)
    │   │   └── "API 服务自动扩容完成"
    │   └── Time (text-xs, text-muted, flex-shrink-0)
    │       └── "2小时前"
    ├── EventItem
    │   ├── StatusDot (bg-warning)
    │   ├── "Follow-up Agent 模型响应超时，已自动重启"
    │   └── "5小时前"
    ├── EventItem
    │   ├── StatusDot (bg-accent)
    │   ├── "系统版本更新至 v1.2.0"
    │   └── "1天前"
    └── EventItem
        ├── StatusDot (bg-danger)
        ├── "数据库连接池短暂耗尽，已自动恢复"
        └── "3天前"
```

---

## 三、页面 11: 设置页 /settings

### 3.1 页面定位

用户个性化配置中心，从图1/5侧边栏底部"设置"按钮进入。覆盖语言、通知、隐私、数据、账户安全等全部用户偏好设置。采用左侧标签导航 + 右侧内容区的经典设置布局。

### 3.2 页面信息架构

```
Settings Page
├── PageHeader
│   ├── Title: "设置" (text-3xl, font-bold)
│   └── Subtitle: "管理您的账户偏好和系统配置。" (text-secondary)
│
├── SettingsLayout (flex, gap: 24px, margin-top: 24px)
│   ├── SettingsNav (w-64, flex-shrink-0, hidden lg:block)
│   │   └── NavList (bg-white, rounded-2xl, shadow-sm, p-2, space-y: 1)
│   │       ├── NavItem "账户信息" (active, bg-primary-light, text-primary, rounded-xl, px-4, py-3, text-sm, font-medium, flex, align-center, gap-3)
│   │       │   └── icon: user (w-4 h-4)
│   │       ├── NavItem "通知偏好" (hover:bg-gray-50, rounded-xl, px-4, py-3, text-sm, text-secondary, flex, align-center, gap-3)
│   │       │   └── icon: bell (w-4 h-4)
│   │       ├── NavItem "语言与地区" (同上)
│   │       │   └── icon: globe (w-4 h-4)
│   │       ├── NavItem "隐私与安全" (同上)
│   │       │   └── icon: shield (w-4 h-4)
│   │       ├── NavItem "数据管理" (同上)
│   │       │   └── icon: database (w-4 h-4)
│   │       ├── NavItem "设备管理" (同上)
│   │       │   └── icon: monitor (w-4 h-4)
│   │       └── NavItem "关于系统" (同上)
│   │           └── icon: info (w-4 h-4)
│   │
│   └── SettingsContent (flex-1, bg-white, rounded-2xl, shadow-sm, padding: 32px)
│       ├── [根据选中标签显示不同内容]
│       └── AccountSection (默认显示)
```

### 3.3 账户信息设置

```
AccountSection
├── SectionHeader (margin-bottom: 24px)
│   ├── "账户信息" (text-xl, font-semibold)
│   └── "管理您的个人资料和登录方式。" (text-sm, text-muted, margin-top: 4px)
│
├── ProfileForm (space-y- 24px)
│   ├── AvatarRow (flex, align-center, gap- 16px, margin-bottom: 8px)
│   │   ├── Avatar (w-20 h-20, rounded-2xl, bg-gray-200, flex, items-center, justify-center)
│   │   │   └── [或用户上传图片]
│   │   └── AvatarActions (flex, flex-col, gap: 8px)
│   │       ├── Button "上传新头像" (outline, text-sm, icon: upload)
│   │       └── Button "删除头像" (ghost, text-sm, text-danger, icon: trash-2)
│   │
│   ├── FormGrid (grid-cols-2, gap: 16px)
│   │   ├── InputGroup
│   │   │   ├── Label: "姓名" (text-sm, font-medium, margin-bottom: 6px)
│   │   │   └── Input (value: "Dr. Lin", w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │   ├── InputGroup
│   │   │   ├── Label: "邮箱" (text-sm, font-medium, margin-bottom: 6px)
│   │   │   └── Input (value: "lin@stanford.edu", type: email, w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │   ├── InputGroup
│   │   │   ├── Label: "手机号" (text-sm, font-medium, margin-bottom: 6px)
│   │   │   └── Input (value: "+86 138****8888", type: tel, w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │   └── InputGroup
│   │       ├── Label: "所属机构" (text-sm, font-medium, margin-bottom: 6px)
│   │       └── Input (value: "Stanford Med", w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │
│   ├── Divider (margin: 24px 0, h-px, bg-gray-100)
│   │
│   ├── PasswordSection
│   │   ├── SectionTitle: "修改密码" (text-base, font-semibold, margin-bottom: 16px)
│   │   └── PasswordGrid (grid-cols-2, gap: 16px)
│   │       ├── InputGroup
│   │       │   ├── Label: "当前密码" (text-sm, font-medium, margin-bottom: 6px)
│   │       │   └── Input (type: password, placeholder: "请输入当前密码", w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │       ├── InputGroup
│   │       │   ├── Label: "新密码" (text-sm, font-medium, margin-bottom: 6px)
│   │       │   └── Input (type: password, placeholder: "至少8位", w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │       └── InputGroup (col-span-2)
│   │           ├── Label: "确认新密码" (text-sm, font-medium, margin-bottom: 6px)
│   │           └── Input (type: password, placeholder: "再次输入新密码", w-full, rounded-xl, border, px-4, py-3, text-sm)
│   │
│   └── SaveButton (margin-top: 24px, bg-primary, text-white, rounded-xl, px-8, py-3, text-sm, font-medium, shadow-primary)
│       └── "保存更改"
```

### 3.4 通知偏好设置

```
NotificationSection
├── SectionHeader
│   ├── "通知偏好" (text-xl, font-semibold)
│   └── "选择您希望接收的通知类型和方式。" (text-sm, text-muted)
│
└── NotificationList (space-y: 16px, margin-top: 24px)
    ├── NotificationItem (flex, justify-between, align-center, py-4, border-b, border-gray-100)
    │   ├── Left (flex, align-center, gap- 12px)
    │   │   ├── IconCircle (40x40, rounded-xl, bg-primary-light, icon: message-square, w-5 h-5, text-primary)
    │   │   └── InfoStack
    │   │       ├── Title: "问诊消息" (text-sm, font-semibold)
    │   │       └── Desc: "当 AI 医生回复或需要您补充信息时通知。" (text-xs, text-muted, margin-top: 2px)
    │   └── ToggleSwitch (w-11 h-6, bg-primary, rounded-full, relative, cursor-pointer)
    │       └── Thumb (w-5 h-5, bg-white, rounded-full, absolute, right-0.5, top-0.5, shadow-sm)
    │           └── [On: translate-x-0] / [Off: translate-x-5, bg-gray-200]
    ├── NotificationItem
    │   ├── Icon: calendar (w-5 h-5, text-primary)
    │   ├── Title: "随访提醒"
    │   ├── Desc: "用药提醒、复诊日期临近时通知。"
    │   └── ToggleSwitch (on)
    ├── NotificationItem
    │   ├── Icon: shield-alert (w-5 h-5, text-primary)
    │   ├── Title: "紧急警报"
    │   ├── Desc: "系统检测到紧急情况时立即通知。"
    │   └── ToggleSwitch (on, disabled, bg-primary)
    ├── NotificationItem
    │   ├── Icon: file-text (w-5 h-5, text-primary)
    │   ├── Title: "报告更新"
    │   ├── Desc: "当新的检验报告上传或分析完成时通知。"
    │   └── ToggleSwitch (off)
    └── NotificationItem
        ├── Icon: mail (w-5 h-5, text-primary)
        ├── Title: "邮件摘要"
        ├── Desc: "每周发送健康数据摘要邮件。"
        └── ToggleSwitch (off)
```

### 3.5 语言与地区设置

```
LanguageSection
├── SectionHeader
│   ├── "语言与地区" (text-xl, font-semibold)
│   └── "选择您偏好的界面语言和地区设置。" (text-sm, text-muted)
│
└── SettingsList (space-y: 24px, margin-top: 24px)
    ├── SettingItem
    │   ├── Label: "界面语言" (text-sm, font-medium, margin-bottom: 8px)
    │   └── LanguageGrid (grid-cols-3, gap: 12px)
    │       ├── LangCard (border, rounded-xl, p-4, text-center, cursor-pointer, hover:border-primary, transition)
    │       │   ├── Flag: "🇨🇳" (text-2xl, margin-bottom: 8px) [实际使用 SVG 国旗图标]
    │       │   ├── "简体中文" (text-sm, font-medium)
    │       │   └── "中文" (text-xs, text-muted)
    │       │   └── [Selected: border-primary, bg-primary-light, ring-2, ring-primary]
    │       ├── LangCard
    │       │   ├── Flag: "🇺🇸"
    │       │   ├── "English"
    │       │   └── "英文"
    │       └── LangCard
    │           ├── Flag: "🇯🇵"
    │           ├── "日本語"
    │           └── "日文"
    │
    ├── SettingItem
    │   ├── Label: "时区" (text-sm, font-medium, margin-bottom: 8px)
    │   └── SelectDropdown (w-full, bg-gray-50, rounded-xl, border, px-4, py-3, text-sm, cursor-pointer)
    │       └── "Asia/Shanghai (UTC+8)" + icon: chevron-down (w-4 h-4, float-right, text-muted)
    │
    └── SettingItem
        ├── Label: "日期格式" (text-sm, font-medium, margin-bottom: 8px)
        └── FormatOptions (flex, gap: 12px)
            ├── FormatButton (flex-1, border, rounded-xl, py-3, text-center, text-sm, cursor-pointer)
            │   ├── "2024-06-12" (text-sm, font-medium)
            │   └── "YYYY-MM-DD" (text-xs, text-muted)
            │   └── [Selected: border-primary, bg-primary-light]
            ├── FormatButton
            │   ├── "12/06/2024"
            │   └── "DD/MM/YYYY"
            └── FormatButton
                ├── "06/12/2024"
                └── "MM/DD/YYYY"
```

### 3.6 隐私与安全设置

```
PrivacySection
├── SectionHeader
│   ├── "隐私与安全" (text-xl, font-semibold)
│   └── "管理您的数据隐私和账户安全设置。" (text-sm, text-muted)
│
└── SecurityList (space-y: 24px, margin-top: 24px)
    ├── SecurityItem (bg-gray-50, rounded-xl, p-5, flex, justify-between, align-center)
    │   ├── Left (flex, align-center, gap- 12px)
    │   │   ├── IconCircle (40x40, rounded-xl, bg-accent-light, icon: shield-check, w-5 h-5, text-accent)
    │   │   └── InfoStack
    │   │       ├── Title: "双重身份验证 (2FA)" (text-sm, font-semibold)
    │   │       └── Desc: "已开启，使用 Authenticator 应用验证。" (text-xs, text-muted, margin-top: 2px)
    │   └── StatusBadge (bg-accent-light, text-accent, rounded-full, px-3 py-1, text-xs, font-medium)
    │       └── "已开启"
    ├── SecurityItem
    │   ├── Icon: key (w-5 h-5, text-primary)
    │   ├── Title: "登录历史"
    │   ├── Desc: "查看最近的登录活动和设备。"
    │   └── Button "查看" (outline, text-sm, px-4, py-2)
    ├── SecurityItem
    │   ├── Icon: eye-off (w-5 h-5, text-primary)
    │   ├── Title: "数据匿名化"
    │   ├── Desc: "在训练数据中使用匿名化标识。"
    │   └── ToggleSwitch (on)
    ├── SecurityItem
    │   ├── Icon: download (w-5 h-5, text-primary)
    │   ├── Title: "导出个人数据"
    │   ├── Desc: "下载您的所有健康数据和问诊记录。"
    │   └── Button "导出" (outline, text-sm, px-4, py-2)
    └── DangerZone (margin-top: 32px, border-t, border-danger/20, pt-6)
        ├── SectionTitle: "危险区域" (text-base, font-semibold, text-danger, margin-bottom: 16px)
        ├── DangerItem (flex, justify-between, align-center, py-4, border-b, border-gray-100)
        │   ├── Left
        │   │   ├── Title: "清除所有健康数据" (text-sm, font-medium, text-danger)
        │   │   └── Desc: "此操作不可撤销，将删除所有问诊记录和健康档案。" (text-xs, text-muted)
        │   └── Button "清除" (outline, border-danger, text-danger, text-sm, px-4, py-2, hover:bg-danger-light)
        └── DangerItem
            ├── Title: "注销账户" (text-sm, font-medium, text-danger)
            ├── Desc: "永久删除您的账户和所有关联数据。" (text-xs, text-muted)
            └── Button "注销" (outline, border-danger, text-danger, text-sm, px-4, py-2, hover:bg-danger-light)
```

---

## 四、页面 12: 分诊与接诊页 /consultation/triage

### 4.1 页面定位

4 阶段问诊流程的第 1 阶段。患者输入症状后，Triage Agent 分析并推荐就诊科室、评估紧急程度。这是问诊流程的起点，决定后续诊断方向。

### 4.2 页面信息架构

```
ConsultationTriage Page
├── StageProgressBar (4阶段, 当前高亮第1阶段"分诊与接诊")
│   └── [同 review/analysis 页面的进度条组件]
│
├── PageHeader
│   ├── StatusBadge: "导诊护士 Agent  阶段 1/4" (text-xs, text-primary, bg-primary-light, rounded-full, px-3 py-1)
│   ├── Title: "分诊与接诊" (text-3xl, font-bold, margin-top: 12px)
│   ├── Subtitle: "请描述您的症状，AI 导诊护士将为您推荐合适的就诊科室。" (text-secondary)
│   └── PatientInfo (margin-top: 16px, flex, align-center, gap: 8px, text-sm, text-muted)
│       └── "患者: 张三  |  年龄: 34岁  |  性别: 男"
│
├── ContentGrid (grid-cols-12, gap: 20px, margin-top: 24px)
│   ├── LeftColumn (col-span-7)
│   │   └── SymptomInputCard
│   └── RightColumn (col-span-5)
│       ├── TriageResultCard (初始隐藏, 提交后显示)
│       └── QuickSymptomsCard
```

### 4.3 症状输入卡片

```
SymptomInputCard (bg-white, rounded-2xl, p-6, shadow-sm)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── Icon: message-square (w-5 h-5, text-primary)
│   └── "症状描述" (text-lg, font-semibold)
│
├── InputArea (bg-gray-50, rounded-xl, border, border-gray-200, padding: 16px, margin-bottom: 16px)
│   ├── Textarea (w-full, bg-transparent, border-none, outline-none, resize-none, min-h-32, text-sm, placeholder:text-muted, leading-relaxed)
│   │   └── Placeholder: "请详细描述您的症状，包括：
1. 症状开始时间和持续时间
2. 症状的具体表现和严重程度
3. 是否伴有其他症状
4. 既往病史和用药情况

例如：我头痛两天了，右侧太阳穴位置，搏动性疼痛，伴有恶心，无呕吐。有偏头痛病史。"
│   └── CharCount (text-right, text-xs, text-muted, margin-top: 8px)
│       └── "0 / 500"
│
├── AttachmentRow (flex, align-center, gap: 12px, margin-bottom: 16px)
│   ├── AttachmentButton (flex, align-center, gap: 6px, text-sm, text-muted, hover:text-primary, cursor-pointer)
│   │   ├── Icon: paperclip (w-4 h-4)
│   │   └── "添加附件 (检验报告、影像资料)"
│   └── FileList (flex, gap: 8px, flex-wrap)
│       └── FileChip (bg-primary-light, text-primary, rounded-full, px-3, py-1, text-xs, flex, align-center, gap: 4px)
│           ├── "血常规报告.pdf"
│           └── Icon: x (w-3 h-3, cursor-pointer)
│
├── VoiceInputRow (flex, align-center, gap: 12px, margin-bottom: 16px)
│   └── VoiceButton (flex, align-center, gap: 6px, text-sm, text-muted, hover:text-primary, cursor-pointer)
│       ├── Icon: mic (w-4 h-4)
│       └── "语音输入"
│
└── SubmitButton (w-full, bg-primary, text-white, rounded-xl, py-3, text-sm, font-medium, shadow-primary, hover:bg-primary-hover, disabled:opacity-50)
    └── "提交症状，开始分诊"
```

### 4.4 分诊结果卡片

```
TriageResultCard (bg-white, rounded-2xl, p-6, shadow-sm, border, border-primary, animate-fade-in-up)
├── ResultHeader (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── Icon: stethoscope (w-5 h-5, text-primary)
│   └── "分诊结果" (text-lg, font-semibold)
│
├── DepartmentRecommendation (bg-primary-light, rounded-xl, p-4, margin-bottom: 16px)
│   ├── Label: "推荐科室" (text-xs, text-primary, font-medium, margin-bottom: 4px)
│   └── DepartmentName: "神经内科" (text-xl, font-bold, text-primary)
│
├── PriorityAssessment (margin-bottom: 16px)
│   ├── Label: "紧急程度评估" (text-sm, font-medium, margin-bottom: 8px)
│   └── PriorityBar (h-3, bg-gray-200, rounded-full, overflow-hidden, position: relative)
│       ├── Segments (flex, h-full)
│       │   ├── Segment1 (flex-1, bg-accent, rounded-l-full) "低"
│       │   ├── Segment2 (flex-1, bg-primary) "中"
│       │   ├── Segment3 (flex-1, bg-warning) "高"
│       │   └── Segment4 (flex-1, bg-danger, rounded-r-full) "紧急"
│       └── Indicator (absolute, top-0, w-1, h-full, bg-white, shadow, transform, translate-x-[150%]) [根据评估结果定位]
│   └── PriorityLabel (text-center, margin-top: 8px, text-sm, font-medium, text-primary)
│       └── "中等优先级 - 建议24小时内就诊"
│
├── SymptomAnalysis (margin-bottom: 16px)
│   ├── Label: "症状分析" (text-sm, font-medium, margin-bottom: 8px)
│   └── AnalysisList (space-y: 6px)
│       ├── AnalysisItem (flex, align-center, gap: 6px, text-sm, text-secondary)
│       │   ├── Icon: check (w-4 h-4, text-accent)
│       │   └── "检测到搏动性头痛特征，符合偏头痛模式"
│       ├── AnalysisItem
│       │   ├── Icon: check (w-4 h-4, text-accent)
│       │   └── "恶心症状提示前庭系统可能受累"
│       └── AnalysisItem
│           ├── Icon: alert-circle (w-4 h-4, text-warning)
│           └── "建议排除颅内压增高风险"
│
├── RiskFlags (margin-bottom: 16px)
│   ├── Label: "风险标记" (text-sm, font-medium, margin-bottom: 8px)
│   └── RiskTags (flex, flex-wrap, gap: 8px)
│       └── RiskTag (bg-warning-light, text-warning, rounded-full, px-3, py-1, text-xs)
│           └── "需神经科专科评估"
│
└── ActionButtons (flex, gap: 12px)
    ├── Button "重新描述" (flex-1, outline, text-sm, py-2.5, rounded-xl)
    └── Button "进入诊断" (flex-1, bg-primary, text-white, text-sm, py-2.5, rounded-xl, shadow-primary)
        └── "进入诊断 →"
```

### 4.5 快速症状选择卡片

```
QuickSymptomsCard (bg-white, rounded-2xl, p-6, shadow-sm, margin-top: 16px)
├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│   ├── Icon: zap (w-5 h-5, text-primary)
│   └── "快速症状选择" (text-lg, font-semibold)
│
├── SymptomCategories (space-y: 16px)
│   ├── Category
│   │   ├── CategoryLabel: "头部" (text-xs, text-muted, uppercase, tracking-wider, margin-bottom: 8px)
│   │   └── SymptomTags (flex, flex-wrap, gap: 8px)
│   │       ├── SymptomTag (border, rounded-full, px-3, py-1.5, text-sm, text-secondary, cursor-pointer, hover:border-primary, hover:text-primary, transition)
│   │       │   └── "头痛"
│   │       ├── SymptomTag
│   │       │   └── "头晕"
│   │       ├── SymptomTag
│   │       │   └── "恶心"
│   │       └── SymptomTag
│   │           └── "视力模糊"
│   ├── Category
│   │   ├── CategoryLabel: "胸部"
│   │   └── SymptomTags
│   │       ├── SymptomTag: "胸痛"
│   │       ├── SymptomTag: "心悸"
│   │       ├── SymptomTag: "呼吸困难"
│   │       └── SymptomTag: "咳嗽"
│   └── Category
│       ├── CategoryLabel: "腹部"
│       └── SymptomTags
│           ├── SymptomTag: "腹痛"
│           ├── SymptomTag: "腹泻"
│           ├── SymptomTag: "便秘"
│           └── SymptomTag: "恶心呕吐"
│
└── SelectedSymptoms (margin-top: 16px, padding-top: 16px, border-t, border-gray-100)
    ├── Label: "已选症状:" (text-sm, text-muted, margin-bottom: 8px)
    └── SelectedTags (flex, flex-wrap, gap: 8px)
        └── SelectedTag (bg-primary, text-white, rounded-full, px-3, py-1.5, text-sm, flex, align-center, gap: 4px)
            ├── "头痛"
            └── Icon: x (w-3 h-3, cursor-pointer)
```

---

## 五、页面 13: 上传新报告页 /reports/new

### 5.1 页面定位

从健康记录页"上传新报告"按钮进入。支持上传检验报告、影像资料、处方单等医疗文件，OCR 自动识别内容，AI 解析并归档到健康记录中。

### 5.2 页面信息架构

```
UploadReport Page
├── PageHeader
│   ├── Title: "上传新报告" (text-3xl, font-bold)
│   ├── Subtitle: "上传检验报告、影像资料或处方单，AI 将自动解析并归档。" (text-secondary)
│   └── BackButton (icon: arrow-left, text-sm, text-muted, hover:text-primary)
│       └── "返回健康记录"
│
├── UploadArea (margin-top: 24px, bg-white, rounded-2xl, p-8, shadow-sm, border, border-dashed, border-gray-300, hover:border-primary, transition, cursor-pointer)
│   ├── UploadContent (text-center, padding: 40px 0)
│   │   ├── UploadIcon (w-16 h-16, mx-auto, rounded-full, bg-primary-light, flex, items-center, justify-center, margin-bottom: 16px)
│   │   │   └── icon: upload-cloud (w-8 h-8, text-primary)
│   │   ├── Title: "拖放文件到此处，或点击上传" (text-lg, font-semibold, text-primary, margin-bottom: 8px)
│   │   ├── Description (text-sm, text-muted, margin-bottom: 16px)
│   │   │   └── "支持 PDF、JPG、PNG、DICOM 格式，单个文件不超过 50MB"
│   │   └── UploadButton (bg-primary, text-white, rounded-xl, px-6, py-2.5, text-sm, font-medium, shadow-primary)
│   │       └── "选择文件"
│   └── FileTypesRow (flex, justify-center, gap: 24px, margin-top: 24px)
│       ├── FileType (text-center)
│       │   ├── Icon: file-text (w-6 h-6, mx-auto, text-muted, margin-bottom: 4px)
│       │   └── "检验报告" (text-xs, text-muted)
│       ├── FileType
│       │   ├── Icon: image (w-6 h-6, mx-auto, text-muted)
│       │   └── "影像资料" (text-xs, text-muted)
│       └── FileType
│           ├── Icon: pill (w-6 h-6, mx-auto, text-muted)
│           └── "处方单" (text-xs, text-muted)
│
├── UploadProgressSection (margin-top: 24px, hidden initially)
│   └── UploadProgressCard (bg-white, rounded-2xl, p-6, shadow-sm)
│       ├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│       │   ├── "正在上传" (text-lg, font-semibold)
│       │   └── Status: "75%" (text-sm, text-primary, font-medium)
│       ├── ProgressBar (h-2, bg-gray-200, rounded-full, margin-bottom: 12px)
│       │   └── Fill (h-full, bg-primary, rounded-full, width: 75%, transition-all, duration-300)
│       └── FileInfo (flex, align-center, gap: 12px)
│           ├── FileIcon (w-10 h-10, rounded-lg, bg-primary-light, flex, items-center, justify-center)
│           │   └── icon: file-text (w-5 h-5, text-primary)
│           └── FileDetails
│               ├── FileName: "血常规报告_20240612.pdf" (text-sm, font-medium)
│               └── FileSize: "2.3 MB" (text-xs, text-muted)
│
├── OCRProcessingSection (margin-top: 24px, hidden initially)
│   └── OCRProgressCard (bg-white, rounded-2xl, p-6, shadow-sm, border, border-primary)
│       ├── Header (flex, align-center, gap: 8px, margin-bottom: 16px)
│       │   ├── Icon: sparkle (w-5 h-5, text-primary, animate-spin)
│       │   └── "AI 正在解析报告内容..." (text-lg, font-semibold)
│       ├── ProcessingSteps (space-y: 12px)
│       │   ├── Step (flex, align-center, gap- 12px)
│       │   │   ├── StepIcon (w-6 h-6, rounded-full, bg-accent, flex, items-center, justify-center)
│       │   │   │   └── icon: check (w-3 h-3, text-white)
│       │   │   └── StepText (text-sm, text-secondary)
│       │   │       └── "文件上传完成"
│       │   ├── Step
│       │   │   ├── StepIcon (w-6 h-6, rounded-full, bg-accent, flex, items-center, justify-center)
│       │   │   │   └── icon: check (w-3 h-3, text-white)
│       │   │   └── "OCR 文字识别完成"
│       │   ├── Step
│       │   │   ├── StepIcon (w-6 h-6, rounded-full, bg-primary, flex, items-center, justify-center, animate-pulse)
│       │   │   │   └── icon: loader (w-3 h-3, text-white, animate-spin)
│       │   │   └── "AI 结构化解析中..." (text-sm, text-primary, font-medium)
│       │   └── Step
│       │       ├── StepIcon (w-6 h-6, rounded-full, bg-gray-200, flex, items-center, justify-center)
│       │       │   └── "4"
│       │       └── "数据归档" (text-sm, text-muted)
│       └── CancelButton (margin-top: 16px, text-sm, text-danger, hover:underline, cursor-pointer)
│           └── "取消解析"
│
├── PreviewSection (margin-top: 24px, hidden initially)
│   └── PreviewCard (bg-white, rounded-2xl, p-6, shadow-sm)
│       ├── Header (flex, justify-between, align-center, margin-bottom: 16px)
│       │   ├── "解析结果预览" (text-lg, font-semibold)
│       │   └── ConfidenceBadge (bg-accent-light, text-accent, rounded-full, px-3, py-1, text-xs, font-medium)
│       │       └── "识别置信度 96%"
│       ├── PreviewContent (bg-gray-50, rounded-xl, p-4, margin-bottom: 16px)
│       │   ├── ReportType (text-sm, text-muted, margin-bottom: 8px)
│       │   │   └── "报告类型: 血常规 (CBC)"
│       │   ├── DataGrid (grid-cols-2, gap- 12px)
│       │   │   ├── DataItem
│       │   │   │   ├── Label: "白细胞计数" (text-xs, text-muted)
│       │   │   │   └── Value: "6.5 x10^9/L" (text-sm, font-medium)
│       │   │   │   └── Reference: "参考: 4.0-10.0" (text-xs, text-accent)
│       │   │   ├── DataItem
│       │   │   │   ├── Label: "红细胞计数" (text-xs, text-muted)
│       │   │   │   └── Value: "4.2 x10^12/L" (text-sm, font-medium)
│       │   │   │   └── Reference: "参考: 4.0-5.5" (text-xs, text-accent)
│       │   │   ├── DataItem
│       │   │   │   ├── Label: "血红蛋白" (text-xs, text-muted)
│       │   │   │   └── Value: "135 g/L" (text-sm, font-medium)
│       │   │   │   └── Reference: "参考: 120-160" (text-xs, text-accent)
│       │   │   └── DataItem
│       │   │       ├── Label: "血小板计数" (text-xs, text-muted)
│       │   │       └── Value: "250 x10^9/L" (text-sm, font-medium)
│       │   │       └── Reference: "参考: 100-300" (text-xs, text-accent)
│       │   └── AIComment (margin-top: 12px, bg-primary-light, rounded-lg, p-3, flex, gap- 8px)
│       │       ├── Icon: sparkle (w-4 h-4, text-primary, flex-shrink-0, margin-top: 2px)
│       │       └── "所有指标均在正常范围内，无异常发现。" (text-xs, text-primary)
│       └── ActionButtons (flex, gap: 12px)
│           ├── Button "重新上传" (flex-1, outline, text-sm, py-2.5, rounded-xl)
│           └── Button "确认归档" (flex-1, bg-primary, text-white, text-sm, py-2.5, rounded-xl, shadow-primary)
│               └── "确认归档"
│
└── TipsSection (margin-top: 24px, margin-bottom: 40px, bg-primary-light, rounded-2xl, p-5, flex, gap- 12px)
    ├── Icon: lightbulb (w-5 h-5, text-primary, flex-shrink-0, margin-top: 2px)
    └── TipsContent
        ├── Title: "上传提示" (text-sm, font-semibold, text-primary, margin-bottom: 4px)
        └── TipsList (text-xs, text-primary/80, space-y: 2px)
            ├── "• 请确保文件清晰可读，避免反光或阴影"
            ├── "• 建议上传原始 PDF 文件以获得最佳识别效果"
            └── "• 涉及隐私信息已自动脱敏处理"
```

---

## 六、全局交互补充

### 6.1 页面切换过渡

```typescript
// 页面间切换动画
const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: { duration: 0.2, ease: 'easeOut' }
};
```

### 6.2 加载状态规范

| 场景 | 加载方式 | 时长 | 样式 |
|------|---------|------|------|
| 页面初始化 | 骨架屏 | 不定 | 灰色脉冲块 |
| 数据获取 | 旋转图标 + 文字 | 不定 | 居中显示 |
| 文件上传 | 进度条 | 实时 | 百分比 + 速度 |
| AI 解析 | 步骤指示器 | 不定 | 逐步完成动画 |
| 表单提交 | 按钮加载态 | 不定 | 按钮内旋转图标 |
| 搜索 | 输入框加载 | 不定 | 输入框右侧旋转图标 |

### 6.3 错误处理规范

| 错误类型 | 展示方式 | 操作按钮 |
|---------|---------|---------|
| 网络错误 | Toast 通知 + 重试按钮 | "重试" |
| 权限不足 | 模态框提示 | "返回首页" / "联系管理员" |
| 数据加载失败 | 页面内错误状态 | "重新加载" |
| 表单验证错误 | 字段级红色提示 | "修正后重试" |
| 文件上传失败 | 上传区域错误提示 | "重新上传" |
| AI 服务超时 | 步骤指示器错误态 | "重试解析" / "跳过" |

### 6.4 新增 Mock 数据

```typescript
// 患者列表数据
export const mockPatients = [
  { id: '4092', name: '张三', avatar: '张', age: 34, gender: '男', stage: 'review', stageLabel: '评估复核', symptoms: '头痛、发热、心悸，持续3天', priority: 'normal', lastUpdate: '10分钟前' },
  { id: '4091', name: '李四', avatar: '李', age: 28, gender: '女', stage: 'triage', stageLabel: '分诊与接诊', symptoms: '皮疹、瘙痒，面部红肿', priority: 'normal', lastUpdate: '1小时前' },
  { id: '4090', name: '王五', avatar: '王', age: 56, gender: '男', stage: 'diagnosis', stageLabel: '诊断映射', symptoms: '胸痛、呼吸困难，活动后加重', priority: 'emergency', lastUpdate: '30分钟前' },
  { id: '4089', name: '赵六', avatar: '赵', age: 42, gender: '女', stage: 'complete', stageLabel: '已完成', symptoms: '腹痛、腹泻，伴有低热', priority: 'normal', lastUpdate: '2小时前' },
];

// 系统状态数据
export const mockSystemStatus = {
  overall: 'healthy', // healthy | warning | critical
  services: [
    { name: '用户认证服务', endpoint: '/api/v1/auth', status: 'healthy', latency: '12ms', uptime: '99.9%' },
    { name: '问诊会话服务', endpoint: '/api/v1/consult', status: 'healthy', latency: '28ms', uptime: '99.8%' },
    { name: '健康记录服务', endpoint: '/api/v1/records', status: 'healthy', latency: '15ms', uptime: '99.9%' },
    { name: 'WebSocket 服务', endpoint: '/ws', status: 'healthy', latency: '8ms', uptime: '99.7%' },
    { name: 'OCR 识别服务', endpoint: '/api/v1/ocr', status: 'healthy', latency: '145ms', uptime: '99.5%' },
    { name: '报告解析服务', endpoint: '/api/v1/parse', status: 'warning', latency: '2.3s', uptime: '98.2%' },
  ],
  models: [
    { name: 'Triage Agent', version: 'v2.1.0', status: 'healthy', load: 45 },
    { name: 'Doctor Agent', version: 'v3.0.2', status: 'healthy', load: 72 },
    { name: 'Review Agent', version: 'v2.0.1', status: 'healthy', load: 28 },
    { name: 'Follow-up Agent', version: 'v1.5.0', status: 'warning', load: 0, message: '模型加载超时，正在重试...' },
  ],
  database: { connections: '8/20', latency: '4.2ms', storage: '67%', activeSessions: 142 },
  incidents: [
    { id: '1', type: 'info', message: 'API 服务自动扩容完成', time: '2小时前' },
    { id: '2', type: 'warning', message: 'Follow-up Agent 模型响应超时，已自动重启', time: '5小时前' },
    { id: '3', type: 'info', message: '系统版本更新至 v1.2.0', time: '1天前' },
    { id: '4', type: 'error', message: '数据库连接池短暂耗尽，已自动恢复', time: '3天前' },
  ],
};

// 分诊结果数据
export const mockTriageResult = {
  recommendedDepartment: '神经内科',
  priority: 'medium', // low | medium | high | emergency
  priorityLabel: '中等优先级 - 建议24小时内就诊',
  analysis: [
    '检测到搏动性头痛特征，符合偏头痛模式',
    '恶心症状提示前庭系统可能受累',
    '建议排除颅内压增高风险',
  ],
  riskFlags: ['需神经科专科评估'],
  confidence: 78,
};

// 上传报告解析结果
export const mockOCRResult = {
  reportType: '血常规 (CBC)',
  confidence: 96,
  data: [
    { label: '白细胞计数', value: '6.5 x10^9/L', reference: '4.0-10.0', status: 'normal' },
    { label: '红细胞计数', value: '4.2 x10^12/L', reference: '4.0-5.5', status: 'normal' },
    { label: '血红蛋白', value: '135 g/L', reference: '120-160', status: 'normal' },
    { label: '血小板计数', value: '250 x10^9/L', reference: '100-300', status: 'normal' },
  ],
  aiComment: '所有指标均在正常范围内，无异常发现。',
};
```

---

> **Part 2 结束**  
> 覆盖 5 个高优先级页面：患者管理列表页、系统状态页、设置页、分诊与接诊页、上传新报告页。  
> 包含完整的组件层级、交互规范、状态管理和 Mock 数据。
