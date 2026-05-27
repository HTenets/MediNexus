# MediNexus / 医枢 — 2个月核心开发计划

> 版本: v1.0 | 周期: 8 周 | 目标: 可运行的核心问诊闭环

---

## 核心范围界定

### 2个月内实现的「核心」

```
┌──────────────────────────────────────────────────────┐
│                  2个月核心范围                          │
│                                                        │
│  ✅ 多 Agent 框架 (LangGraph)                          │
│  ✅ Triage Agent (导诊)                                │
│  ✅ Doctor Agent (医生) + 3 个科室 Skill 包             │
│  ✅ Coordinator Agent (会诊协调)                       │
│  ✅ Follow-up Agent (随访管理)                         │
│  ✅ Mental Health Skill (心理科/精神科)                │
│  ✅ Review Agent (处方审查)                           │
│  ✅ 基础 RAG 知识库 (向量检索)                         │
│  ✅ 记忆系统 (基于 Mem0)                              │
│  ✅ FastAPI 后端 + WebSocket 流式对话                  │
│  ✅ PostgreSQL 病历存储                               │
│  ✅ Web 前端 (React + 对话界面 + 病历展示)             │
│  ✅ OAuth 认证 + 基本安全                              │
│  ✅ Docker Compose 一键部署                            │
│  ✅ 完整的就诊闭环 (导诊→诊断→审查→输出)               │
└──────────────────────────────────────────────────────┘
```

### ❌ 不包含 (未来扩展)

```
┌──────────────────────────────────────────────────────┐
│  后期扩展 (架构预留, 暂不实现)                          │
│                                                        │
│  ┌── 微信小程序 ── 架构上 WebSocket 复用, UI 层延迟   │
│  ┌── Desktop Pet 桌宠 ── API 可复用, 客户端延迟        │
│  ┌── GraphRAG ── RAG 接口抽象化, 实现延迟              │
│  ┌── 插件市场 ── Plugin SDK 定义, 市场延迟             │
│  ┌── 多模态 (影像分析) ── Tool 接口预留                │
│  ┌── FHIR 导出 ── 数据模型兼容, 导出功能延迟           │
│  ┌── 可穿戴设备接入 ── API 接口预留, 具体实现延迟      │
│  ┌── Kubernetes 部署 ── Docker Compose 先行            │
│  ┌── 专家在环 (Human-in-the-loop) ── Guard 接口预留    │
│  ┌── 多语言/国际化 ── i18n 框架搭好, 翻译延迟          │
└──────────────────────────────────────────────────────┘
```

---

## 项目架构

