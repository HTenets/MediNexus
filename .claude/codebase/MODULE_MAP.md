# MediNexus 模块图谱 (Module Map)

> 此文件是项目代码结构的权威索引。AI 在修改代码前应查阅此文件理解模块职责与边界。
> 状态标记: ✅ 已完成 | 🏗 进行中 | 📋 待实现 | 🔌 预留接口
> 决策基线: 患者自助问诊(A) | 参考级准确度 | Ollama 默认 + BYO Key 降级 | 中文为主英文备用 | 紧急演示级
> 版本: v0.1.0 (2026-06-22)

---

## 1. 后端核心层 `backend/`

### 1.1 Agent 系统 `backend/agents/`

| 文件 | 职责 | 关键导出 | 依赖 | 状态 |
|------|------|---------|------|------|
| `__init__.py` | 包入口, 导入所有 Agent 触发注册 | `BaseAgent, AgentRegistry, registry` | base.py, registry.py, triage/agent, doctor/agent | ✅ |
| `base.py` | Agent 抽象基类, 定义生命周期和 Tool 接口 | `class BaseAgent(ABC)` | `HandoverManifest` | ✅ |
| `registry.py` | 全局 Agent 注册中心 (单例) | `class AgentRegistry`, `registry` 实例 | BaseAgent | ✅ |

**已注册 Agent:** triage, doctor, review, coordinator, followup — 共 5 个

---

### 1.2 Triage Agent `backend/agents/triage/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | TriageAgent: 症状评估/科室分诊/紧急度判断 | `class TriageAgent(BaseAgent)` | ✅ |
| `prompt.py` | 系统提示词 (中英双语) | `TRIAGE_SYSTEM_PROMPT`, `TRIAGE_EXTRACTION_PROMPT` | ✅ |

---

### 1.3 Doctor Agent `backend/agents/doctor/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | DoctorAgent (LLM + 规则双模式, Skill 集成, 降级标注) | `class DoctorAgent(BaseAgent)` | ✅ |
| `prompt.py` | 诊断提示词 (Ollama 优化: 结构化 JSON 输出) | `DIAGNOSIS_SYSTEM_PROMPT` | ✅ |
| `diagnosis_flow.py` | 诊断状态机定义 | `DiagnosisState` (INITIAL→HISTORY_TAKING→DIFFERENTIAL→TREATMENT→COMPLETED) | ✅ |

#### Skill 子系统 `backend/agents/doctor/skills/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `base.py` | Skill 抽象基类 (system_prompt + knowledge + tools + match_symptoms) | ✅ |
| `loader.py` | Skill 动态加载器 (内置 4 个 Skill, 外部加载预留 v0.3.0+) | ✅ |
| `registry.py` | Skill 注册中心 (含 auto_route: 科室匹配→症状评分→首注册降级) | ✅ |
| `builtin/internal_medicine/skill.py` | 内科 Skill — 呼吸/消化/心血管/内分泌 | ✅ |
| `builtin/dermatology/skill.py` | 皮肤科 Skill — 湿疹/荨麻疹/痤疮/真菌 | ✅ |
| `builtin/ent/skill.py` | 耳鼻喉科 Skill — 耳/鼻/咽喉常见病 | ✅ |
| `builtin/mental_health/skill.py` | 心理科 Skill — PHQ-9/GAD-7 + 自杀危机检测 | ✅ |

---

### 1.4 Review Agent `backend/agents/review/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | ReviewAgent (独立 RAG 验证 + 鉴别诊断检查 + 证据等级) | `class ReviewAgent(BaseAgent)` | ✅ |
| `prompt.py` | 8 维审查完整提示词 (药物/禁忌/剂量/过敏/证据/重复/年龄/鉴别) | `REVIEW_PROMPT`, `REVIEW_SYSTEM_PROMPT` | ✅ |
| `rules/drug_interaction.py` | 药物相互作用检查 (14 组药物对 + severity/mechanism/recommendation) | `check_drug_interaction`, `check_drug_in_context` | ✅ |
| `rules/contraindication.py` | 禁忌症+过敏+年龄限制检查 (完整数据 + 3 个检查函数) | `check_contraindication`, `check_allergy`, `check_age_restriction`, `check_all_contraindications` | ✅ |
| `checkers/__init__.py` | 可插拔检查器注册框架 + run_all_checkers 聚合 | `CHECKERS`, `register_checker()`, `run_all_checkers()` | ✅ |
| `checkers/drug_interaction_checker.py` | 药物相互作用检查器 (注册为 drug_interaction) | — | ✅ |
| `checkers/contraindication_checker.py` | 禁忌症+过敏+年龄限制检查器 (注册为 contraindication) | — | ✅ |

---

