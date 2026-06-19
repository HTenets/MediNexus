# MediNexus 前端设计参考文档

> 此文档作为前端开发的唯一真相来源 (Single Source of Truth)，包含设计语言、技术栈、页面清单、功能列表、API 接口和组件目录。可作 AI 提示词使用。

---

## 一、项目背景

**MediNexus（医枢）** 是一个开源的 AI 多智能体医疗诊断平台。用户（患者）输入症状描述，系统通过 **多 Agent 协作**（Triage 导诊 → Doctor 诊断 → Review 审查 → Follow-up 随访）提供 AI 辅助医疗咨询。

- **定位:** 患者自助问诊，参考级准确度（非临床级）
- **目标用户:** 普通患者（非医生）
- **语言:** 中文为主，英文备用
- **LLM 策略:** Ollama 本地模型默认 + 用户 BYO Key 增强
- **准确度:** 基于三路知识库（临床病例 0.8 / 医学理论 0.6 / 最新论文 0.3）
- **部署:** 自托管，数据不出设备，支持 Docker Compose 一键启动

**核心理念:** 让专业医疗知识触手可及，但始终明确"不构成医疗诊断建议"。

---

## 二、设计语言 (Design System)

### 2.1 设计风格

- **风格:** Accessible & Ethical — 高对比度、大字体、键盘可导航、WCAG AA 合规
- **审美:** 现代医疗诊所风格 — 干净、专业、可信赖、温暖但不花哨
- **布局:** Bento Grid 卡片系统 + Minimal Single Column 内容区
- **参考:** 可参考 Clyhealth Dashboard 等现代医疗平台设计

### 2.2 颜色系统

| 用途 | 色值 | Tailwind 类名 | 说明 |
|------|------|--------------|------|
| 主色 Primary | `#0891B2` | `bg-medical-primary` | 医用青蓝色，用于主按钮、链接、强调 |
| 主色 Hover | `#0E7490` | `bg-medical-primary-hover` | 按钮悬停态 |
| 次色 Secondary | `#22D3EE` | - | 渐变色辅助 |
| 强调色 Accent | `#16A34A` | `text-medical-accent` | 健康绿，用于成功状态、完成标记 |
| 背景 Background | `#F0FDFA` | `bg-medical-bg` | 浅青背景 |
| 前景 Foreground | `#134E4A` | `text-medical-fg` | 深青文字 |
| 静音 Muted | `#E8F1F6` | `bg-medical-muted` | 次要背景/面板 |
| 静音文字 | `#64748B` | `text-medical-muted-fg` | 次要文字 |
| 边框 Border | `#CCFBF1` | `border-medical-border` | 卡片/输入框边框 |
| 破坏色 Destructive | `#DC2626` | `text-red-600` | 错误/紧急状态 |
| 白色卡片 | `#FFFFFF` | `bg-white` | 卡片背景 |
| Ring 聚焦环 | `#0891B2` | `ring-medical-primary` | 聚焦状态 |

### 2.3 字体系统

| 用途 | 字体 | 备选 | CSS |
|------|------|------|-----|
| 标题 (H1-H6) | Figtree | system-ui, sans-serif | `font-family: 'Figtree', system-ui, sans-serif` |
| 正文 (Body) | Noto Sans | system-ui, sans-serif | `font-family: 'Noto Sans', system-ui, sans-serif` |
| 代码/等宽 (Mono) | JetBrains Mono | monospace | `font-family: 'JetBrains Mono', monospace` |

Google Fonts 导入:
```
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&family=Noto+Sans:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
```

**字体层级:**
- H1: `text-4xl md:text-6xl font-bold tracking-tight`
- H2: `text-3xl font-bold`
- H3: `text-lg font-semibold` / `text-sm font-semibold`
- Body: `text-sm` / `text-base` leading-relaxed
- Caption: `text-xs`
- 等宽: `text-xs font-mono`（用于 ID、代码片段）

### 2.4 间距系统

使用 4pt/8dp 增量:
- 组件内 padding: `p-3` (12px), `p-4` (16px), `p-6` (24px)
- 卡片间距: `gap-4` (16px), `gap-5` (20px), `space-y-4`
- 区块间距: `py-8` (32px), `py-16` (64px), `py-20` (80px)
- 导航高度: `h-14` (56px)

