---
name: learning-resources
description: MediNexus 全技术栈学习指南（W1–W8 合并去重版）——含每项技术的项目作用、用法、官方文档与关键代码
metadata:
  type: reference
---

# MediNexus 技术栈学习指南（合并版）

> 本文档由 `week1`~`week8-learning-resources.md` 合并去重而来，覆盖 8 周开发中用到的全部技术。
> 适合新手按「通用基础 → 各周专题」顺序学习；重复出现的命令、设计模式、FAQ 已提取到文末附录。

---

## 〇、通用基础（跨周复用）

### 1. 项目启动 / 构建命令

```bash
# 后端开发
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 数据库迁移
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "描述"

# 前端开发
cd frontend && npm install
cd frontend && npm run dev        # 默认 3000
cd frontend && npm run build      # 生产构建验证

# 完整环境（Docker）
docker compose up --build
docker compose up -d
docker compose down

# 测试
cd backend && python -m pytest tests/ -v
cd backend && python -m pytest tests/ -m "not slow" -v   # 跳过慢测试
make test / make test-unit / make test-integration

# 验证 Agent / Skill / 记忆 注册
python -c "from agents import registry; print(registry.list_agents())"
python -c "from memory import MemoryManager; print('OK')"
```

### 2. Makefile 常用目标

| 目标 | 作用 |
|------|------|
| `make dev-backend` | uvicorn 启动后端 (8000) |
| `make dev-frontend` | next dev 启动前端 |
| `make docker-up` / `make docker-down` | Docker 一键起/停 |
| `make db-migrate msg="..."` | alembic 自动生成迁移 |
| `make db-upgrade` / `make init-db` | 升级 / 初始化数据库 |
| `make install` | pip + npm 安装依赖 |
| `make test` / `make test-unit` / `make test-integration` | 测试 |

### 3. 项目级工具

| 项目 | 作用 | 文档 |
|------|------|------|
| `pyproject.toml` | Python 项目元数据 + 依赖声明 | https://packaging.python.org/en/latest/guides/writing-pyproject-toml/ |
| `Makefile` | 常用命令一键执行（`.PHONY`、目标/依赖） | https://www.gnu.org/software/make/manual/ |
| `next.config.js` | 前端 `/api/*` → `http://localhost:8000/api/v1/*` 代理 | https://nextjs.org/docs/app/api-reference/next-config-js/rewrites |

---

## 一、Week 1 — 后端核心与基础设施

### 1. Python 3.12+ / FastAPI / Uvicorn / Pydantic v2
- **Python**：全部后端代码；重点 type hints、`async/await`、`dataclass`、`pyproject.toml`。文档：https://docs.python.org/3.12/
- **FastAPI**：`backend/app/main.py` 创建 `FastAPI()`；`backend/app/api/` 定义路由；依赖注入 `Depends()`。文档：https://fastapi.tiangolo.com/
- **Uvicorn**：`uvicorn app.main:app --reload --port 8000`。文档：https://www.uvicorn.org/
- **Pydantic v2**：`backend/app/schemas/` 定义请求/响应；`backend/app/config.py` 用 `BaseSettings` 管理环境变量。重点：`BaseModel`、`Field()`、配置继承。文档：https://docs.pydantic.dev/latest/

### 2. SQLAlchemy 2.0 (Async) / Alembic
- **SQLAlchemy**：`backend/app/models/` 定义 `Base`+模型；`backend/app/core/database.py` 创建 async engine/session。重点：`DeclarativeBase`、`Column`、`ForeignKey`/`relationship`、`AsyncSession`。文档：https://docs.sqlalchemy.org/en/20/
- **Alembic**：`backend/alembic/env.py` 关联 `Base.metadata` 与 DB URL。文档：https://alembic.sqlalchemy.org/en/latest/

### 3. PostgreSQL + pgvector / Redis
- **PostgreSQL+pgvector**：主库存患者/病历/处方；pgvector 提供向量检索（RAG）。Docker `pgvector/pgvector:pg17`，asyncpg 驱动。
- **Redis**：缓存 + 工作记忆 + 会话 + Agent 通信。`backend/app/core/redis.py`：`aioredis.from_url(...)`。重点：String/Hash/List、TTL、`asyncio` 客户端。

