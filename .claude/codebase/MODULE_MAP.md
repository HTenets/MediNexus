# MediNexus 模块图谱 (Module Map)

> 此文件是项目代码结构的权威索引。AI 在修改代码前应查阅此文件理解模块职责与边界。
> 状态标记: ✅ 已完成 | 🏗 进行中 | 📋 待实现 | 🔌 预留接口
> 决策基线: 患者自助问诊(A) | 参考级准确度 | Ollama 默认 + BYO Key 降级 | 中文为主英文备用 | 紧急演示级
> 详细设计决策见 `BUILD_STATUS.md` 总体进度章节和 `CONVENTIONS.md` 第 1a-1d 节。

---

## 1. 后端核心层 `backend/`

### 1.1 Agent 系统 `backend/agents/`

| 文件 | 职责 | 关键导出 | 依赖 | 状态 |
|------|------|---------|------|------|
| `__init__.py` | 包入口, 导出 BaseAgent + AgentRegistry | `BaseAgent, AgentRegistry, registry` | base.py, registry.py | ✅ |
| `base.py` | Agent 抽象基类, 定义生命周期和 Tool 接口 | `class BaseAgent(ABC)` | `HandoverManifest` | ✅ |
| `registry.py` | 全局 Agent 注册中心 (单例) | `class AgentRegistry`, `registry` 实例 | BaseAgent | ✅ |

#### BaseAgent 生命周期

```
context → on_pre_process(context) → run(context) → on_post_process(manifest) → HandoverManifest
```

- `run(context: dict) -> HandoverManifest` — 抽象方法, 子类必须实现
- `on_pre_process(context) -> context` — Plugin 注入点 (身份验证/PII 脱敏等)
- `on_post_process(manifest) -> manifest` — Plugin 注入点 (审计/增强等)
- `register_tool(name, fn)` — 注册可调用工具
- `execute_tool(name, **kwargs)` — 执行已注册工具

---

### 1.2 Triage Agent `backend/agents/triage/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | TriageAgent 实现: 症状评估/科室分诊/紧急度判断 | `class TriageAgent(BaseAgent)` | ✅ |
| `prompt.py` | 系统提示词 (中英双语) | `TRIAGE_SYSTEM_PROMPT`, `TRIAGE_EXTRACTION_PROMPT` | ✅ |

**接口:**
- `run(context) -> HandoverManifest(context.triage_result)`
- `triage_result` 格式: `{urgency, department, reason, key_info_gaps[]}`
- 双模式: LLM 智能分诊 ↔ 关键词降级分诊
- 紧急度层级: `emergency > urgent > routine`

---

### 1.3 Doctor Agent `backend/agents/doctor/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | DoctorAgent (当前为 stub) | `class DoctorAgent(BaseAgent)` | 🏗 |
| `prompt.py` | 诊断提示词 | — | 📋 |
| `diagnosis_flow.py` | 诊断状态机定义 | `DiagnosisState` (INITIAL→HISTORY_TAKING→DIFFERENTIAL→TREATMENT→COMPLETED) | ✅ |

#### Skill 子系统 `backend/agents/doctor/skills/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `base.py` | Skill 抽象基类 (system_prompt + knowledge + tools) | 🏗 |
| `loader.py` | Skill 动态加载器 (支持外部目录加载) | 🏗 |
| `registry.py` | Skill 注册中心 | 🏗 |
| `builtin/internal_medicine/skill.py` | 内科 Skill | 📋 |
| `builtin/dermatology/skill.py` | 皮肤科 Skill | 📋 |
| `builtin/ent/skill.py` | 耳鼻喉科 Skill | 📋 |
| `builtin/mental_health/skill.py` | 心理科 Skill (含 PHQ-9/GAD-7) | 📋 |

---

### 1.4 Review Agent `backend/agents/review/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | ReviewAgent (当前为 stub) | `class ReviewAgent(BaseAgent)` | 🏗 |
| `prompt.py` | 审查提示词 | — | 📋 |
| `rules/drug_interaction.py` | 药物相互作用检查规则 | — | 📋 |
| `rules/contraindication.py` | 禁忌症检查规则 | — | 📋 |
| `checkers/__init__.py` | 可插拔检查器骨架 | — | 📋 |