```
MediNexus/
├── pyproject.toml                       # Python 项目配置
├── docker-compose.yml                   # 本地开发部署
├── Dockerfile
├── Makefile                             # 常用命令
├── .env.example
├── README.md
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   ├── agent-design.md
│   └── contribution.md
│
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI 入口
│   │   ├── config.py                    # 配置管理 (env -> pydantic)
│   │   │
│   │   ├── api/                         # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── router.py                # 路由汇总
│   │   │   ├── consultation.py          # 问诊 API
│   │   │   ├── patients.py              # 患者 API
│   │   │   ├── medical_records.py       # 病历 API
│   │   │   └── health.py               # 健康检查
│   │   │
│   │   ├── core/                        # 核心基础设施
│   │   │   ├── __init__.py
│   │   │   ├── database.py              # PostgreSQL 连接
│   │   │   ├── redis.py                 # Redis 连接
│   │   │   ├── auth.py                  # OAuth 2.0 + JWT
│   │   │   ├── security.py             # PII 脱敏/加密
│   │   │   └── dependencies.py          # FastAPI 依赖注入
│   │   │
│   │   ├── models/                      # SQLAlchemy ORM 模型
│   │   │   ├── __init__.py
│   │   │   ├── patient.py               # 患者
│   │   │   ├── consultation.py          # 就诊记录
│   │   │   ├── prescription.py          # 处方
│   │   │   ├── medical_history.py       # 病史
│   │   │   ├── followup.py              # 随访 (表结构预留)
│   │   │   └── audit_log.py            # 审计日志
│   │   │
│   │   ├── schemas/                     # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── consultation.py          # 请求/响应 schema
│   │   │   ├── patient.py
│   │   │   ├── agent.py                 # Agent 通信协议
│   │   │   └── memory.py               # 记忆数据格式
│   │   │
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── auth.py                  # 认证中间件
│   │       ├── logging.py              # 请求日志
│   │       └── rate_limit.py           # 限流
│   │
│   ├── agents/                          # ★ 核心: 多智能体
│   │   ├── __init__.py
│   │   ├── base.py                     # BaseAgent 抽象
│   │   │   # 所有 Agent 继承此类
│   │   │   # └── 预留: tool_calling, hook 接口
│   │   │
│   │   ├── triage/                     # 导诊 Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # TriageAgent
│   │   │   └── prompt.py               # 系统提示词
│   │   │
│   │   ├── doctor/                     # 医生 Agent (核心)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # DoctorAgent
│   │   │   ├── prompt.py               # 诊断提示词
│   │   │   ├── diagnosis_flow.py       # 诊断流程状态机
│   │   │   └── skills/                 # ★ Skill 系统
│   │   │       ├── __init__.py
│   │   │       ├── base.py             # Skill 抽象类
│   │   │       ├── loader.py           # Skill 动态加载器
│   │   │       ├── registry.py         # Skill 注册中心
│   │   │       │   # └── 预留: 插件式 Skill 热加载
│   │   │       └── builtin/            # 内置科室 Skill
│   │   │           ├── internal_medicine/
│   │   │           ├── dermatology/
│   │   │           ├── ent/
│   │   │           └── mental_health/       # 心理科 Skill
│   │   │
│   │   ├── review/                     # 审查 Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # ReviewAgent
│   │   │   ├── prompt.py               # 审查提示词
│   │   │   ├── rules/                  # 审查规则
│   │   │   │   ├── drug_interaction.py # 药物相互作用
│   │   │   │   └── contraindication.py # 禁忌症检查
│   │   │   └── checkers/               # 预留: 可插拔检查器
│   │   │       └── __init__.py
│   │   │
│   │   ├── coordinator/                # 会诊协调 Agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                # CoordinatorAgent
│   │   │   ├── prompt.py               # 会诊提示词
│   │   │   └── consultation_protocol.py # 会诊协议/状态机
│   │   │
│   │   └── followup/                   # 随访 Agent
│   │       ├── __init__.py
│   │       ├── agent.py                # FollowupAgent
│   │       ├── prompt.py               # 随访提示词
│   │       └── scheduler.py            # 随访计划调度
│   │
│   ├── orchestration/                  # ★ Agent 编排层
│   │   ├── __init__.py
│   │   ├── graph.py                    # LangGraph 状态图
│   │   │   # └── 预留: 动态图构建 (未来条件分支)
│   │   ├── supervisor.py               # Supervisor Agent
│   │   │   # └── 预留: 负载感知路由
│   │   ├── state.py                    # 会话状态定义
│   │   └── stream.py                   # 流式事件处理
│   │
│   ├── knowledge/                      # 知识库
│   │   ├── __init__.py
│   │   ├── rag.py                      # RAG 查询接口 (抽象)
│   │   ├── vector_store.py             # Qdrant 操作
│   │   ├── loader.py                   # 文档加载/分块Pipeline
│   │   └── graph_rag.py               # 预留: GraphRAG 接口
│   │       # └── 接口与 rag.py 一致, 可切换实现
│   │
│   ├── memory/                         # 记忆系统
│   │   ├── __init__.py
│   │   ├── manager.py                  # 记忆管理器
│   │   ├── working.py                  # 工作记忆 (Redis)
│   │   └── stores/
│   │       ├── __init__.py
│   │       ├── episodic.py             # 情景记忆 (Mem0/PostgreSQL)
│   │       └── semantic.py             # 语义记忆 (PostgreSQL)
│   │
│   ├── llm/                            # LLM 抽象层
│   │   ├── __init__.py
│   │   ├── client.py                   # 统一客户端接口
│   │   └── providers/                  # 多 Provider 支持
│   │       ├── __init__.py
│   │       ├── openai.py               # OpenAI / 兼容接口
│   │       ├── anthropic.py            # Anthropic Claude
│   │       └── ollama.py               # 本地模型 (Ollama)
│   │
│   ├── guardrails/                     # 安全护栏 (新增, 教训驱动)
│   │   ├── __init__.py
│   │   ├── identity_verifier.py        # 身份验证 (教训1)
│   │   ├── emergency_detector.py       # 紧急信号检测
│   │   └── pii_sanitizer.py            # PII 脱敏
│   │
│   └── workers/                        # 后台任务
│       ├── __init__.py
│       └── tasks.py                    # Celery 任务定义
│
├── frontend/                           # Web 前端 (Next.js)
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                # 首页
│   │   │   ├── consultation/
│   │   │   ├── records/
│   │   │   └── profile/
│   │   ├── components/                 # UI 组件
│   │   │   ├── chat/                   # 对话组件
│   │   │   ├── medical-record/         # 病历展示
│   │   │   └── ui/                     # 通用 UI
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts                  # API 客户端
│   │   │   └── websocket.ts            # WebSocket 客户端
│   │   └── stores/                     # 状态管理
│   └── public/
│
├── plugins/                            # 预留: 插件 SDK + 示例
│   ├── sdk/
│   │   ├── __init__.py
│   │   ├── base.py                     # Plugin 基类
│   │   └── hooks.py                    # 生命周期钩子定义
│   └── examples/
│       └── drug_lookup/
│
├── scripts/                            # 工具脚本
│   ├── init_db.py                      # 数据库初始化
│   ├── load_knowledge.py               # 知识库导入
│   └── seed_data.py                    # 测试数据
│
├── tests/                              # 测试
│   ├── unit/
│   │   ├── agents/
│   │   ├── knowledge/
│   │   └── memory/
│   ├── integration/
│   │   ├── test_consultation_flow.py   # 完整就诊流程测试
│   │   └── test_agent_communication.py # Agent 通信测试
│   └── evaluation/                     # 预留: Agent 评估
│       └── test_cases/                 # 标准化测试病例
│
└── infrastructure/                     # 部署配置
    ├── docker/
    │   ├── Dockerfile.backend
    │   ├── Dockerfile.frontend
    │   └── Dockerfile.worker
    └── monitoring/                     # 预留: 监控配置
        └── prometheus.yml
```