### 4. Docker & Docker Compose
- `docker-compose.yml` 定义 PostgreSQL+Redis+Qdrant+Backend 四个服务；`infrastructure/docker/Dockerfile.backend` 定义后端镜像。`docker-compose up --build` 一键启动。文档：https://docs.docker.com/compose/

### 5. 前端基础（Next.js 14 / React 18 / Tailwind）
- **Next.js 14**：`frontend/src/app/` App Router（文件即路由）、`layout.tsx`、`page.tsx`。文档：https://nextjs.org/docs
- **React 18**：函数组件、Hooks（`useState`/`useEffect`）、Props。文档：https://react.dev/
- **Tailwind CSS**：utility class（`flex items-center p-4`）；响应式前缀 `sm:`/`md:`。文档：https://tailwindcss.com/docs

### 6. 安全与认证骨架
- **python-jose + passlib**：JWT 生成/验证 + 密码哈希。`backend/app/core/auth.py`：`jwt.decode()`。文档：https://python-jose.readthedocs.io/ 、https://passlib.readthedocs.io/

---

## 二、Week 2 — Agent 框架与流式通信

### 1. LangGraph
- Agent 编排：状态图 `StateGraph(GraphState)` → `add_node()` → `add_conditional_edges()` → `compile()` → `ainvoke()/astream()`。节点接收状态返回更新，边决定下一步。文档：https://langchain-ai.github.io/langgraph/

### 2. BaseAgent 抽象类
- `backend/agents/base.py`，所有 Agent 基类。核心接口 `async def run(context) -> HandoverManifest`；钩子 `on_pre_process(context)`（身份验证/PII）、`on_post_process(manifest)`（审计）；`register_tool`/`execute_tool`。

### 3. AgentRegistry
- `backend/agents/registry.py`，`@registry.register` 装饰器自动注册；`registry.get("triage")` / `registry.create("triage")`。注册表 + 单例模式。

### 4. HandoverManifest（Agent 通信协议）
- `backend/app/schemas/agent.py`：`facts` / `pending_questions` / `risk_flags` / `evidence_level`(A/B/C) / `context`。结构化通信，避免自由文本解析错误。

### 5. TriageAgent & SupervisorAgent
- **TriageAgent**：`backend/agents/triage/`，LLM 模式 ↔ 关键词降级，中英文双语，三级紧急度（routine/urgent/emergency），输出 `HandoverManifest`。
- **SupervisorAgent**：`backend/orchestration/supervisor.py`，会话生命周期 + 路由（Triage→Doctor→Review→Followup→Complete；紧急→Emergency）。`SessionState`：`session_id`/`patient_id`/`current_agent`/`history`/`context`。

### 6. 诊断流程状态机
- `backend/agents/doctor/diagnosis_flow.py`：`INITIAL → HISTORY_TAKING → DIFFERENTIAL → TREATMENT → COMPLETED`。

### 7. WebSocket 流式通信
- 后端：`@app.websocket("/ws/{session_id}")` → `accept()` / `receive_text()` / `send_text()`；事件类型 `agent_start`/`token`/`agent_end`/`error`/`info`。`backend/orchestration/stream.py` 的 `StreamManager` 封装类型化事件。文档：https://fastapi.tiangolo.com/advanced/websockets/
- 前端：`frontend/src/lib/websocket.ts` 的 `ConsultationSocket`（自动重连、指数退避、事件监听）。文档：https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

### 8. 前端对话组件 & TypeScript
- `frontend/src/components/chat/`：`ChatMessage`/`ChatInput`/`ChatContainer`，用 `useState`/`useEffect`/`useCallback`/`useRef`；`setInterval` 每 30ms 追加 3 字符模拟流式。
- TypeScript：`frontend/src/lib/websocket.ts` 定义 `WsEventType`/`WsEvent`/`ConsultationSocket`；`tsconfig.json` 路径别名 `paths: {"@/*": ["./src/*"]}`。文档：https://www.typescriptlang.org/docs/