### 2.5 圆角与阴影

- 输入框/小按钮: `rounded-xl` (12px)
- 图标容器: `rounded-xl` (12px)
- 卡片: `rounded-2xl` (16px)
- 大图标容器: `rounded-2xl` (16px)
- 消息气泡: `rounded-2xl` (16px)，用户气泡 `rounded-br-sm`，AI 气泡 `rounded-bl-sm`
- 标签/徽章: `rounded-full`
- 卡片阴影: `shadow-sm`(默认) → `shadow-md`(悬停)
- 主按钮阴影: `shadow-sm shadow-medical-primary/20`

### 2.6 动画和过渡

- 微交互: `transition-all duration-200` / `transition-colors duration-200`
- 按钮 active: `active:scale-[0.98]`
- 加载点: `animate-bounce` + staggered delay（0ms / 150ms / 300ms）
- 脉冲: `animate-pulse`（紧急标记、流式光标）
- 淡入: `animate-in fade-in duration-200`
- 旋转: `transition-transform duration-200`（折叠箭头 `rotate-180`）

### 2.7 图标规范

- **必须使用 SVG 图标**，禁止 emoji 作为功能性图标
- 图标来源: 自建 `icons.tsx` (手写 SVG path)，风格参考 Lucide icons
- 笔画宽度: `strokeWidth="1.5"`，线帽: `round`，线连接: `round`
- 颜色: `stroke="currentColor"` 继承文本色
- 尺寸: `w-4 h-4`(导航), `w-5 h-5`(按钮/卡片), `w-6 h-6`(大图标), `w-7 h-7`(特大)

### 2.8 交互状态

- **聚焦:** `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-medical-primary focus-visible:ring-offset-2`
- **悬停:** 按钮变色 / 卡片阴影提升 / 链接下划线
- **禁用:** `opacity-50 cursor-not-allowed`
- **加载:** 圆点弹跳动画 / 骨架屏
- **错误:** 红色边框 + 错误消息文本

### 2.9 无障碍要求

- 所有可交互元素: `cursor-pointer`
- 仅图标按钮: `aria-label="描述"`
- 表单输入: 始终有可见 label
- 颜色对比度: AA 级（正文 4.5:1，大文字 3:1）
- 支持键盘导航（Tab 顺序）
- 支持 `prefers-reduced-motion`

---

## 三、技术栈

| 层 | 技术 | 版本 | 用途 |
|----|------|------|------|
| 框架 | Next.js | 14 | React 框架，App Router |
| UI | React | 18 | 组件库 |
| 样式 | Tailwind CSS | 3 | 原子化 CSS |
| 图标 | 自建 SVG | — | `src/components/ui/icons.tsx` |
| 状态 | React useState/useEffect | — | 组件内状态 |
| WebSocket | 浏览器原生 API | — | 流式对话 |
| 语言 | TypeScript | 5 | 类型安全 |
| 构建 | Webpack (Next.js 内置) | — | 构建打包 |
| 字体 | Google Fonts (Figtree, Noto Sans, JetBrains Mono) | — | 通过 CSS @import |

**依赖项:**
```json
{
  "next": "^14",
  "react": "^18",
  "react-dom": "^18",
  "tailwindcss": "^3",
  "autoprefixer": "^10"
}
```

**配置文件:**
- `next.config.js` — API 代理 `/api/*` → `http://localhost:8000/api/v1/*`
- `tailwind.config.js` — 自定义颜色 (medical-*)，自定义字体 (heading/body/mono)
- `postcss.config.js` — Tailwind + Autoprefixer 插件
- `tsconfig.json` — `@/*` → `./src/*` 路径别名

---

## 四、页面清单

### 4.1 首页 `/`

**文件:** `src/app/page.tsx`

**内容:**
- Hero 区域: 大标题 + 副标题 + CTA 按钮（开始问诊）
- 版本标签: `v0.1.0` 带呼吸灯
- 功能卡片网格: 6 张卡片 (Bento Grid 3×2)，每张含图标、标题、描述
- Footer: 品牌信息 + 医疗免责声明

