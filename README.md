# MediNexus / 医枢 — 开源多智能体医疗诊断平台

<p align="center">
  <a href="https://github.com/HTenets/MediNexus"><img src="https://img.shields.io/badge/版本-v0.1.1-blue" alt="版本"></a>
  <a href="https://github.com/HTenets/MediNexus/blob/main/LICENSE"><img src="https://img.shields.io/badge/许可证-Apache%202.0-green" alt="许可证"></a>
  <a href="https://github.com/HTenets/MediNexus"><img src="https://img.shields.io/github/stars/HTenets/MediNexus?style=social" alt="Stars"></a>
  <a href="https://github.com/HTenets/MediNexus/commits/main"><img src="https://img.shields.io/badge/状态-开发中-orange" alt="状态"></a>
</p>

<p align="center">
  <b>多智能体协作 · 全流程闭环问诊 · 离线降级可用 · 完全开源</b>
</p>

<p align="center">
  <img src="docs/images/homepage.png" alt="MediNexus 宣传页面" width="80%">
  <br>
</p>

---

## 在线体验

| 入口 | 地址 |
|------|------|
| **Frontend** | [http://htenets.top/programs/medinexus](http://htenets.top/programs/medinexus) |
| **API Docs** | [http://htenets.top/api/v1/docs](http://htenets.top/api/v1/docs) |
| **GitHub** | [https://github.com/HTenets/MediNexus](https://github.com/HTenets/MediNexus) |

---

## 项目简介

**MediNexus（医枢）** 是一个基于 **多智能体协作** 的开源智能医疗诊断平台，由四个专业 AI Agent 协作完成全流程问诊：

- **TriageAgent（导诊护士）** — 症状评估与科室分诊，识别紧急情况
- **DoctorAgent（主治医生）** — 多轮问诊与鉴别诊断，集成专科 Skill 系统
- **ReviewAgent（审方药师）** — 独立知识库验证，用药合规与禁忌复核
- **FollowupAgent（随访助手）** — 康复计划与用药提醒，健康管理追踪

每个 Agent 既可由 **LLM 驱动** 提供智能诊断，也能在无 LLM 时 **自动降级为规则引擎**，确保系统始终可用。

---

## 核心特色

### 1. 多智能体编排流水线

```
用户 → TriageAgent → DoctorAgent (+ Skill) → ReviewAgent → FollowupAgent → 输出
```

- **状态机路由** — `SupervisorAgent` 根据分诊结果、紧急程度与上下文在 Agent 间路由；
  每个 Agent 独立运行，通过 `HandoverManifest` 标准协议交接
- **真流式输出** — WebSocket 直连 LLM 的 `chat_stream`，逐 token 下发；
  无 LLM 时整段下发，不做"假打字"模拟
- **患者口述渲染** — 结构化的 `HandoverManifest` 会经 LLM 渲染为通俗段落后再流式下发
  （`MEDINEXUS_STREAM_NARRATIVE=false` 可关闭，省下每阶段一次额外调用）

> **CoordinatorAgent（多科室会诊）已实现但尚未接线**：其触发词（头痛、发热、胸闷）
> 过于宽泛，直接启用会把绝大多数日常问诊引入尚无专科会诊能力的多科分支。
> 接线计划见 [v0.1.1 路线图](docs/plan/v0.1.1-plan.md)。


### 2. 分层记忆系统

参照 Mem0 思路自研的三层记忆（**未依赖 Mem0 库**），实现跨会话的智能健康档案：

| 记忆层次 | 有 Redis / 数据库时 | 无外部依赖时 | 功能 |
|---------|------------------|-------------|------|
| **Working Memory** | Redis（TTL 过期） | 进程内字典 | 当前会话短期状态 |
| **Episodic Memory** | `consultations` 表 | 进程内列表 | 历史就诊/问诊记录 |
| **Semantic Memory** | `patients` 表 | 进程内字典 | 患者画像（过敏史、既往病史） |

- 复诊时自动把患者档案与既往记录注入 Agent 上下文，无需重复陈述
- 会话结束（`complete` / `emergency_protocol`）时自动归档为本轮 Episode
- 每一层都优雅降级：记忆故障只记录日志，绝不阻断问诊
- PII 脱敏处理，保障患者隐私安全

### 3. 安全护栏系统

在 Agent 执行前后注入安全钩子：

- **PII 脱敏器** — 自动识别并脱敏手机号、身份证号、邮箱等敏感信息
- **紧急检测器** — 中英文关键词 + 正则匹配，识别自杀倾向、心脏急症、呼吸困难等 6 类紧急信号
- 紧急信号 **强制覆盖** Agent 输出，触发应急响应流程

### 4. 专科 Skill 插件系统

DoctorAgent 内置可扩展的专科技能系统：

- **内科** — 呼吸/消化/心脑血管症状的诊疗建议
- **皮肤科** — 皮疹/痤疮/湿疹的鉴别诊断
- **耳鼻喉科** — 咽喉/耳部/鼻部症状的评估
- **心理科** — 焦虑/抑郁/失眠的筛查与危机干预
- **骨科** — 疼痛/骨折/关节问题的初步判断

Skill 自动匹配症状，支持自定义扩展，可独立注入知识库上下文。

### 5. RAG 知识增强

多源检索增强生成（HF-RAG 风格融合）：

- 三源知识库：临床病例（0.8权重）、医学理论（0.6权重）、最新论文（0.3权重）
- RRF + Z-score 融合排序
- **默认走 BM25 全文检索**（内置知识库，零外部依赖）；配置 `MEDINEXUS_QDRANT_URL`
  且可用嵌入服务时切换到向量检索，BM25 自动作为降级链路
- 知识图谱（症状→疾病）增强召回
- 通过 `GET /api/v1/knowledge/search` 对外提供检索能力

### 6. 现代化前端设计

<p align="center">
  <img src="docs/images/consultation-ui.png" alt="智能问诊界面" width="80%">
  <br>
</p>

- **Next.js 14 + React 18 + Tailwind CSS 3** — App Router 架构，全栈现代框架
- **shadcn/ui 设计语言** — 专业的医疗级 UI 组件库
- **framer-motion 动画** — 流畅的页面过渡与交互反馈
- **玻璃拟态设计** — 多层级毛玻璃效果，视觉层次分明
- **医疗色系统** — 蓝色主色调 + 绿色强调色，传递专业与信任感
- **自适应布局** — 12 列网格系统，侧边栏可折叠

### 7. LLM 多提供商支持

统一 LLM 客户端接口，支持热切换：

- **Ollama** — 本地部署，数据不出设备（默认）
- **OpenAI** — GPT-4o / GPT-4o-mini 等
- **Anthropic** — Claude 3.5 Sonnet / Haiku 等
- **自动降级** — 无 LLM 时无缝切换至规则引擎

### 8. 灵活部署方案

| 方案 | 平台 | 费用 | 适合场景 |
|------|------|------|---------|
| **Docker Compose** | 本地/阿里云 | 自备服务器 | 生产环境，完全掌控 |
| **Vercel + Zeabur** | 云平台 | 免费额度 | 快速体验，无需绑卡 |
| **Vercel + Koyeb** | 云平台 | 免费额度 | 国际方案，流程成熟 |
| **纯 Demo 模式** | 内存模式 | 免费 | 快速演示，重启丢失 |

---

## 实现状态

本表用于避免"宣传与实物不符"。✅ = 真实可用；🚧 = 代码存在但运行时不参与；📌 = 规划中。

| 能力 | 状态 | 说明 |
|------|------|------|
| 四 Agent 问诊链路（分诊→诊断→复核→随访） | ✅ | LLM 模式 + 规则降级双通道 |
| PII 脱敏 / 紧急检测护栏 | ✅ | 在 Agent 前置钩子中强制执行 |
| JWT 签发 / 刷新 / 注册登录 | ✅ | bcrypt 哈希；刷新端点已放行 |
| 患者 / 病历 / 会话持久化 | ✅ | PostgreSQL + Alembic 迁移；无库时内存降级 |
| 分层记忆（working / episodic / semantic） | ✅ | 已注入 Agent 上下文，复诊自动带出档案 |
| RAG 多源检索 + 知识图谱 | ✅ | BM25 默认路由，Qdrant 可选；`ReviewAgent` 独立检索 |
| 真流式 WebSocket 输出 | ✅ | 直连 LLM `chat_stream` |
| 专科 Skill 系统（内/皮肤/耳鼻喉/心理） | ✅ | 按症状与科室自动匹配 |
| `/consultation/analysis` 知识源分析 | ✅ | 接真实检索接口 |
| CoordinatorAgent 多科室会诊 | 🚧 | 已实现并有测试，但**未接入路由**（触发词过宽） |
| 数字孪生 3D 可视化 | 📌 | 现为 CSS 动画占位；排入 v0.2.0 |
| 可穿戴设备同步（心率/睡眠/步数） | 📌 | 界面已标注"尚未接入" |
| 报告上传与自动解析 | 📌 | 上传页为静态原型，未接后端 |
| 随访计划与预约 | 📌 | 页面已改为展示真实医嘱，不做虚假排期 |
| LangGraph 状态图编排 | — | 已移除：与 `SupervisorAgent` 重复且从未被调用 |
| Mem0 库 | — | 未采用：三层记忆为自研实现 |
| Celery 异步任务 | 🚧 | 任务已定义但无调用方，未随应用启动 |
| 实名认证（IdentityVerifier） | 🚧 | 有实现与测试，未接入流水线 |

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | FastAPI + Python 3.12+ | REST API + WebSocket |
| **Agent 编排** | 自研 `SupervisorAgent` 状态机 | 会话管理 + Agent 路由 + 记忆/RAG 注入 |
| **数据库** | PostgreSQL 17（SQLAlchemy 2.0 异步 + Alembic） | 患者 / 病历 / 会话 / 用户 |
| **向量存储** | Qdrant（可选） | 知识库语义检索 |
| **全文检索** | 内置 BM25（默认检索路径，零依赖） | 知识库检索与降级链路 |
| **缓存/会话** | Redis 7（可选） | 会话状态 + 工作记忆 |
| **记忆系统** | 自研三层（working / episodic / semantic） | 跨会话患者档案 |
| **密码哈希** | bcrypt（直接使用，不经 passlib） | 用户口令存储 |
| **前端框架** | Next.js 14 + React 18 | App Router 全栈框架 |
| **UI 组件** | shadcn/ui + Tailwind CSS 3 | 医疗级设计系统 |
| **动画** | framer-motion | 流畅交互动画 |
| **图标** | lucide-react | 开源图标库 |
| **LLM 客户端** | 统一接口 | Ollama / OpenAI / Anthropic |

---

## 快速开始

### Docker Compose（推荐）

```bash
# 一键启动全部服务
docker-compose up --build

# 或仅启动数据库，后端在前端独立运行
docker-compose up postgres redis qdrant
```

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看 API 文档。

### 本地开发

```bash
# 终端 1：启动数据库
docker-compose up postgres redis qdrant

# 终端 2：启动后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 3：启动前端
cd frontend
npm run dev
```

### 环境变量

配置通过 `.env` 文件加载，变量前缀为 `MEDINEXUS_`：

```env
MEDINEXUS_DATABASE_URL=postgresql+asyncpg://medinexus:medinexus_dev@localhost:5432/medinexus
MEDINEXUS_REDIS_URL=redis://localhost:6379/0
MEDINEXUS_QDRANT_URL=http://localhost:6333
MEDINEXUS_JWT_SECRET=change-me-in-production
MEDINEXUS_DEMO_MODE=true
MEDINEXUS_LLM_PROVIDER=ollama
MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434
MEDINEXUS_OLLAMA_MODEL=qwen2.5:14b
```

所有组件均可省略：`DATABASE_URL` / `REDIS_URL` / `QDRANT_URL` 缺省时，
系统分别降级为进程内存储与 BM25 检索，仍是一条完整可用的链路。

其他可选变量：

| 变量 | 默认 | 说明 |
|------|------|------|
| `MEDINEXUS_STREAM_NARRATIVE` | `true` | 用 LLM 流式渲染通俗口述（每阶段多一次调用） |
| `MEDINEXUS_EMBEDDING_PROVIDER` | `auto` | `auto` / `ollama` / `openai` / `none` |
| `MEDINEXUS_EMBEDDING_MODEL` | 跟随 LLM | 嵌入模型名 |
| `MEDINEXUS_EMBEDDING_BASE_URL` | 跟随 provider | 嵌入服务地址 |
| `MEDINEXUS_EMBEDDING_API_KEY` | 空 | 嵌入服务密钥 |
| `MEDINEXUS_EMBEDDING_DIM` | 按 provider 推断 | 向量维度，需与 Qdrant collection 一致 |

---

## 项目结构

```
MediNexus/
├── backend/                 # FastAPI 后端
│   ├── agents/              # 多智能体系统
│   │   ├── base.py          # Agent 抽象基类
│   │   ├── triage/          # 导诊分诊 Agent
│   │   ├── doctor/          # 医生诊断 Agent（含 Skill 系统）
│   │   ├── review/          # 审方复核 Agent
│   │   └── followup/        # 随访管理 Agent
│   ├── app/                 # API 层
│   │   ├── api/             # REST 路由
│   │   └── schemas/         # Pydantic 数据模型
│   ├── guardrails/          # 安全护栏
│   │   ├── pii_sanitizer.py # PII 脱敏
│   │   └── emergency_detector.py  # 紧急信号检测
│   ├── knowledge/           # 知识库 & RAG
│   │   ├── factory.py       # 检索栈装配（BM25 / Qdrant / 知识图谱）
│   │   ├── rag.py           # 多源检索增强生成
│   │   ├── retriever.py     # 检索器（RRF + Z-score 融合）
│   │   ├── bm25_fallback.py # BM25 全文检索（默认路径）
│   │   └── graph/           # 知识图谱
│   ├── memory/              # 记忆系统
│   │   ├── manager.py       # 记忆管理器（三层门面）
│   │   ├── working.py       # 工作记忆（Redis / 进程内）
│   │   ├── _redis.py        # Redis 惰性访问器
│   │   └── stores/          # 情景/语义记忆存储
│   ├── llm/                 # LLM 客户端
│   │   └── providers/       # Ollama / OpenAI / Anthropic
│   └── orchestration/       # 编排层
│       ├── supervisor.py    # 会话管理 & Agent 路由 & 记忆/RAG 注入
│       ├── narrative.py     # 结构化结果 → 患者口述（真流式）
│       ├── state.py         # 会话状态
│       └── stream.py        # WebSocket 事件封装
├── frontend/                # Next.js 前端
│   └── src/
│       ├── app/             # 页面路由
│       ├── components/      # UI 组件
│       └── lib/             # 工具库（API / WebSocket）
├── docs/                    # 项目文档
├── infrastructure/          # Docker / Nginx 配置
└── docker-compose.yml       # 服务编排
```

---

## Agent 流水线详解

### 1. TriageAgent — 智能分诊

- 接收患者主诉，分析症状
- 评估紧急程度（routine / urgent / emergency）
- 推荐就诊科室（内科 / 皮肤科 / 耳鼻喉科 / 心理科 / 骨科 / 全科）
- 识别关键信息缺口，生成追问列表

### 2. DoctorAgent — 医生诊断

- 接收分诊结果，自动匹配专科 Skill
- 运行诊断状态机（INITIAL → DIFFERENTIAL → TREATMENT → COMPLETED）
- LLM 模式：注入 Skill 知识 + 系统提示，生成结构化诊断
- 规则模式：基于关键字的专科症状匹配，经验性建议
- 输出诊断结果、治疗方案、风险评估

### 3. ReviewAgent — 质控审核

- 独立检索知识库，验证诊断准确性
- 检查用药禁忌与相互作用
- 评估证据等级（A/B/C）
- 标记高风险项，强制返回 Doctor 修订

### 4. FollowupAgent — 随访管理

- 生成康复计划与用药提醒
- 症状监测与复查建议
- 健康档案更新

---

## 贡献指南

欢迎参与 MediNexus 的开发！任何形式的贡献——代码、文档、Bug 反馈、功能建议——都非常欢迎。

1. Fork 仓库
2. 创建特性分支：`git checkout -b feat/amazing-feature`
3. 提交改动：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feat/amazing-feature`
5. 发起 Pull Request

详细开发指南请参阅 [docs/contribution.md](docs/contribution.md)。

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [架构设计](docs/architecture.md) | 系统架构与核心流程（v0.1.1） |
| [部署指南](docs/deploy-aliyun.md) | 阿里云生产环境部署 |
| [Vercel 部署](docs/deploy-vercel-render.md) | 免费云平台部署方案 |
| [Docker 快速入门](docs/docker-quickstart.md) | Docker 零基础教程 |
| [BYOK 指南](docs/byok-guide.md) | 自带 LLM Key 配置 |

---

## 许可证

[Apache License 2.0](LICENSE)

---

<p align="center">
  <b>MediNexus / 医枢</b> — 让 AI 赋能医疗，让健康触手可及
</p>

<p align="center">
  <sub>免责声明：AI 诊断仅供参考，不构成医疗诊断建议。如有身体不适，请及时前往正规医疗机构就诊。</sub>
</p>