### 9. Pytest + pytest-asyncio
- `asyncio_mode = "auto"` 或 `@pytest.mark.asyncio`；`tests/integration/test_consultation_flow.py`、`test_agent_communication.py`。文档：https://docs.pytest.org/ 、https://pytest-asyncio.readthedocs.io/

**W2 Agent 数据流（速览）**：用户输入 → `WebSocket /ws/{id}` → `main.py` → `SupervisorAgent.run_agent` → `registry.get("triage")` → `TriageAgent.run` → `HandoverManifest` → `route()→doctor` → `StreamManager.emit_*` → 前端逐 token 渲染。

---

## 三、Week 3 — Skill 系统 + Doctor Agent

### 1. BaseSkill 抽象类
- `backend/agents/doctor/skills/base.py`：核心方法 `get_knowledge(context)`、`get_tools()`（可选）、`match_symptoms(symptoms)→float[0,1]`。策略模式隔离各科室诊断逻辑。

### 2. SkillRegistry（三级路由）
- `backend/agents/doctor/skills/registry.py`：`auto_route(symptoms, department)` → ① 精确科室匹配 → ② `match_symptoms()` 置信度（阈值 0.3）→ ③ 首个注册 Skill 降级。

### 3. Skill Loader
- `backend/agents/doctor/skills/loader.py`：`load_builtin_skills()` 导入 4 个 Skill 并注册；外部目录扫描接口预留（社区 Skill 延至 v0.3.0+）。

### 4. 内置 Skill
- **内科**：呼吸/消化/心血管/内分泌系统知识；Ollama 优化提示词（分段+完整 JSON Schema）。
- **皮肤科**：5 步诊断流程（皮损→伴随症状→病史→鉴别→治疗）。
- **耳鼻喉**：耳/鼻/咽喉疾病 + 警示信号（突发听力下降 72h 急诊等）。
- **心理科**：`calculate_phq9()`（0-4 无 → 20-27 重度）、`calculate_gad7()`；自杀检测 `match_symptoms("suicidal")` 返回 0.95 触发危机响应；含 SSRI+CBT 治疗与证据等级。

### 5. DoctorAgent（双模式）
- `backend/agents/doctor/agent.py`：LLM 模式（注入 Skill 提示词+知识 → 调 LLM → 解析 JSON）↔ 规则引擎降级（关键词 → 结构化建议）。`skill_registry.auto_route()` 匹配 Skill。
- JSON 三层容错解析：纯 JSON → Markdown 代码块 → 非结构化文本（降级规则引擎）。
- `backend/agents/doctor/prompt.py`：明确分段、完整 JSON Schema、少样本示例、关键约束前置、证据等级默认 `"C"`、红色警戒（心梗/呼吸困难/高热/呕血等）。

### 6. @registry.register 自动注册
- Agent 类定义上加 `@registry.register`；`agents/__init__.py` 导入子模块触发注册。验证：`registry.list_agents()` → `['triage','doctor','review','coordinator','followup']`。

### 7. Ollama 兼容策略
- 结构明确（`##` 分段）、完整 JSON Schema、少样本示例、约束前置、避免复杂推理链、三层容错解析。无 LLM 时插入 `[模式: 规则引擎]` 降级标记，所有建议标 `证据等级: C`。

**W3 测试**：`tests/unit/agents/test_skill_system.py`（19 用例）、`test_doctor_agent.py`（16 用例），用 `MockLLM` 返回固定 JSON 验证解析与 Manifest 构建。

---

## 四、Week 4 — 多源 RAG + Review Agent

### 1. 三路知识源
| 源 | 类型 | 置信度 | 分块 | 场景 |
|----|------|--------|------|------|
| 源A 临床病例 | — | 0.8 | Semantic | 常见病典型表现 |
| 源B 医学理论 | — | 0.6 | Hierarchical(父子) | 鉴别诊断框架 |
| 源C 最新论文 | — | 0.3 | Recursive | 疑难/罕见病 |