### 1.5 Coordinator Agent `backend/agents/coordinator/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | CoordinatorAgent (多科室会诊: 6 种复杂性触发器 + 专科意见收集 + 综合报告) | `class CoordinatorAgent(BaseAgent)` | ✅ |
| `prompt.py` | 会诊提示词 | `COORDINATOR_SYSTEM_PROMPT` | ✅ |
| `consultation_protocol.py` | 会诊协议: 7 阶段状态机 + SpecialistOpinion + ConsultationReport | `ConsultationPhase`, `SpecialistOpinion`, `ConsultationReport` | ✅ |

---

### 1.6 Followup Agent `backend/agents/followup/`

| 文件 | 职责 | 关键导出 | 状态 |
|------|------|---------|------|
| `agent.py` | FollowupAgent (随访计划 + 用药提醒 + 5 种计划模板) | `class FollowupAgent(BaseAgent)` | ✅ |
| `prompt.py` | 随访提示词 | `FOLLOWUP_SYSTEM_PROMPT` | ✅ |
| `scheduler.py` | 随访排程器 (generate_schedule + get_plan_for_diagnosis) | `FollowupPlan`, `ScheduledFollowup`, `generate_schedule()` | ✅ |

---

### 1.7 编排层 `backend/orchestration/`

| 文件 | 职责 | 关键导出 | 依赖 | 状态 |
|------|------|---------|------|------|
| `state.py` | 会话状态 + LangGraph TypedDict | `SessionState`, `GraphState` | — | ✅ |
| `graph.py` | ConsultationGraph (LangGraph 状态图构建) | `class ConsultationGraph` | GraphState | ✅ |
| `supervisor.py` | SupervisorAgent (Redis 会话 + MemoryManager 注入 + 路由) | `class SupervisorAgent` | AgentRegistry, HandoverManifest, MemoryManager | ✅ |
| `stream.py` | StreamManager (流式事件处理) | `class StreamManager` | — | ✅ |

---

### 1.8 API 层 `backend/app/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `main.py` | FastAPI 入口 + WebSocket 端点 | ✅ |
| `config.py` | pydantic-settings 配置 (env_prefix=MEDINEXUS_) | ✅ |
| `api/router.py` | 路由汇总 (含 mock_data 注册) | ✅ |
| `api/consultation.py` | 问诊 API + WebSocket + SOAP complete | ✅ |
| `api/mock_data.py` | 10 个 mock 端点 (三路知识源/SOAP/档案/Dashboard/状态/患者) | ✅ |
| `api/patients.py` | 患者 CRUD API (create/list/get/update/delete + demo 数据) | ✅ |
| `api/medical_records.py` | 病历 API (get/list/create + demo 数据) | ✅ |
| `api/health.py` | 健康检查 | ✅ |
| `core/database.py` | PostgreSQL 连接 (SQLAlchemy async) | ✅ |
| `core/redis.py` | Redis 连接 | ✅ |
| `core/auth.py` | JWT 认证 (create_token/refresh/decode/get_current_user/get_optional_user) | ✅ |
| `core/security.py` | PII 检测/脱敏/掩码 (正则: 手机/座机/身份证/邮箱) | ✅ |
| `core/dependencies.py` | FastAPI 依赖注入 (get_session_id/get_current_patient_id/pagination_params) | ✅ |
| `middlewares/auth.py` | 认证中间件 (JWT 可选, Demo 模式跳过) | ✅ |
| `middlewares/logging.py` | 请求日志中间件 | ✅ |
| `middlewares/rate_limit.py` | 限流中间件 (60 req/min per IP, 已接入 main.py) | ✅ |

---

### 1.9 数据模型 `backend/app/models/`

| 文件 | 表名 | 关键字段 | 状态 |
|------|------|---------|------|
| `patient.py` | `patients` | id, name, gender, dob, phone, created_at | ✅ |
| `consultation.py` | `consultations` | id, patient_id, status, subjective, objective, assessment, plan, diagnosis | ✅ |
| `prescription.py` | `prescriptions` | — | 🏗 (v0.2.0+ 业务逻辑) |
| `medical_history.py` | `medical_histories` | id, patient_id, history_type, content(JSON) | ✅ |
| `followup.py` | `followups` | id, patient_id, consultation_id, status, notes | 🏗 (v0.2.0+ 业务逻辑) |
| `audit_log.py` | `audit_logs` | id, action, details(JSON), created_at | ✅ |

---

### 1.10 Schema `backend/app/schemas/`

| 文件 | 关键模型 | 状态 |
|------|---------|------|
| `agent.py` | `HandoverManifest` (facts, pending_questions, risk_flags, evidence_level, context) | ✅ |
| `consultation.py` | `ConsultationStartRequest/Response`, `ConsultationStatusResponse`, `SOAPCompletionRequest` | ✅ |
| `patient.py` | 患者 Pydantic 模型 (PatientCreate/Update/Response/ListResponse) | ✅ |
| `memory.py` | `MemoryEntry` (session_id, patient_id, content, memory_type) | ✅ |

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

