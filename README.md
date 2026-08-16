# MediNexus / 医枢 — 开源多智能体医疗诊断平台

<p align="center">
  <a href="https://github.com/HTenets/MediNexus"><img src="https://img.shields.io/badge/版本-v0.1.0-blue" alt="版本"></a>
  <a href="https://github.com/HTenets/MediNexus/blob/main/LICENSE"><img src="https://img.shields.io/badge/许可证-Apache%202.0-green" alt="许可证"></a>
  <a href="https://github.com/HTenets/MediNexus"><img src="https://img.shields.io/github/stars/HTenets/MediNexus?style=social" alt="Stars"></a>
  <a href="https://github.com/HTenets/MediNexus/commits/main"><img src="https://img.shields.io/badge/状态-开发中-orange" alt="状态"></a>
</p>

<p align="center">
  <b>多智能体协作 · 全流程闭环问诊 · 离线降级可用 · 完全开源</b>
</p>

<p align="center">
  <!-- MediNexus — 智能问诊主界面 -->
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Modern%20medical%20AI%20consultation%20dashboard%20with%20a%20chat%20interface%20showing%20multi-agent%20diagnosis%20pipeline%2C%20gradient%20blue%20and%20green%20UI%2C%20sleek%20glassmorphism%20design%2C%20dark%20text%20on%20light%20background%2C%20medical%20icons%2C%20sidebar%20with%20navigation%2C%20professional%20and%20clean%20aesthetic&image_size=landscape_16_9" alt="MediNexus 智能问诊界面" width="80%">
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
                         ↕
                  CoordinatorAgent（多科室会诊）
```

- **LangGraph 状态图驱动** — 每个 Agent 独立运行，通过 `HandoverManifest` 标准协议交接
- **智能路由** — SupervisorAgent 根据分诊结果、紧急程度自动路由到对应 Agent
- **流式输出** — 基于 WebSocket 的实时流式传输，对话体验流畅自然

<p align="center">
  <!-- 多智能体流水线图示 -->
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=A%20flowchart%20diagram%20showing%20a%20multi-agent%20pipeline%20for%20medical%20consultation%3A%20User%20%22%22%20Triage%20%22%22%20Doctor%20%22%22%20Review%20%22%22%20Followup%2C%20with%20arrows%20connecting%20each%20stage%2C%20clean%20minimalist%20design%20in%20blue%20and%20green%20colors%2C%20professional%20medical%20style&image_size=landscape_16_9" alt="多智能体流水线" width="80%">
</p>

### 2. 分层记忆系统

基于 **Mem0** 架构的三层记忆存储，实现跨会话的智能健康档案：

| 记忆层次 | 存储介质 | 功能 |
|---------|---------|------|
| **Working Memory** | Redis（TTL 过期） | 当前会话短期状态 |
| **Episodic Memory** | PostgreSQL + pgvector | 历史就诊/问诊记录 |
| **Semantic Memory** | PostgreSQL + pgvector | 患者画像（过敏史、慢性病、用药禁忌） |

- 复诊时自动加载历史档案，无缝衔接
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
- BM25 全文检索作为向量库离线降级
- 可选知识图谱增强

### 6. 现代化前端设计

<p align="center">
  <!-- 前端界面多图展示 -->
  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Modern%20medical%20web%20application%20screenshot%20showing%20a%20landing%20page%20with%20hero%20section%20titled%20%22%20Intelligent%20Triage%20Precise%20Diagnosis%22%2C%20floating%20gradient%20backgrounds%2C%20glassmorphism%20cards%2C%20feature%20sections%20with%20icons%2C%20clean%20white%20and%20blue%20design%2C%20responsive%20layout&image_size=landscape_16_9" alt="首页展示" width="80%">
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

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | FastAPI + Python 3.12+ | REST API + WebSocket |
| **Agent 编排** | LangGraph | 状态图驱动多 Agent 流水线 |
| **数据库** | PostgreSQL 17 + pgvector | 主存储 + 向量检索 |
| **向量存储** | Qdrant | 知识库语义检索 |
| **缓存/会话** | Redis 7 | 会话状态 + 工作记忆 |
| **记忆系统** | Mem0 架构 | 三层分层记忆存储 |
| **异步任务** | Celery | 后台任务调度 |
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
│   │   ├── rag.py           # 多源检索增强生成
│   │   ├── retriever.py     # 检索器
│   │   └── graph.py         # 知识图谱
│   ├── memory/              # 记忆系统
│   │   ├── manager.py       # 记忆管理器
│   │   ├── working.py       # 工作记忆（Redis）
│   │   └── stores/          # 情景/语义记忆存储
│   ├── llm/                 # LLM 客户端
│   │   └── providers/       # Ollama / OpenAI / Anthropic
│   └── orchestration/       # 编排层
│       ├── supervisor.py    # 会话管理 & Agent 路由
│       └── stream.py        # WebSocket 流式传输
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
| [架构设计](docs/architecture.md) | 系统架构与核心流程 |
| [Agent 设计](docs/agent-design.md) | 多智能体系统设计详解 |
| [API 参考](docs/api-reference.md) | REST API 与 WebSocket 协议 |
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