位置：`backend/knowledge/source.py`（`SourceConfig`）。

### 2. 差异化分块
- **SemanticChunker**（源A，384t）：按段落边界保持病例结构完整。
- **HierarchicalChunker**（源B，768t/子192t）：父承载上下文、子精确检索，子命中返回父。
- **RecursiveChunker**（源C，512t）：分隔符优先级 `\n\n`>`\n`>`. `>` ` `>char，保留 Abstract/Conclusion。
- 位置：`backend/knowledge/chunker.py`。

### 3. 多源融合检索（HF-RAG 架构）
`MultiSourceRetriever.retrieve()`：① 并行搜索三个 Qdrant 集合 → ② 每源 Top-K 召回（A=10/B=8/C=5）→ ③ RRF 源内融合 → ④ Z-score 跨源标准化 → ⑤ 置信度加权 `final = z × weight` → ⑥ 排序取 Top-K。
- **RRF**：`score = Σ 1/(k+rank)`，`k=60`（HF-RAG）。
- **Z-score**：`z=(score-μ)/σ`，解决不同集合相似度分布不可比。
- 位置：`backend/knowledge/retriever.py`。

### 4. BM25 降级
- `backend/knowledge/bm25_fallback.py`：自实现 BM25Okapi（无依赖），中文 bi-gram+单字混合分词；`VectorStore.health_check()` 返回 False 时切换。

### 5. 轻量知识图谱
- `backend/knowledge/graph/client.py`：症状→疾病一跳映射（Neo4j 待接入 / 开发用内存 dict）；种子数据 100+ 关系（`symptom_graph.py`，源自 OpenKG DiseaseKG、QASystemOnMedicalGraph）。

### 6. Review Agent 独立验证
- `backend/agents/review/agent.py`：**独立 RAGQuery 实例**，不从 Doctor 继承检索结果（避免确认偏误）。流程：独立检索 → 验证诊断 → 保留/追加风险标记 → A/B/C 评估 → 鉴别检查 → 输出审查 `HandoverManifest`。

**W4 论文参考**：HF-RAG(CIKM2025)、M-Eval(2025)、MECR-RAG(2025)、MultiDocFusion(2026)、Adaptive Chunking(2026)、SNOMED-CT KG(2025)、KI-DDI GAT(2024)。

---

## 五、Week 5 — 三层记忆 + SOAP 病历 + Follow-up

### 1. 三层记忆架构
| 层 | 存储 | 数据 | 生命周期 |
|----|------|------|---------|
| Working | Redis | `current_agent`+`context` | 会话期 (TTL 1h) |
| Episodic | PostgreSQL | 历史就诊 SOAP | 永久 |
| Semantic | PostgreSQL | 患者画像(过敏/既往/家族史/用药) | 永久 |

入口：`backend/memory/manager.py`（`MemoryManager.retrieve(patient_id)→LLM 文本`）。

### 2. Working Memory（Redis）
- `backend/memory/working.py`：`session:<id>:agent` / `session:<id>:context`（JSON）。TTL 3600s。`set(key, value, ex=ttl)`（Redis 5+ 弃用 `setex`）。history 仍在内存（过大不适合 TTL）。

### 3. Episodic Memory（SOAP）
- `backend/memory/stores/episodic.py`：SOAP 字段（subjective/objective/assessment/plan）。`recall(patient_id)`→最近 N 次；`store(SOAP)`；`format_history()`。所有 DB 操作 `try/except` 优雅降级返回 `[]`。

### 4. Semantic Memory
- `backend/memory/stores/semantic.py`：`patients` + `medical_histories`(JSONB)，含过敏/既往/家族/长期用药。`content` 示例：`{"name":"青霉素过敏","reaction":"皮疹","severity":"中"}`。

### 5. MemoryManager 注入点
- `orchestration/supervisor.py`：构建 context 时 `memory_manager.retrieve()` 注入 `patient_memory`；各 Agent 通过 `context.get("patient_memory","")` 读取。

### 6. 延迟导入模式（Lazy Import）
- DB/Redis 依赖模块（episodic/semantic/knowledge）在方法内 `from app.core.database import ...`，避免无 DB 时导入即失败。

### 7. SupervisorAgent 重构（W5）
- `_sessions: dict` → 仅存 metadata+history；`current_agent`/`context` 迁 Redis；`get_session()` 改 async，Redis 缺失则 session not found；`run_agent()` 自动注入记忆。断线重连：本地无 → Redis 恢复 → 重建 `SessionState`。

### 8. Follow-up Agent
- `backend/agents/followup/agent.py`：输入 `context["diagnosis"]` → 输出 `HandoverManifest`（复诊/用药提醒/警示/追问）。
- `scheduler.py`：5 种模板 `chronic_disease(30d)/post_surgery(7d)/medication_monitoring(14d)/mental_health(14d)/routine(7d)`；优先级 `mental > post_op > medication > chronic > routine`（修复 W4「抑郁症」误匹配 chronic 的问题）。
- 新增端点：`POST /consult/{id}/complete`（提交 SOAP）、`GET /consult/{id}/history`。

---

## 六、Week 6 — 前端完整产品

### 1. 前端结构
`frontend/src/app/`（layout/page/consultation/records/profile）、`components/chat/`+`ui/`（NavBar/DisclaimerBanner/LoadingState/ErrorState/EmptyState）、`lib/`（api.ts/websocket.ts）、`stores/consultationStore.ts`。

### 2. App Router & 状态组件
- 每个页面 `"use client"`；文件即路由；`layout.tsx` 共享布局。
- 三态覆盖：`LoadingState`/`ErrorState`/`EmptyState`，页面须处理 加载中/失败/空/有数据 四种状态。
- `DisclaimerBanner`：`standard`（琥珀色）/`emergency`（红色脉冲，🚨 急救指引）。

### 3. Tailwind 关键类
`min-h-screen`、`h-[calc(100vh-56px)]`、`flex-col`、`max-w-3xl mx-auto`、`grid md:grid-cols-3 gap-5`、`sticky top-0 z-50`、`animate-bounce`/`animate-pulse`、`transition-colors`、`space-y-4`。断点：`sm:640 / md:768 / lg:1024`。

### 4. WebSocket 流式渲染
- 事件类型 6 种：`agent_start`/`token`/`agent_end`/`error`/`info`/`emergency`(W6 新增)。
- `ChatMessage`：`useEffect` 每 30ms 追加 3 字符逐字渲染；`ChatContainer` 按 `agent_start→token…→agent_end` 管理消息流；`socket.on("emergency")` 置 `isEmergency` 并切换免责声明为急救模式。

### 5. API 客户端
| 函数 | 端点 |
|------|------|
| `startConsultation()` | POST `/consult` |
| `getConsultation()` | GET `/consult/{id}` |
| `completeConsultation()` | POST `/consult/{id}/complete` |
| `getConsultationHistory()` | GET `/consult/{id}/history` |
| `healthCheck()` | GET `/health` |

### 6. 页面
- **首页 `/`**：Hero + 6 功能卡片 + 页脚免责声明。
- **问诊 `/consultation`**：`chat`→`summary` 两阶段；顶部紧急标记 + 完成按钮；底部免责声明条。
- **病历 `/records`**：SOAP 时间线，可展开卡片。
- **个人中心 `/profile`**：头像+健康档案(过敏/既往/用药)+编辑模式。
- Mock 数据：`MOCK_RECORDS`(600ms)、`MOCK_PROFILE`(400ms)，API 就绪后替换。

---

## 七、Week 7 — 安全护栏 + Coordinator

### 1. Guardrail 三件套（`backend/guardrails/`）
- **EmergencyDetector**：三层次 关键词(50+中英文)→正则(7条语义)→LLM(可选)；分类 SUICIDE/CARDIAC/RESPIRATORY/NEUROLOGICAL/HEMORRHAGE；分发急救指引+热线。
- **PIISanitizer**：正则（lookbehind/lookahead 兼容中文，不用 `\b`）；支持手机/身份证/邮箱/座机；`sanitize_text()`/`mask_pii()`(138****5678)/`detect_pii()`。
- **IdentityVerifier**：`verify(patient_id, session_patient_id)` 匹配 + JWT 验证（demo 跳过）+ `audit_access()` 审计。

### 2. Coordinator Agent（多科室会诊）
- `backend/agents/coordinator/agent.py` + `consultation_protocol.py`。
- 流程：分析复杂度 → 邀请专科(Skill 生成意见) → 综合报告(共识诊断+分歧)。
- `SpecialistOpinion{specialty, diagnosis[], recommendations[], confidence, evidence_level}`、`ConsultationReport{...consensus_diagnosis, disagreements}`。
- 6 种复杂性触发器：`multi_system`/`cardio_respiratory`/`skin_systemic`/`mental_physical`/`ent_systemic` 等，逐级责任链匹配。

### 3. Middleware & 审计
- `LoggingMiddleware`（`backend/app/middlewares/logging.py`）：HTTP 方法+路径+状态码+耗时，`medinexus.audit` Logger。
- `AuthMiddleware`（`auth.py`）：demo 放行；公开路径 `/health`/`/api/v1/health`/`/docs`/`/openapi.json`/`/ws/*`；生产启用 JWT。
- `AuditLog` 模型：`action`/`details(JSON)`/`created_at`；Agent 处理前由 `IdentityVerifier.audit_access()` 触发。

**W7 测试**：`test_guardrails.py`(22) + `test_coordinator.py`(13)。

---

## 八、Week 8 — Docker 部署 + BYO Key + 文档体系

### 1. 多阶段构建
- 前端 `frontend/Dockerfile`：`node:20-alpine`，build 阶段 `npm ci`+`npm run build`，run 阶段仅复制 `.next/`/`node_modules/`。
- 后端 `infrastructure/docker/Dockerfile.backend`：`python:3.12-slim`，`pip install -e ".[dev]"`，`uvicorn app.main:app`。

### 2. Docker Compose 生产
| 服务 | 镜像 | 端口 | 健康检查 |
|------|------|------|---------|
| postgres | pgvector/pgvector:pg17 | 5432 | pg_isready |
| redis | redis:7-alpine | 6379 | redis-cli ping |
| qdrant | qdrant/qdrant:latest | 6333 | — |
| backend | 自构建 | 8000 | — |
| frontend | 自构建 | 3000 | — |

### 3. BYO Key 配置
- 项目不内置任何 Key；无 Key 自动降级规则引擎。
```env
MEDINEXUS_LLM_PROVIDER=ollama        # + MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434
MEDINEXUS_LLM_PROVIDER=anthropic     # + MEDINEXUS_ANTHROPIC_KEY=sk-ant-xxxx
MEDINEXUS_LLM_PROVIDER=openai        # + MEDINEXUS_OPENAI_KEY=sk-xxxx
```
- 降级链：Ollama → OpenAI → Anthropic → 规则引擎。详细见 `docs/byok-guide.md`。

### 4. 项目文档体系
| 文档 | 用途 |
|------|------|
| `README.md` | 概览 + 快速开始 |
| `docs/architecture.md` | 系统架构与 Agent 流程（v0.1.1） |
| `.claude/codebase/API_SURFACE.md` | REST/WebSocket API 权威清单（AI 索引） |
| `.claude/codebase/MODULE_MAP.md` | 模块与 Agent 权威清单（AI 索引） |
| `docs/byok-guide.md` | LLM 配置 |
| `docs/docker-quickstart.md` | Docker 零基础 |
| `docs/frontend-design-reference.md` | 前端规范 |
| `.claude/codebase/*` | AI 代码图谱（MODULE_MAP/BUILD_STATUS/CONVENTIONS/API_SURFACE/DATA_FLOW/DEPENDENCY_GRAPH） |

---

## 附录 A — 设计模式总览（各周合并去重）

| 模式 | 使用位置 |
|------|---------|
| 抽象基类 / 模板方法 | `BaseAgent.run()`、`DoctorAgent` 双模式 `run()` 骨架 |
| 注册表 (Registry) + 单例 | `AgentRegistry` / `SkillRegistry` 模块级实例 |
| 策略 (Strategy) | TriageAgent 双模式、Skill 系统、随访计划 `get_plan_for_diagnosis()`、紧急响应分发 |
| 状态机 (State Machine) | `SupervisorAgent.route()`、`DiagnosisFlow` |
| 工厂方法 (Factory) | `SkillRegistry.auto_route()`、层叠路由 |
| 适配器 (Adapter) | `_parse_diagnosis_response()`（LLM 文本→JSON）、`RAGQuery` 外观 |
| 责任链 (Chain of Responsibility) | `auto_route()` 三级路由、Coordinator 复杂性触发器 |
| 观察者 (Observer) | `ConsultationSocket.on()` 事件订阅 |
| 生产者-消费者 | `StreamManager` + WebSocket |
| 钩子 (Hook) | `on_pre_process` / `on_post_process`（Plugin 注入点） |
| 外观 (Facade) | `MemoryManager`、`RAGQuery` |
| 建造者 (Builder) | `SymptomGraphBuilder` |
| 延迟初始化 (Lazy Init) | `_ensure_skills()`、episodic/semantic 延迟导入 |
| 标记接口 | 降级模式 `[模式: 规则引擎]` 前缀 |
| 分层架构 | Working→Episodic→Semantic |
| 数据类 (Data Class) | `FollowupPlan`/`ScheduledFollowup`/`RetrievedChunk`/`FusionResult` |
| 装饰器 | middleware 请求前后注入、类注册 |
| 三阶段检测 | EmergencyDetector 关键词→正则→LLM |

## 附录 B — 常见问题（各周合并去重）

- **Skill 和 Agent 的区别？** Agent 是完整角色（分诊/诊断），Skill 是 Agent 使用的知识包；一个 DoctorAgent 按科室切换 Skill。
- **为什么双模式（LLM+规则引擎）？** 用户可能没配 Key，规则引擎保证零配置可跑，降级标注让用户知情。
- **怎么加新科室 Skill？** ① 继承 `BaseSkill` 实现 `get_knowledge()`；② 定义 `system_prompt`+`match_symptoms()`；③ 在 `loader.py` 的 `load_builtin_skills()` 加 import，自动注册。
- **提示词为何写详细 JSON Schema？** 本地模型（Ollama）对模糊指令不稳定，完整 Schema+示例显著提升格式可靠性。
- **Mock LLM 是什么？** 测试用 `MockLLM` 返回固定 JSON，验证 JSON 解析与 Manifest 构建，不依赖真实服务。
- **三层记忆 vs SessionState？** Working(Redis)=进行到哪；Episodic(PG)=看过什么病；Semantic(PG)=患者特征；SessionState=当前对话上下文（内存）。
- **get_session 为何变 async？** `current_agent`/`context` 现存 Redis，读取需异步 IO（为断线重连付出的代价）。
- **SOAP 与 HandoverManifest 关系？** Manifest 是 Agent 间「快递单」，SOAP 是存库「病历格式」；Doctor 输出 Manifest → 提取 SOAP → `complete` API 入库。
- **没有 PostgreSQL 记忆能工作吗？** 能，所有 DB 操作 try/except 兜底，失败返回空/False 不崩溃。
- **为什么 `"use client"`？** 问诊页需 `useState`/`useEffect`/`useCallback` 等客户端 Hook。
- **三态组件必须每个页面都加吗？** 是，W6 原则：任意页面不应白屏，必须覆盖 加载中/失败/空/有数据。
- **没有后端前端能跑吗？** 能，但 WebSocket 失败重试，病历/个人中心用 Mock 数据。
- **降级链顺序？** Ollama → OpenAI → Anthropic → 规则引擎。

---

> 合并说明：本文件由 W1–W8 学习资源去重合并，删除了各周重复的「学习路线图 / 命令速查 / 设计模式表 / FAQ」，统一为「通用基础 + 分周专题 + 附录」。原始 `weekN-learning-resources.md` 已移除。
