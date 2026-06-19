---
name: week6-learning-resources
description: W6 前端完整产品——React/Next.js 组件体系、Tailwind CSS 布局、WebSocket 流式渲染
metadata:
  type: reference
---

# MediNexus W6 技术栈学习指南

> 本文档列出了第 6 周前端完整产品开发中用到的所有技术，适合新手按顺序学习。

---

## 一、项目前端架构

### 整体结构

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router 页面
│   │   ├── layout.tsx          # 全局布局 (NavBar)
│   │   ├── page.tsx            # 首页 (Hero + 功能卡片)
│   │   ├── consultation/       # 问诊对话页
│   │   ├── records/            # 就诊记录页
│   │   └── profile/            # 个人中心页
│   │
│   ├── components/             # 可复用 UI 组件
│   │   ├── chat/               # 对话相关
│   │   │   ├── ChatContainer   # 对话容器 (消息管理)
│   │   │   ├── ChatMessage     # 消息气泡 (流式渲染)
│   │   │   └── ChatInput       # 输入框 (自动缩放)
│   │   └── ui/                 # 通用 UI (W6 新增)
│   │       ├── NavBar          # 导航栏
│   │       ├── DisclaimerBanner # 医疗免责声明
│   │       ├── LoadingState    # 加载态
│   │       ├── ErrorState      # 错误态
│   │       └── EmptyState      # 空态
│   │
│   ├── lib/                    # 工具库
│   │   ├── api.ts              # REST API 客户端
│   │   └── websocket.ts        # WebSocket 客户端 (含重连)
│   │
│   └── stores/                 # 状态管理 (预留)
│       └── consultationStore.ts
│
├── tailwind.config.js
├── next.config.js              # API 代理 /api → localhost:8000
└── tsconfig.json               # @/ → ./src/ 路径别名
```

---

## 二、Next.js 14 App Router

### 1. 页面与路由

| 路由 | 文件 | 内容 |
|------|------|------|
| `/` | `app/page.tsx` | 首页，Hero + 6 功能卡片 |
| `/consultation` | `app/consultation/page.tsx` | 流式问诊对话 |
| `/records` | `app/records/page.tsx` | SOAP 病历时间线 |
| `/profile` | `app/profile/page.tsx` | 健康档案 + 编辑 |

每个文件以 `"use client"` 开头，表示客户端组件（需要 `useState`/`useEffect`）。

**新手学习重点:**
- App Router 的**文件即路由**原则 (`app/records/` → `/records`)
- `layout.tsx` 是**共享布局**，包裹所有子页面
- `"use client"` vs 服务端组件

**官方文档:** https://nextjs.org/docs/app

---

## 三、UI 组件体系

### 2. 状态组件 (W6 新增)

每个页面必须覆盖 3 种状态:

| 组件 | 用途 | 触发条件 |
|------|------|---------|
| **LoadingState** | 数据加载中 | `useEffect` → `setTimeout` / API call |
| **ErrorState** | 加载失败 | `catch` / API error |
| **EmptyState** | 数据为空 | `records.length === 0` |

**使用模式:**
```tsx
if (loading) return <LoadingState message="加载中..." />;
if (error) return <ErrorState message={error} onRetry={refetch} />;
if (items.length === 0) return <EmptyState icon="📋" title="暂无数据" actionLabel="开始" actionHref="/consultation" />;
return <ActualContent />;
```

### 3. 导航栏 (NavBar)

```tsx
const navItems = [
  { href: "/", label: "首页", icon: "🏠" },
  { href: "/consultation", label: "智能问诊", icon: "💬" },
  { href: "/records", label: "就诊记录", icon: "📋" },
  { href: "/profile", label: "个人中心", icon: "👤" },
];
```

- 使用 `usePathname()` 高亮当前页面
- `sticky top-0` 固定在顶部
- `hidden sm:block` 在手机上隐藏文字，只显示图标

### 4. 免责声明 (DisclaimerBanner)

两种模式:

| 模式 | 样式 | 内容 |
|------|------|------|
| `standard` | 琥珀色背景 | "AI 生成仅供参考，不构成医疗建议" |
| `emergency` | 红色背景，脉冲动画 | "🚨 检测到紧急情况，请立即拨打 120" |

---

## 四、Tailwind CSS 布局技巧

### 5. 本项目使用的关键类

| 类 | 用途 | 示例 |
|----|------|------|
| `min-h-screen` | 全屏高度 | `min-h-screen bg-gray-50` |
| `h-[calc(100vh-56px)]` | 减去导航栏高度 | 问诊页全高 |
| `flex-col` | 垂直排列 | 聊天布局 |
| `max-w-3xl mx-auto` | 内容居中 | 病历列表 |
| `grid md:grid-cols-3 gap-5` | 响应式网格 | 首页功能卡片 |
| `sticky top-0 z-50` | 固定顶部 | 导航栏 |
| `animate-bounce` | 弹跳动画 | 加载指示器 |
| `animate-pulse` | 脉冲动画 | 紧急标记 |
| `transition-colors` | 颜色过渡 | 悬停效果 |
| `space-y-4` | 子元素间距 | 卡片列表 |

### 6. 响应式设计

```
移动端 (<768px):    单列布局，导航栏仅图标
平板/桌面 (≥768px): 多列网格，导航栏图文

典型断点:
  sm: 640px    — 隐藏文字
  md: 768px    — 两列/三列网格
  lg: 1024px   — 大间距
```

---

## 五、WebSocket 流式渲染

### 7. 事件类型 (6 种)

```typescript
type WsEventType =
  | "agent_start"   // Agent 开始处理
  | "token"         // 逐字输出
  | "agent_end"     // 处理完成
  | "error"         // 错误
  | "info"          // 系统消息
  | "emergency";    // 🚨 紧急情况 (W6 新增)