**功能卡片内容:**
| 标题 | 描述 |
|------|------|
| 多科室导诊 | 智能分析症状，精确推荐就诊科室，覆盖内科、皮肤科、耳鼻喉科、心理科 |
| AI 诊断助手 | 多 Agent 协作诊断，基于临床病例和医学理论的知识库支撑 |
| 知识库增强 | 三路知识源融合检索：临床病例 + 医学理论 + 前沿论文 |
| 智能随访 | 自动生成随访计划、用药提醒和复诊建议 |
| 隐私可控 | 完全开源，支持 Ollama 本地部署，数据不出设备 |
| 流式对话 | 实时流式对话，多 Agent 协作，体验流畅自然 |

### 4.2 智能问诊页 `/consultation`

**文件:** `src/app/consultation/page.tsx`

**两个阶段:**

**阶段 1: 对话 (chat)**
- 顶部栏: 标题 + 会话 ID（等宽字体）+ 紧急标记（红色脉冲）+ "完成问诊"按钮
- 对话区: ChatContainer（消息列表 + 输入框）
- 流式渲染: token 逐字追加
- Agent 标签: 导诊护士(蓝)、AI 医生(绿)、审方药师(紫)、随访助手(琥珀)
- 免责声明条: 首次 Agent 响应后出现
- 紧急模式: 红色免责声明 + 急救指引

**阶段 2: 完成总结 (summary)**
- 完成确认: 绿色勾号图标
- 行动按钮: 查看就诊记录 / 重新问诊
- 会话详情卡片: 会话 ID + 状态
- 免责声明条

### 4.3 就诊记录页 `/records`

**文件:** `src/app/records/page.tsx`

**三态覆盖:**
- **加载态:** 三个渐入圆点
- **空态:** 图标 + 标题 + 描述 + "开始问诊"按钮
- **有数据:** 可展开卡片列表

**每张卡片:**
- 折叠态: 图标 + 诊断名称 + 日期 + 状态标签 + 展开箭头
- 展开态: SOAP 四个字段 (Subjective/Objective/Assessment/Plan)
- Mock 数据: 2 条示例记录（感冒 + 接触性皮炎）

### 4.4 个人中心页 `/profile`

**文件:** `src/app/profile/page.tsx`

**内容:**
- 个人信息卡片: 渐变色头像 + 姓名 + 编辑模式
- 编辑模式: 性别(下拉)、出生日期、手机号
- 健康档案卡片: 过敏史(琥珀色)、既往病史(青蓝色)、长期用药(绿色)
- 快捷入口: 就诊记录 + 开始问诊（Bento 卡片）
- Mock 数据: 访客用户档案

---

## 五、组件清单

### 5.1 Chat 组件 (`src/components/chat/`)

| 组件 | 文件 | Props | 说明 |
|------|------|-------|------|
| ChatContainer | `ChatContainer.tsx` | `sessionId: string, socket: ConsultationSocket \| null` | 消息列表管理 + WebSocket 事件绑定 |
| ChatMessage | `ChatMessage.tsx` | `role, content, agent?, streaming?` | 消息气泡渲染，支持流式光标 |
| ChatInput | `ChatInput.tsx` | `onSend: (msg) => void, disabled?, placeholder?` | 自动缩放 textarea + 发送按钮 |

### 5.2 UI 组件 (`src/components/ui/`)

| 组件 | 文件 | Props | 说明 |
|------|------|-------|------|
| NavBar | `NavBar.tsx` | 无 | 全局导航栏（4 项 + 品牌 Logo），毛玻璃效果 |
| DisclaimerBanner | `DisclaimerBanner.tsx` | `type?: "standard" \| "emergency"` | 医疗免责声明条 |
| LoadingState | `LoadingState.tsx` | `message?: string` | 三点弹跳动画 |
| ErrorState | `ErrorState.tsx` | `message?: string, onRetry?: () => void` | 错误图标 + 重试按钮 |
| EmptyState | `EmptyState.tsx` | `icon?, title, description, actionLabel?, actionHref?` | 空状态图标 + CTA |
| icons | `icons.tsx` | — | 12 个 SVG 图标 |

### 5.3 可用图标 (`icons.tsx`)