---

## 架构关键设计决策 (响应教训)

```
基于调研教训的 5 个关键架构决策:

1️⃣ Identity Verification Guard (教训1: Patient Misbinding)
   └── guardrails/identity_verifier.py
   └── 每个 Agent 处理患者数据前调用
   └── 架构位置: 在 orchestration/supervisor.py 中作为 pre-hook

2️⃣ Structured Handover Manifest (教训2: Agent 交接失败)
   └── schemas/agent.py → HandoverManifest
   └── Agent 间传递结构化数据, 非自由文本
   └── 格式: { facts: [], pending_questions: [], risk_flags: [] }

3️⃣ Evidence-Level Tagging (教训3: 有害建议更易被采纳)
   └── 所有治疗建议带证据等级标记
   └── Level A: 指南推荐 | Level B: 专家共识 | Level C: LLM 生成
   └── Review Agent 可据此判定审查严格度

4️⃣ Tiered Guardrail (教训4: Guardrail 延迟)
   └── L1 (在线同步): 身份验证, 紧急信号, 自杀倾向
   └── L2 (异步): 处方审查, 诊断一致性
   └── L3 (离线): 方案优化, 证据更新

5️⃣ Contextual Retrieval (教训5: 信息可及≠可用)
   └── 知识检索分阶段:
   └── 导诊阶段 → 仅过敏史和主诉
   └── 诊断阶段 → 完整既往史
   └── 审查阶段 → 药物相互作用
```

---

## 逐周开发计划

### 第 1 周: 项目基础设施

**目标**: 能跑起来的开发环境 + 数据模型 + LLM 联通

| 日期 | 后端任务 | 前端任务 |
|------|---------|---------|
| Day 1 | 初始化项目仓库, pyproject.toml, Docker Compose 骨架 | 初始化 Next.js 项目, Tailwind 配置 |
| Day 2 | PostgreSQL 模型定义 (patient, consultation, prescription, medical_history) | 基础布局组件 (Sidebar, Header) |
| Day 3 | FastAPI 基础框架 + config.py + database.py | API 客户端封装 (lib/api.ts) |
| Day 4 | LLM 抽象层 (client.py + OpenAI/Anthropic/Ollama providers) | 首页框架 (Layout + 路由) |
| Day 5 | Redis 连接 + 基础缓存 | 类型定义 + API schema 对齐 |
| Day 6 | Alembic 迁移 + init_db.py 脚本 | 主题/UI 组件库 (shadcn/ui) |
| Day 7 | Docker Compose 整合 (PostgreSQL + Redis + Qdrant) | 端到端验证: 后端健康检查通过 |