---

### 1.5 Coordinator Agent `backend/agents/coordinator/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | CoordinatorAgent (多科室会诊协调) | `class CoordinatorAgent(BaseAgent)` | 🏗 |
| `prompt.py` | 会诊提示词 | — | 📋 |
| `consultation_protocol.py` | 会诊协议/状态机 | — | 📋 |

---

### 1.6 Followup Agent `backend/agents/followup/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | FollowupAgent (随访管理) | `class FollowupAgent(BaseAgent)` | 🏗 |
| `prompt.py` | 随访提示词 | — | 📋 |
| `scheduler.py` | 随访计划调度 | — | 📋 |

---

### 1.7 编排层 `backend/orchestration/`

| 文件 | 职责 | 关键导出 | 依赖 | 状态 |
|------|------|---------|------|------|
| `state.py` | 会话状态 + LangGraph TypedDict | `SessionState`, `GraphState` | — | ✅ |
| `graph.py` | ConsultationGraph (LangGraph 状态图构建) | `class ConsultationGraph` | GraphState | ✅ |
| `supervisor.py` | SupervisorAgent (路由 + 会话管理) | `class SupervisorAgent` | AgentRegistry, SessionState, HandoverManifest | ✅ |
| `stream.py` | StreamManager (流式事件处理) | `class StreamManager` | — | ✅ |

#### 会话路由逻辑 (supervisor.py)

```
triage → (emergency → 原地紧急处理)
       → (routine) → doctor → (需审查) → review → followup → complete
                            → (无需审查) → followup → complete
       → coordinator → review → (不通过→回到doctor) → followup → complete
```

---

### 1.8 API 层 `backend/app/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `main.py` | FastAPI 入口 + WebSocket 端点 | ✅ |
| `config.py` | pydantic-settings 配置 (env_prefix=MEDINEXUS_) | ✅ |
| `api/router.py` | 路由汇总 | ✅ |
| `api/consultation.py` | 问诊 API + WebSocket 处理 | ✅ |
| `api/patients.py` | 患者 API | 🏗 |
| `api/medical_records.py` | 病历 API | 🏗 |
| `api/health.py` | 健康检查 | ✅ |
| `core/database.py` | PostgreSQL 连接 (SQLAlchemy async) | ✅ |
| `core/redis.py` | Redis 连接 | 🏗 |
| `core/auth.py` | OAuth 2.0 + JWT | 📋 |
| `core/security.py` | PII 脱敏/加密 | 📋 |
| `core/dependencies.py` | FastAPI 依赖注入 | 📋 |
| `middlewares/auth.py` | 认证中间件 | 📋 |
| `middlewares/logging.py` | 请求日志中间件 | 🏗 |
| `middlewares/rate_limit.py` | 限流中间件 | 📋 |

---

### 1.9 数据模型 `backend/app/models/`

| 文件 | 表名 | 关键字段 | 状态 |
|------|------|---------|------|
| `patient.py` | `patients` | id, name, dob, gender, allergies, history | ✅ |
| `consultation.py` | `consultations` | id, patient_id, status, diagnosis, created_at | ✅ |
| `prescription.py` | `prescriptions` | — | 🏗 |
| `medical_history.py` | `medical_histories` | — | 🏗 |
| `followup.py` | `followups` (预留表) | — | 📋 |
| `audit_log.py` | `audit_logs` | — | 📋 |

---

### 1.10 Schema `backend/app/schemas/`

| 文件 | 关键模型 | 状态 |
|------|---------|------|
| `agent.py` | `HandoverManifest` (facts, pending_questions, risk_flags, evidence_level, context) | ✅ |
| `consultation.py` | `ConsultationStartRequest`, `ConsultationStartResponse`, `ConsultationStatusResponse` | ✅ |
| `patient.py` | 患者 Pydantic 模型 | 🏗 |
| `memory.py` | 记忆数据格式 | 📋 |