| 图标 | 函数名 | 用途 |
|------|--------|------|
| 心脏 | `IconHeart` | 健康相关 |
| 消息气泡 | `IconMessage` | 对话/问诊 |
| 剪贴板 | `IconClipboard` | 记录/病历 |
| 用户 | `IconUser` | 个人/档案 |
| 主页 | `IconHome` | 导航 |
| 大脑 | `IconBrain` | AI/诊断 |
| 书本 | `IconBook` | 知识库 |
| 日历 | `IconCalendar` | 随访/排程 |
| 锁 | `IconLock` | 隐私/安全 |
| 箭头 | `IconArrow` | 导航/CTA |
| 勾号 | `IconCheck` | 完成/成功 |
| 警示三角 | `IconAlert` | 警告/紧急 |
| 折叠箭头 | `IconChevron` | 展开/折叠 |
| 听诊器 | `IconStethoscope` | 导诊/医疗 |
| 发送 | `IconSend` | 消息发送 |
| 电话 | `IconPhone` | 急救/联系 |
| 药片 | `IconPill` | 用药提醒 |

---

## 六、功能清单

| 功能 | 页面 | 状态 | 说明 |
|------|------|------|------|
| 功能卡片展示 | 首页 | ✅ | Bento Grid 6 卡片 |
| 智能问诊对话 | 问诊页 | ✅ | WebSocket 流式对话 |
| Agent 标签展示 | 问诊页 | ✅ | 4 种 Agent 不同颜色/图标 |
| 逐字流式渲染 | 问诊页 | ✅ | WebSocket token 事件追加 |
| 紧急情况检测 | 问诊页 | ✅ | `emergency` 事件红色显示 |
| 医疗免责声明 | 问诊页 | ✅ | 首次响应后出现 |
| 问诊完成总结 | 问诊页 | ✅ | 完成卡片 + 操作入口 |
| 就诊记录查看 | 记录页 | ✅ | SOAP 卡片展开/折叠 |
| 个人档案管理 | 个人中心页 | ✅ | 编辑 + 健康档案 |
| 加载/错误/空态 | 全部页面 | ✅ | 3 态全覆盖 |
| 响应式布局 | 全部页面 | ✅ | 移动端适配 |
| 导航栏高亮 | 全部页面 | ✅ | 当前页面高亮 |
| WebSocket 断线重连 | 问诊页 | ✅ | 指数退避 3 次 |
| Mock 数据降级 | 记录/个人中心 | ✅ | 无后端时展示示例数据 |

---

## 七、API 接口

### 7.1 REST API

基础路径: `/api/v1`（前端通过 `next.config.js` 代理 `http://localhost:8000/api/v1/*`）

| 端点 | 方法 | 请求体 | 响应 | 用途 |
|------|------|--------|------|------|
| `/consult` | POST | `{ symptoms: string, patient_id?: string }` | `{ session_id, patient_id, status, current_agent, created_at }` | 创建问诊会话 |
| `/consult/{id}` | GET | — | `{ session_id, patient_id, status, current_agent, history[] }` | 查询会话状态 |
| `/consult/{id}/complete` | POST | `{ subjective, objective, assessment, plan, diagnosis }` | `{ session_id, status, message }` | 完成问诊 / 保存 SOAP |
| `/consult/{id}/history` | GET | — | `{ patient_id, history: string }` | 获取患者历史记录 |
| `/health` | GET | — | `{ status: "ok" }` | 健康检查 |

### 7.2 WebSocket

端点: `/ws/{session_id}`

**客户端 → 服务端:**
```json
{"type": "message", "content": "我头痛两天了"}
```

**服务端 → 客户端 (6 种事件):**
| 事件 | data | 说明 |
|------|------|------|
| `agent_start` | `{"agent": "triage"}` | Agent 开始处理 |
| `token` | `{"token": "字"}` | 流式逐字输出 |
| `agent_end` | `{"summary": "...", "manifest": {...}}` | 处理完成，携带 HandoverManifest |
| `error` | `{"message": "...", "code": "..."}` | 错误消息 |
| `info` | `{"message": "..."}` | 系统通知 |
| `emergency` | `{"type": "emergency", "message": "...", "actions": [...]}` | 🚨 紧急情况 |