**里程碑**: `docker-compose up` 后所有服务启动成功, FastAPI 健康检查返回 200, LLM 调用通过

**可扩展预留**: 数据模型中的 followup 表已创建 (空表), medical_history 支持多种病史类型 (JSONB)

---

### 第 2 周: Agent 框架 + 导诊 Agent

**目标**: Agent 基类 + LangGraph 图定义 + Triage Agent 可对话

| 日期 | 后端任务 | 前端任务 |
|------|---------|---------|
| Day 1 | BaseAgent 抽象类 + AgentRegistry | — |
| Day 2 | LangGraph 图定义: state.py + graph.py (基础节点链路) | — |
| Day 3 | Triage Agent: agent.py + prompt.py | WebSocket 连接封装 |
| Day 4 | Supervisor Agent: 路由逻辑 + 会话管理 | 对话 UI 组件 (基础消息列表) |
| Day 5 | Agent 流式输出: stream.py (SSE 事件格式设计) | 流式消息渲染 |
| Day 6 | API routes: POST /consult + WebSocket /ws/{session_id} | 对话输入框 + 发送逻辑 |
| Day 7 | 集成测试: 用户输入 → Triage Agent → 输出 | 端到端对话演示 |

**里程碑**: 用户能输入「我头痛两天了」, Triage Agent 返回分诊结果, 前端流式渲染

**可扩展预留**: BaseAgent 预留 `tool_calling` 和 `hook` 接口, 后期可通过 Plugin 注入

---

### 第 3 周: Skill 系统 + Doctor Agent

**目标**: Doctor Agent + Skill 加载机制 + 2 个科室 Skill

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | Skill 系统: base.py + loader.py + registry.py | 定义 Skill 抽象: system_prompt + knowledge + tools |
| Day 2 | 内科 Skill: internal_medicine | system_prompt + 常见疾病知识 |
| Day 3 | 皮肤科 Skill: dermatology | 同上 |
| Day 4 | **心理科 Skill: mental_health** | PHQ-9/GAD-7 筛查、危机检测提示词、心理评估流程 |
| Day 5 | Doctor Agent: agent.py + prompt.py | 通用诊断推理框架 |
| Day 6 | Doctor + Skill 集成 | Agent 按患者主诉自动加载对应 Skill |
| Day 7 | 测试: 内科/皮肤科/心理科各 10 个测试病例 | 验证分诊→诊断流程 |

**里程碑**: 输入「脸上起红疹, 痒」 → Triage → 皮肤科 Doctor Agent → 诊断推理 + 治疗方案; 心理科支持 PHQ-9 筛查和危机信号检测

**可扩展预留**: Skill 支持未来从外部包动态加载 (plugin_loader.py 预留接口)

---

### 第 4 周: RAG 知识库 + Review Agent

**目标**: 知识库可检索 + Review Agent 可审查处方

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | Qdrant 集成 + 向量化 Pipeline | Qdrant 客户端 + Embedding 模型选型 |
| Day 2 | 知识文档加载: loader.py | PDF/Markdown 解析 + 分块策略 |
| Day 3 | RAG 查询: rag.py | 检索 + 重排序 + 上下文组装 |
| Day 4 | 加载首批知识: 药品说明书 + 内科/皮肤科指南 | 实际数据入库 |
| Day 5 | Review Agent: agent.py + prompt.py | 8 维审查矩阵实现 |
| Day 6 | 审查规则: 药物相互作用 + 禁忌症 (硬编码规则) | 规则引擎骨架 |
| Day 7 | Doctor + Review 联调 | 诊断后自动触发审查, 反馈结果 |

**里程碑**: Doctor 开出处方 → Review Agent 审查 → 标记潜在问题 → 返回审查报告

**可扩展预留**: RAG 接口设计与 GraphRAG 同构, 未来可切换; 审查规则设计为可插拔 checker