| 文件 | 职责 | 关键导出 | 依赖 | 状态 |
|------|------|---------|------|------|
| `__init__.py` | 包入口 | 全部 15+ 公共类/函数 | — | ✅ |
| `source.py` | 三路知识源定义 + 置信度配置 + 数据结构 | `SourceType`, `SourceConfig`, `RetrievedChunk`, `FusionResult` | — | ✅ |
| `chunker.py` | 差异化分块策略 (semantic/hierarchical/recursive) | `SemanticChunker`, `HierarchicalChunker`, `RecursiveChunker` | source.py | ✅ |
| `vector_store.py` | Qdrant 多集合 CRUD | `VectorStore` | qdrant_client | ✅ |
| `bm25_fallback.py` | BM25 全文搜索降级 | `BM25Index`, `BM25Fallback` | — | ✅ |
| `retriever.py` | 多源融合检索: RRF + Z-score + 置信度加权 | `MultiSourceRetriever` | source.py, vector_store.py, bm25_fallback.py | ✅ |
| `rag.py` | RAGQuery 主入口: 三路召回 + 融合 + LLM Context 格式化 | `RAGQuery` | retriever.py, graph/ | ✅ |
| `graph_rag.py` | GraphRAGQuery (接口预留, 包装 RAG + KG) | `GraphRAGQuery` | rag.py | ✅ |
| `loader.py` | 文档加载 Pipeline + 种子数据 | `DocumentLoader`, `SEED_*` | chunker.py, vector_store.py | ✅ |

#### 知识图谱子系统 `backend/knowledge/graph/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `__init__.py` | 包入口 | ✅ |
| `client.py` | KnowledgeGraph: 症状→疾病一跳映射, Neo4j 就绪/内存兜底 | ✅ |
| `symptom_graph.py` | SymptomGraphBuilder: 100+ 症状-疾病关系, JSON 导出 | ✅ |

---

### 1.13 记忆系统 `backend/memory/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `manager.py` | MemoryManager (三层记忆统一检索 + 会话代理) | ✅ |
| `working.py` | 工作记忆 (Redis: current_agent + context, TTL 3600s) | ✅ |
| `stores/episodic.py` | 情景记忆 (PostgreSQL 历史就诊 SOAP) | ✅ |
| `stores/semantic.py` | 语义记忆 (PostgreSQL 患者画像) | ✅ |

---

### 1.14 Guardrails `backend/guardrails/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `emergency_detector.py` | 紧急信号检测 (50+ 关键词 + 7 条正则 + 5 类响应) | ✅ |
| `pii_sanitizer.py` | PII 脱敏 (手机/身份证/邮箱/座机 + 掩码) | ✅ |
| `identity_verifier.py` | 身份验证 (ID 校验 + JWT 可注入 + 审计日志) | ✅ |

---

### 1.15 Celery 任务 `backend/workers/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `tasks.py` | Celery 异步任务 (send_followup_reminder/process_async_analysis/cleanup_expired_sessions + lazy Celery app init) | ✅ |

---

## 2. 前端 `frontend/`