```

### 8. ChatContainer 消息流

```
用户输入 → socket.send({type:"message", content})
              │
              ▼
服务器返回 agent_start → token → token → ... → agent_end
              │         │                      │
              ▼         ▼                      ▼
          创建新消息  追加内容              结束流式标记
          显示 Agent  逐字渲染              显示光标
          标签                               完成态
```

### 9. 流式渲染效果 (ChatMessage)

```tsx
// 每 30ms 追加 3 个字符的模拟流式效果
useEffect(() => {
  if (!streaming || !content) return;
  let i = 0;
  const interval = setInterval(() => {
    i += 3;
    setDisplayedContent(content.slice(0, i));
    if (i >= content.length) clearInterval(interval);
  }, 30);
  return () => clearInterval(interval);
}, [content, streaming]);
```

---

## 六、API 客户端

### 10. REST 端点

| 函数 | 端点 | 用途 |
|------|------|------|
| `startConsultation()` | `POST /consult` | 新建会话 |
| `getConsultation()` | `GET /consult/{id}` | 查询状态 |
| `completeConsultation()` | `POST /consult/{id}/complete` | 提交 SOAP |
| `getConsultationHistory()` | `GET /consult/{id}/history` | 历史记录 |
| `healthCheck()` | `GET /health` | 健康检查 |

API 代理配置 (`next.config.js`):
```js
// 前端 /api/* → 后端 http://localhost:8000/api/v1/*
async rewrites() {
  return [{ source: "/api/:path*", destination: "http://localhost:8000/api/v1/:path*" }];
}
```

---

## 七、页面详解

### 11. 首页 (`/`)

```
Hero:   标题 + 描述 + CTA 按钮 → /consultation
        版本标签 (v0.1.0)
下方:   3×2 功能卡片网格 (6 个 feature)
页脚:   项目信息 + 免责声明
```

### 12. 问诊页 (`/consultation`)

两个阶段: `chat` (对话中) → `summary` (完成总结)

```
对话阶段:
  ├── 顶部: 标题 + 会话ID + 紧急标记 + 完成按钮
  ├── 中间: ChatContainer (消息列表)
  └── 底部: 免责声明条 (首次响应后出现)

完成阶段:
  ├── 完成确认卡片
  ├── 会话信息卡
  ├── 免责声明
  └── 返回对话链接
```

紧急标记逻辑:
```tsx
socket.on("emergency", () => setIsEmergency(true));
```
一旦触发:
- 🚨 红色脉冲标记出现在顶部
- `DisclaimerBanner` 切换为 `emergency` 模式 (急救指引)

### 13. 病历页 (`/records`)

```
加载中: LoadingState (~
600ms mock)
加载失败: ErrorState (消息 + 重试)
空数据: EmptyState → "开始问诊" 按钮
有数据: 可展开卡片列表
          └── 点击展开 → SOAP 字段详情
```

SOAP 展示:
```tsx
<SOAPField label="主诉 (Subjective)" value={record.subjective} />
<SOAPField label="查体 (Objective)"   value={record.objective} />
<SOAPField label="诊断 (Assessment)"  value={record.assessment} />
<SOAPField label="方案 (Plan)"        value={record.plan} />
```

### 14. 个人中心 (`/profile`)

```
顶部: 头像 + 姓名 + 编辑模式切换
中部: 健康档案 (过敏史/既往史/长期用药)
底部: 快速入口 (病历 / 咨询)
```

编辑模式:
```tsx
<button onClick={() => editing ? handleSave() : setEditing(true)}>
  {editing ? "保存" : "编辑"}
</button>
```

---

## 八、Mock 数据策略

开发阶段各页面使用 Mock 数据模拟后端返回:

| 页面 | Mock 数据 | 延迟 |
|------|-----------|------|
| Records | `MOCK_RECORDS` (2 条 SOAP 记录) | 600ms |
| Profile | `MOCK_PROFILE` (患者档案) | 400ms |

```tsx
// Mock 数据在 API 就绪后替换为真实调用
useEffect(() => {
  const timer = setTimeout(() => {
    setRecords(MOCK_RECORDS);
    setLoading(false);
  }, 600);
  return () => clearTimeout(timer);
}, []);
```

---

## 九、关键命令

```bash
# 安装依赖
cd frontend && npm install

# 开发模式 (默认端口 3000)
cd frontend && npm run dev

# 生产构建
cd frontend && npm run build

# 预览生产构建
cd frontend && npm start
```

---

## 十、常见问题

### Q: 为什么用 `"use client"` 而不是 Next.js 服务端组件?

**A:** 问诊页需要 `useState`(消息列表)、`useEffect`(WebSocket 绑定)、`useCallback`(发送函数)等客户端 Hook，必须声明为客户端组件。首页其实可以是服务端组件，但为了保持一致性也加了。

### Q: 3 态组件 (Loading/Error/Empty) 必须每个页面都加吗?

**A:** 是的。W6 的设计原则是「状态覆盖完整性」——用户在任何页面都不应该看到白屏或未定义状态。每个页面必须处理: 加载中、加载失败、数据为空、有数据 4 种状态。

### Q: 免责声明放在哪里? 每次都显示吗?

**A:** 问诊页: 首次 Agent 响应后显示，出现在消息列表底部和输入框之间。总结页: 每次显示。紧急情况: 切换为红色急救模式。

### Q: 没有后端时前端能跑起来吗?

**A:** 能。但问诊页的 WebSocket 连接会失败（自动重试 3 次），病历页和个人中心使用 Mock 数据。要完整体验请启动后端。