---

### 第 5 周: 记忆系统 + 病历管理 + 随访 Agent

**目标**: 跨会话记忆 + 结构化病历 + SOAP 输出 + 随访管理

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | Mem0 集成: 安装 + 基础配置 | 评估 Mem0 API, 建立连接 |
| Day 2 | 情景记忆: episodic.py | 历史就诊记录存储 + 语义检索 |
| Day 3 | 语义记忆: semantic.py | 患者画像 (过敏史/既往史/家族史) 管理 |
| Day 4 | 记忆管理器: manager.py | 记忆分层检索 + 注入到 Agent 上下文 |
| Day 5 | SOAP 病历生成 + 随访表结构扩展 | Doctor Agent 输出结构化病历; followup 表补充字段 |
| Day 6 | **Follow-up Agent: agent.py + prompt.py + scheduler.py** | 基于病历自动生成随访计划、用药提醒、复诊建议 |
| Day 7 | 病历 API + 前端病历页 + 复诊/随访演示 | 就诊历史时间线 + 随访日程 + 端到端演示 |

**里程碑**: 首诊 → 记录病历 → 自动生成随访计划 → 复诊 Agent 加载历史 → 基于病史继续问诊

**可扩展预留**: Mem0 的 Graph DB 模式预留 (后期关联实体关系); 随访支持多渠道推送 (短信/邮件) 接口预留

---

### 第 6 周: 前端核心功能完成

**目标**: 完整的 Web 用户体验

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | 问诊对话页完整 UI | 消息气泡 + 病历卡片实时生成 + 加载状态 |
| Day 2 | 病历页面 | 时间线 + 详情展开 + 处方展示 |
| Day 3 | 个人中心 + 健康档案 | 基础信息编辑 + 病史管理 + 过敏史 |
| Day 4 | 结束总结页 | 就诊摘要 + 处方 + 医嘱 + 复诊建议 |
| Day 5 | 移动端适配 | 响应式布局, 手机可用 |
| Day 6 | 页面串联 + 路由完善 | 端到端用户流程可用 |
| Day 7 | UI 打磨 + 错误处理 | 加载态/空态/错误态全覆盖 |

**里程碑**: 完整的 Web 问诊体验, 移动端可用, 所有页面无死链

**可扩展预留**: 前端组件化设计, 未来桌宠/小程序可直接复用 API

---

### 第 7 周: 安全 + Guardrail + 会诊协调 + 集成测试

**目标**: 安全加固 + Coordinator Agent 实现 + 全部集成测试通过

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | 认证系统: OAuth 2.0 + JWT | 注册/登录/Token 刷新 |
| Day 2 | 前端认证接入 + **Coordinator Agent 接口定义** | 登录页 + 路由守卫; 会诊协议数据结构 (consultation_protocol.py) |
| Day 3 | Identity Verification Guard + **Coordinator Agent 核心逻辑** | 身份验证; 多 Agent 协调状态机、专家邀请/汇总流程 |
| Day 4 | PII 脱敏 (guardrails/pii_sanitizer.py) + **会诊前端页面** | LLM 请求前脱敏; 会诊详情展示、专家意见聚合 UI |
| Day 5 | Emergency Detector + **会诊端到端联调** | 关键词 + 语义双重检测; 多科室会诊演示 |
| Day 6 | 集成测试: 完整就诊流程 + 会诊流程 | 模拟 10 个完整就诊场景 + 3 个会诊场景 |
| Day 7 | 审计日志 | 所有 Agent 操作记录 + LLM 调用日志 |

**里程碑**: 安全扫描通过, Coordinator 支持多科室会诊, 所有测试通过, 审计日志完整

**可扩展预留**: Guardrail 的 L2/L3 分级接口预留; OAuth 支持第三方登录接口预留; 会诊支持外部专家接入接口预留

---

### 第 8 周: 部署 + 文档 + 发布

**目标**: 开源发布 v0.1.0