| 文件/目录 | 职责 | 状态 |
|-----------|------|------|
| `src/app/layout.tsx` | 全局布局 | ✅ |
| `src/app/globals.css` | Tailwind 入口 + web-design 设计令牌 | ✅ |
| `src/app/page.tsx` | 首页 (营销 + 9 功能卡片) | ✅ |
| `src/app/consultation/page.tsx` | 问诊对话页 (WebSocket 实时 + Agent 阶段指示器 + 快捷症状) | ✅ |
| `src/app/consultation/analysis/page.tsx` | 多维知识源分析 (三路 API) | ✅ |
| `src/app/consultation/review/page.tsx` | 方案合规复核 (SOAP + 禁忌症) | ✅ |
| `src/app/summary/page.tsx` | 问诊总结 (SOAP 记录) | ✅ |
| `src/app/records/page.tsx` | 健康档案 (mock API) | ✅ |
| `src/app/profile/page.tsx` | 个人中心 (mock API) | ✅ |
| `src/app/dashboard/page.tsx` | 数字孪生全景 (mock API) | ✅ |
| `src/app/patients/page.tsx` | 患者管理 (mock API) | ✅ |
| `src/app/system-status/page.tsx` | 系统状态 (mock API) | ✅ |
| `src/app/settings/page.tsx` | 设置 (React 组件) | ✅ |
| `src/app/upload-report/page.tsx` | 报告上传 (拖拽) | ✅ |
| `src/app/login/page.tsx` | 登录页 (角色选择 + 表单) | ✅ |
| `src/app/design-preview/page.tsx` | 设计预览索引 | ✅ |
| `src/components/layout/AppShell.tsx` | Sidebar + TopBar 布局壳 | ✅ |
| `src/components/ui/NavBar.tsx` | 导航栏 (已废弃, 被 AppShell 替代) | 🔌 |
| `src/components/ui/DisclaimerBanner.tsx` | 医疗免责声明 (standard/emergency) | ✅ |
| `src/components/ui/LoadingState.tsx` | 加载态 | ✅ |
| `src/components/ui/ErrorState.tsx` | 错误态 | ✅ |
| `src/components/ui/EmptyState.tsx` | 空态 | ✅ |
| `src/components/chat/ChatContainer.tsx` | 对话容器 (WebSocket 事件绑定) | ✅ |
| `src/components/chat/ChatMessage.tsx` | 消息气泡 (Agent 标签 + 流式渲染) | ✅ |
| `src/components/chat/ChatInput.tsx` | 输入框 (自动缩放 + Enter 发送) | ✅ |
| `src/lib/api.ts` | REST API 客户端 | ✅ |
| `src/lib/websocket.ts` | WebSocket 客户端 (自动重连 + 6 事件) | ✅ |
| `src/stores/consultationStore.ts` | 状态管理 (预留) | 🔌 |
| `tailwind.config.js` | 自定义颜色 medical-* + 字体 | ✅ |
| `postcss.config.js` | PostCSS 插件 | ✅ |
| `next.config.js` | API 代理 | ✅ |
| `Dockerfile` | 多阶段构建 | ✅ |

---

## 3. 插件系统 `plugins/`

| 文件 | 职责 | 状态 |
|------|------|------|
| `sdk/base.py` | BasePlugin 抽象类 (initialize/shutdown) | 🔌 (v0.3.0+) |
| `sdk/hooks.py` | PluginHooks (on_agent_pre_process / on_agent_post_process) | 🔌 (v0.3.0+) |
| `examples/drug_lookup/` | 药品查询插件示例 | 🔌 (v0.3.0+) |

---

## 4. 测试 `tests/`

| 文件 | 覆盖范围 | 测试数 | 状态 |
|------|---------|--------|------|
| `integration/test_consultation_flow.py` | 完整就诊流程 | 12 | ✅ |
| `integration/test_agent_communication.py` | Agent 通信协议 | 11 | ✅ |
| `unit/agents/test_skill_system.py` | Skill 系统 | 19 | ✅ |
| `unit/agents/test_doctor_agent.py` | Doctor Agent | 16 | ✅ |
| `unit/agents/test_review_agent.py` | Review Agent | 6 | ✅ |
| `unit/agents/test_coordinator.py` | Coordinator | 13 | ✅ |
| `unit/agents/test_followup_agent.py` | Followup | 10 | ✅ |
| `unit/guardrails/test_guardrails.py` | Guardrails | 22 | ✅ |
| `unit/knowledge/test_source.py` | 知识源定义 | 9 | ✅ |
| `unit/knowledge/test_chunker.py` | 分块策略 | 12 | ✅ |
| `unit/knowledge/test_bm25.py` | BM25 | 9 | ✅ |
| `unit/knowledge/test_retriever.py` | 融合检索 (标记 slow) | 8 | ✅ |
| `unit/knowledge/test_knowledge_graph.py` | 知识图谱 (标记 slow) | 6 | ✅ |
| `unit/knowledge/test_loader.py` | 文档加载 | 6 | ✅ |
| `unit/memory/test_memory_manager.py` | 记忆管理器 (标记 slow) | 7 | ✅ |
| `unit/memory/test_semantic_memory.py` | 语义记忆 (标记 slow) | 4 | ✅ |
| `unit/memory/test_working_memory.py` | 工作记忆 (标记 slow) | 8 | ✅ |

---

## 5. 基础设施 `infrastructure/`

| 文件 | 用途 | 状态 |
|------|------|------|
| `docker/Dockerfile.backend` | 后端镜像 (多阶段构建) | ✅ |
| `docker/Dockerfile.render` | Render 专用 Dockerfile | ✅ |
| `docker/Dockerfile.worker` | Celery Worker 镜像 | 📋 |
| `monitoring/prometheus.yml` | Prometheus 配置 (预留) | 📋 |
| `docker-compose.yml` | 5 服务 (postgres/redis/qdrant/backend/frontend) | ✅ |
| `Makefile` | 开发/部署/测试命令 | ✅ |
| `monitoring/prometheus.yml` | Prometheus 配置 (预留) | 📋 |
| `docker-compose.yml` | 5 服务 (postgres/redis/qdrant/backend/frontend) | ✅ |
| `Makefile` | 开发/部署/测试命令 | ✅ |