---

### 1.11 LLM 层 `backend/llm/`

| 文件 | 职责 | 关键方法 | 状态 |
|------|------|---------|------|
| `client.py` | BaseLLMClient 抽象类 | `chat()`, `chat_stream()` | ✅ |
| `providers/openai.py` | OpenAI / 兼容接口实现 | — | ✅ |
| `providers/anthropic.py` | Anthropic Claude 实现 | — | ✅ |
| `providers/ollama.py` | 本地模型 (Ollama) 实现 | — | ✅ |

---

### 1.12 知识库 `backend/knowledge/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `rag.py` | RAGQuery (Qdrant 向量检索) | 🏗 |
| `vector_store.py` | Qdrant 客户端操作 | 🏗 |
| `loader.py` | 文档加载/分块 Pipeline | 📋 |
| `graph_rag.py` | GraphRAGQuery (预留, 接口与 RAGQuery 同构) | 📋 |

---

### 1.13 记忆系统 `backend/memory/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `manager.py` | MemoryManager (三层记忆协调) | 📋 |
| `working.py` | 工作记忆 (Redis TTL) | 📋 |
| `stores/episodic.py` | 情景记忆 (历史就诊) | 📋 |
| `stores/semantic.py` | 语义记忆 (患者画像) | 📋 |

---

### 1.14 Guardrails `backend/guardrails/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `emergency_detector.py` | 紧急信号检测 (关键词+语义, 中英双语) | 🏗 |
| `pii_sanitizer.py` | PII 脱敏 | 📋 |
| `identity_verifier.py` | 身份验证 | 📋 |

---

### 1.15 Celery 任务 `backend/workers/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `tasks.py` | 后台异步任务定义 | 📋 |

---

## 2. 前端 `frontend/`

| 文件/目录 | 职责 | 状态 |
|-----------|------|------|
| `src/app/page.tsx` | 首页 | ✅ |
| `src/app/layout.tsx` | 全局布局 | ✅ |
| `src/app/consultation/page.tsx` | 问诊对话页 | 🏗 |
| `src/app/records/page.tsx` | 病历页 | 🏗 |
| `src/app/profile/page.tsx` | 个人中心 | 🏗 |
| `src/components/chat/ChatContainer.tsx` | 对话容器 | ✅ |
| `src/components/chat/ChatMessage.tsx` | 消息气泡 | ✅ |
| `src/components/chat/ChatInput.tsx` | 输入框 | ✅ |
| `src/lib/api.ts` | API 客户端 | ✅ |
| `src/lib/websocket.ts` | WebSocket 客户端 (含自动重连) | ✅ |
| `src/stores/` | 状态管理 | 📋 |

---

## 3. 插件系统 `plugins/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `sdk/base.py` | BasePlugin 抽象类 (initialize/shutdown) | 📋 |
| `sdk/hooks.py` | PluginHooks (on_agent_pre_process / on_agent_post_process) | 📋 |
| `examples/drug_lookup/` | 药品查询插件示例 | 📋 |

---

## 4. 测试 `tests/`

| 文件 | 覆盖范围 | 状态 |
|------|---------|------|
| `integration/test_consultation_flow.py` | 完整就诊流程 (含 12 个测试用例) | ✅ |
| `integration/test_agent_communication.py` | Agent 间通信 | ✅ |
| `unit/agents/` | Agent 单元测试 | 📋 |
| `unit/knowledge/` | 知识库单元测试 | 📋 |
| `unit/memory/` | 记忆系统单元测试 | 📋 |

---

## 5. 基础设施 `infrastructure/`

| 文件 | 用途 | 状态 |
|------|------|------|
| `docker/Dockerfile.backend` | 后端镜像 | 🏗 |
| `docker/Dockerfile.frontend` | 前端镜像 | 🏗 |
| `docker/Dockerfile.worker` | Celery Worker 镜像 | 📋 |
| `monitoring/prometheus.yml` | Prometheus 配置 (预留) | 📋 |