| 日期 | 任务 | 说明 |
|------|------|------|
| Day 1 | Docker Compose 生产配置 | 多阶段构建 + 环境变量 |
| Day 2 | 后端 API 文档 | OpenAPI + 关键流程文档 |
| Day 3 | README + 快速开始 | 5 分钟本地启动指南 |
| Day 4 | 贡献者指南 CONTRIBUTING.md | Issue/PR 模板 + 开发流程 |
| Day 5 | 种子数据 + Demo 脚本 | 一键加载示例知识 + 测试病例 |
| Day 6 | 最终回归测试 | 全流程跑通 |
| Day 7 | v0.1.0 发布 | GitHub Release + 演示视频 |

**里程碑**: GitHub 仓库公开, 任何人可 `docker-compose up` 启动完整系统

**可扩展预留**: CI/CD 工作流骨架 (GitHub Actions), 保留未来扩展的空间

---

## 8 周甘特图

```
任务                    W1    W2    W3    W4    W5    W6    W7    W8
─────────────────────────────────────────────────────────────────────
项目初始化              ████
数据模型                ████
LLM 抽象层             ████
Agent 框架                    ████
Triage Agent                  ████
Skill 系统                          ████
Doctor Agent                        ████
Mental Health Skill                ████
RAG 知识库                               ████
Review Agent                              ████
记忆系统                                        ████
病历管理                                        ████
Follow-up Agent                                 ████
前端核心                                              ████
Coordinator Agent                                              ████
安全+Guardrail                                                 ████
集成测试                                                  ██████
部署+文档                                                          ████
发布                                                                  ████
─────────────────────────────────────────────────────────────────────
```

---

## 可扩展预留点总清单

以下所有预留点均只定义接口/骨架, **不实现具体逻辑**, 确保后期可插拔:

| 预留点 | 位置 | 预留方式 | 未来用途 |
|--------|------|---------|---------|
| **Agent Hook 系统** | `agents/base.py` | `on_pre_process`, `on_post_process` 空方法 | Plugin 注入 |
| **动态 Skill 加载** | `agents/doctor/skills/loader.py` | 支持从外部目录/包加载 | 社区贡献 Skill |
| **Plugin SDK** | `plugins/sdk/base.py` | 定义 Plugin 基类 + 钩子 | 第三方扩展 |
| **GraphRAG** | `knowledge/graph_rag.py` | 接口与 `rag.py` 同构 | 知识图谱检索 |
| **Multi-provider LLM** | `llm/providers/` | `BaseLLMClient` 抽象 | 新模型接入 |
| **L2/L3 Guardrail** | `guardrails/` | 接口定义, 异步执行 | 异步审查 |
| **FHIR 导出** | `models/` 数据模型 | 字段与 FHIR 资源对齐 | 标准病历交换 |
| **专家在环** | `agents/review/human_review.py` | Review Agent 预留人工审核输出 | 医生审核 |
| **监控** | `infrastructure/monitoring/` | Prometheus metrics 预留 | 生产运维 |
| **CI/CD** | `.github/workflows/` | 基础 workflow 骨架 | 自动测试/发布 |

---

## 技术栈速览

| 层 | 技术 | 选型理由 |
|----|------|---------|
| Agent 编排 | LangGraph | 状态图灵活, 支持流式, 生态好 |
| 后端 | FastAPI + Python 3.12 | 异步原生, 性能好, AI 生态 |
| 数据库 | PostgreSQL 16 + pgvector | 结构化 + 向量一体 |
| 缓存/消息 | Redis 7 | 会话管理 + Agent 通信 |
| 向量库 | Qdrant | 云原生, Docker 一键起 |
| 记忆 | Mem0 | 生产级记忆层, 开箱即用 |
| 前端 | Next.js 14 + React + shadcn/ui | SSR + 组件化 |
| LLM | Claude 4 / GPT-4o + Ollama (本地) | 主模型 + 降级 |
| 部署 | Docker Compose | 低成本起步 |

---

## 成功标准 (v0.1.0)

1. **核心闭环**: 用户输入症状 → 导诊 → 诊断 → 审查 → 输出结构化病历
2. **多科室**: 至少 2 个科室 Skill 可用 (内科、皮肤科)
3. **记忆**: 跨会话识别用户, 复诊自动加载历史
4. **知识库**: RAG 可检索药品说明和指南
5. **安全**: 身份验证、PII 脱敏、紧急检测
6. **可复现**: 任何人在一台机器上 `docker-compose up` 即可运行
7. **文档**: README + API 文档 + 贡献指南