### 7.3 HandoverManifest (Agent 通信协议)

```typescript
interface HandoverManifest {
  facts: string[];           // 已确定的事实/结论
  pending_questions: string[]; // 还需收集的信息
  risk_flags: string[];      // 风险标记 ("EMERGENCY_DETECTED"等)
  evidence_level: "A" | "B" | "C";  // A=指南 B=共识 C=LLM生成
  context: Record<string, unknown>; // 跨 Agent 共享上下文
}
```

---

## 八、文件结构

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # 根布局 (NavBar + 全局样式导入)
│   │   ├── globals.css             # Tailwind + 设计令牌 + 组件样式
│   │   ├── page.tsx                # 首页 (Hero + 功能卡片)
│   │   ├── consultation/
│   │   │   └── page.tsx            # 问诊页 (chat/summary 两阶段)
│   │   ├── records/
│   │   │   └── page.tsx            # 就诊记录页 (SOAP 卡片)
│   │   └── profile/
│   │       └── page.tsx            # 个人中心页 (档案 + 编辑)
│   │
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx   # 对话容器
│   │   │   ├── ChatMessage.tsx     # 消息气泡
│   │   │   └── ChatInput.tsx       # 输入框
│   │   └── ui/
│   │       ├── NavBar.tsx          # 导航栏
│   │       ├── DisclaimerBanner.tsx # 免责声明
│   │       ├── LoadingState.tsx    # 加载态
│   │       ├── ErrorState.tsx      # 错误态
│   │       ├── EmptyState.tsx      # 空态
│   │       └── icons.tsx           # SVG 图标库
│   │
│   ├── lib/
│   │   ├── api.ts                  # REST API 客户端
│   │   └── websocket.ts            # WebSocket 客户端
│   │
│   └── stores/
│       └── consultationStore.ts    # 状态管理 (预留)
│
├── tailwind.config.js              # 自定义颜色/字体
├── postcss.config.js               # PostCSS 插件
├── next.config.js                  # API 代理配置
├── tsconfig.json                   # TypeScript 配置
└── package.json                    # 依赖管理
```

---

## 九、启动命令

```bash
# 安装依赖
cd frontend && npm install --legacy-peer-deps

# 开发模式
npm run dev    # → http://localhost:3000

# 生产构建
npm run build

# 需要后端时，另开终端:
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 十、API 客户端使用示例

```typescript
import { startConsultation, completeConsultation } from "@/lib/api";
import { createConsultationSocket } from "@/lib/websocket";

// REST: 创建会话
const resp = await startConsultation("我头痛两天了");
// { session_id: "session_abc123...", patient_id: "patient_def456...", ... }

// REST: 完成问诊
await completeConsultation("session_abc123", {
  subjective: "发热咳嗽3天",
  objective: "体温38.2°C",
  assessment: "急性上呼吸道感染",
  plan: "退热药 + 休息",
  diagnosis: "感冒",
});

// WebSocket: 实时对话
const socket = createConsultationSocket("session_abc123");
socket.on("token", (e) => console.log(e.data.token));  // 逐字渲染
socket.on("agent_end", () => console.log("Agent 完成"));
socket.on("emergency", () => alert("紧急情况!"));
socket.connect();
socket.send({ type: "message", content: "我头痛" });
```

---

## 十一、设计约束 (Do / Don't)

### ✅ Must Do

- 使用 SVG 图标（`icons.tsx`），不使用 emoji
- 所有文本色对比度 ≥4.5:1
- 每个页面覆盖加载/错误/空三态
- 医疗回答后必须显示免责声明
- 使用设计令牌颜色（`medical-*`），不硬编码色值
- 标题用 `font-heading` 字体族
- 所有按钮/链接有 `cursor-pointer` 和悬停反馈

### ❌ Must Not

- 不使用 emoji 作为 UI 图标（🎨🚀⚙️换成SVG）
- 不使用霓虹色（#FF00FF等）
- 不使用粉色/紫色渐变（AI 常见套路）
- 不使用运动密集的动画（尊重 `prefers-reduced-motion`）
- 不隐藏聚焦环 (`outline-none` 需同时提供 `focus-visible:ring`)
- 不省略 alt/aria-label
