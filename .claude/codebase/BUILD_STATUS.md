# MediNexus 构建状态 (Build Status)

> 追踪每个组件的实现状态。对 AI 而言: 知道什么已就绪、什么待实现。
> 时间: v0.1.0 (2026-06-22), 全部 8 周开发 + Demo 级模块完善完成。
> 测试状态: 快速测试 129 ✅ / 集成测试 27 ✅ / 总计 156 测试通过。
> 决策基线: 详见 [[design-decisions]]

---

## 总体进度

```
第1周 ████████████████████ 100%  项目基础设施
第2周 ████████████████████ 100%  Agent 框架 + Triage Agent
第3周 ████████████████████ 100%  Skill 系统 + Doctor Agent ✅ Ollama 优化 + 中英双语 + 降级路径
第4周 ████████████████████ 100%  RAG 知识库 + Review Agent ✅ 三路知识源 + HF-RAG 融合 + 轻量 KG + BM25 降级 + Review 独立验证
第5周 ████████████████████ 100%  记忆系统 + SOAP + Session→Redis + Followup ✅
第6周 ████████████████████ 100%  前端完整产品 ✅ 17 页面 + web-design 迁移 + Mock API
第7周 ████████████████████ 100%  安全 + Guardrail + Coordinator ✅ Emergency/PII/Identity + 会诊协议
第8周 ████████████████████ 100%  部署 + 文档 + v0.1.0 ✅ Docker 多阶段构建 + README + BYO Key 指南
```

### 设计决策摘要
| 决策 | 影响 |
|------|------|
| 🎯 **目标用户: 患者自助问诊** | 前端须在所有医疗回答后显示免责声明 |
| 🏥 **准确度: 参考级** | W4 RAG 需要双语知识库(指南+药品说明), 投入加倍 |
| 🤖 **默认 LLM: Ollama** | Skill 提示词须针对本地模型能力优化(更明确的提示结构) |
| 🔑 **BYO Key + 降级** | 降级时须在响应中明确提示用户"当前为降级模式" |
| 🌐 **中文为主英文备用** | UI/Agent 输出默认中文, 知识库中英文索引 |
| 🔌 **Skill 社区维护** | builtin/ 保留, 外部加载接口预留到 v0.3.0+ |
| 📱 **前端完整产品** | W6 高强度: 全页面 + 响应式 + 移动端适配 |
| ⚠️ **紧急演示级** | 只记录日志 + 前端展示急救信息, 不做真实接入 |

---

## 组件详细状态

### ✅ 已完成 (可直接使用)

| 组件 | 文件 | 说明 |
|------|------|------|
| BaseAgent 抽象 | `agents/base.py` | 含 on_pre_process / on_post_process Hook |
| AgentRegistry | `agents/registry.py` | 全局单例, 支持自动注册 |
| TriageAgent | `agents/triage/agent.py` | LLM + 关键词双模式, 中英文分诊 |
| Triage prompt | `agents/triage/prompt.py` | 完整中英文系统提示词 |
| SessionState | `orchestration/state.py` | 会话状态定义 |
| GraphState | `orchestration/state.py` | LangGraph TypedDict |
| ConsultationGraph | `orchestration/graph.py` | LangGraph 状态图构建器 |
| SupervisorAgent | `orchestration/supervisor.py` | Redis 会话 + MemoryManager 注入 + 路由 |
| StreamManager | `orchestration/stream.py` | WebSocket 流式事件 |
| Consultation API | `app/api/consultation.py` | POST/GET + WebSocket + SOAP complete |
| Mock Data API | `app/api/mock_data.py` | 10 个端点: 三路知识源/SOAP/档案/Dashboard/状态 |
| Main entry | `app/main.py` | FastAPI 应用 + WS 端点 |
| Router | `app/api/router.py` | 路由汇总前缀 + mock_data 注册 |
| Config | `app/config.py` | pydantic-settings 配置 |
| Database core | `app/core/database.py` | async SQLAlchemy |
| Health API | `app/api/health.py` | 健康检查 |
| LLM Client | `llm/client.py` | 抽象 + chat/chat_stream |
| LLM providers | `llm/providers/` | OpenAI/Anthropic/Ollama |
| DoctorAgent | `agents/doctor/agent.py` | LLM + 规则双模式, Skill 集成, 降级标注 |
| Doctor prompt | `agents/doctor/prompt.py` | Ollama 优化 JSON 输出诊断提示词 |
| Skill 系统 | `agents/doctor/skills/` | BaseSkill + Registry + Loader + 4 内置 Skill |
| ReviewAgent | `agents/review/agent.py` | 独立 RAG 验证 + 鉴别诊断检查 + 证据等级 |
| Review prompt | `agents/review/prompt.py` | 8 维完整审查提示词 + JSON 输出格式 |
| Review rules | `agents/review/rules/drug_interaction.py` | 14 组药物相互作用 (severity/mechanism/recommendation) |
| Review rules | `agents/review/rules/contraindication.py` | 禁忌症+过敏+年龄限制 (完整数据 + 3 检查函数) |
| Review checkers | `agents/review/checkers/` | 可插拔框架 + drug_interaction + contraindication 检查器 |
| CoordinatorAgent | `agents/coordinator/agent.py` | 多科室会诊 + COMPLEXITY_TRIGGERS (4 种触发器) |
| FollowupAgent | `agents/followup/agent.py` | 随访计划 + 用药提醒 + 5 种计划模板 |
| EmergencyDetector | `guardrails/emergency_detector.py` | 50+ 关键词 + 7 条语义正则 + 5 类紧急响应 |
| PIISanitizer | `guardrails/pii_sanitizer.py` | 正则脱敏(手机/身份证/邮箱) + 掩码 + 检测 |
| IdentityVerifier | `guardrails/identity_verifier.py` | 患者ID校验 + JWT 可注入 + 审计日志 |
| Patients API | `app/api/patients.py` | 完整 CRUD + 搜索分页 + 2 条 demo 数据 |
| Medical Records API | `app/api/medical_records.py` | get/list/create + 3 条 demo 记录 |
| JWT Auth | `app/core/auth.py` | create/refresh/decode/get_current_user/optional |
| PII Security | `app/core/security.py` | 正则检测/脱敏/掩码 (4 种模式) |
| Dependencies | `app/core/dependencies.py` | session_id/patient_id/pagination |
| Rate Limit | `app/middlewares/rate_limit.py` | 60 req/min per IP (已接入 main.py) |
| Celery Workers | `workers/tasks.py` | 3 任务 (reminder/analysis/cleanup) + lazy Celery init |
| Logging middleware | `app/middlewares/logging.py` | 请求耗时 + 状态码审计日志 |
| Auth middleware | `app/middlewares/auth.py` | JWT 可选 (Demo 模式跳过) |
| MemoryManager | `memory/manager.py` | 三层记忆统一检索接口 |
| WorkingMemory | `memory/working.py` | Redis 会话 (current_agent + context, TTL 3600s) |
| EpisodicMemory | `memory/stores/episodic.py` | PostgreSQL 历史就诊 (SOAP 字段) |
| SemanticMemory | `memory/stores/semantic.py` | PostgreSQL 患者画像 (过敏/既往史/家族史) |
| RAG 知识库 | `knowledge/` | 三路源 + 3 种分块 + Qdrant + BM25 降级 + RRF/Z-score 融合 |
| 轻量知识图谱 | `knowledge/graph/` | 症状→疾病一跳映射, 100+ 种子实体 |
| 前端 17 页面 | `frontend/src/app/` | 全部 next build 通过, web-design 风格 |
| 前端 UI 组件 | `frontend/src/components/` | AppShell/Icons/Loading/Error/Empty/NavBar 等 |
| WebSocket 客户端 | `frontend/src/lib/websocket.ts` | 含自动重连 + 6 事件类型 |
| API 客户端 | `frontend/src/lib/api.ts` | REST + SOAP 封装 |
| 集成测试 | `tests/integration/` | 12 个测试用例 |
| 单元测试 (Agent) | `tests/unit/agents/` | ~78 测试 (Skill/Doctor/Review/ReviewRules/Coordinator/Followup) |
| 单元测试 (Guardrails) | `tests/unit/guardrails/` | 24 测试 (Emergency/PII/Identity) |
| Patient model | `app/models/patient.py` | ORM 模型 (含 gender/dob/phone) |
| Consultation model | `app/models/consultation.py` | ORM 模型 (含 SOAP 字段) |
| Dockerfiles | `frontend/Dockerfile`, `infrastructure/docker/` | 多阶段构建 |
| docs/byok-guide.md | — | Ollama/Claude/OpenAI 配置指南 + 降级链 |
| 周学习文档 | `docs/weekN-*.md` | W1-W8 完整 |

### 🏗 部分完成 (骨架就绪, 待实现核心逻辑)

| 组件 | 文件 | 已就绪 | 待完成 |
|------|------|--------|--------|
| RAG 真实数据 | `knowledge/loader.py` | 分块/向量化 Pipeline | 爬取真实病例/指南/论文入库 |
| Neo4j 知识图谱 | `knowledge/graph/client.py` | 内存 dict 兜底 | Neo4j 生产接入 |
| Prescription model | `app/models/prescription.py` | ORM 模型定义 | 业务逻辑 (create/verify/dispense) |
| Followup model | `app/models/followup.py` | ORM 模型定义 | 业务逻辑 (schedule/notify) |
| Patient schema | `app/schemas/patient.py` | 完整 Pydantic 模型 | 已在 API 层使用 |
| Plugin SDK | `plugins/sdk/` | BasePlugin + hooks | 分类注册/生命周期/市场 (v0.3.0+) |
| 程序性记忆 | `memory/` | 三层基础记忆 | Agent 总结经验能力 |

### 📋 待实现 (文件未创建或为预留)

| 组件 | 说明 | 计划版本 | 备注 |
|------|------|---------|------|
| GraphRAG | 知识图谱检索 | v0.3.0+ | 接口已预留 (graph_rag.py) |
| 外部 Skill 加载 | 社区贡献 Skill | v0.3.0+ | loader.py 接口预留 |
| 前端状态管理 | Zustand 集成 | v0.2.0+ | store 预留文件 |
| 英文 i18n | 国际化 | v0.2.0+ | — |
| Human-in-the-loop | 专家审核 | v0.2.0+ | — |
| 真实急救接入 | 120 集成 | v0.2.0+ | 演示级已够 |

---

## 已知问题 / Todo

| 问题 | 位置 | 说明 | 优先级 |
|------|------|------|--------|
| TriageAgent evidence_level 硬编码 | `agents/triage/agent.py:55` | `evidence_level="C"` 写死 | low |
| Has_prescription 硬编码 | `orchestration/supervisor.py:44` | 路由逻辑的条件目前写死 | low |
| RAG 无真实数据 | `knowledge/loader.py` | 只有 3 条 seed case | medium |
| DoctorAgent 降级标注 | `agents/doctor/agent.py` | facts[0] 降级标记已实现但需验证 | low |
| Patients API 内存存储 | `app/api/patients.py` | 无持久化，重启丢失 | low |
| Medical Records API 内存存储 | `app/api/medical_records.py` | 无持久化，重启丢失 | low |

---

## 测试覆盖率

```
tests/
├── integration/
│   ├── test_consultation_flow.py  — 12 测试 (完整就诊流程)
│   ├── test_agent_communication.py — 11 测试 (Agent 通信)
│   └── 小计: 27 passed ✅
├── unit/
│   ├── agents/
│   │   ├── test_skill_system.py      — 19 测试 (Skill 系统)        ✅ W3
│   │   ├── test_doctor_agent.py      — 16 测试 (Doctor Agent)      ✅ W3
│   │   ├── test_review_agent.py      — 6 测试 (Review Agent)       ✅ W4
│   │   ├── test_review_rules.py      — 14 测试 (药物交互+禁忌症)   ✅ 2026-06-22
│   │   ├── test_coordinator.py       — 13 测试 (Coordinator)       ✅ W7
│   │   └── test_followup_agent.py    — 10 测试 (Followup)          ✅ W5
│   │   └── 小计: 78 passed ✅
│   ├── guardrails/
│   │   └── test_guardrails.py        — 24 测试 (Emergency/PII/ID)  ✅ W7
│   ├── knowledge/                  (慢测试: 需 Qdrant)
│   │   ├── test_source.py           — 9 测试                       ✅ W4
│   │   ├── test_chunker.py          — 12 测试                      ✅ W4
│   │   ├── test_bm25.py             — 9 测试                       ✅ W4
│   │   ├── test_retriever.py        — 8 测试 (标记 slow)           ✅ W4
│   │   ├── test_knowledge_graph.py  — 6 测试 (标记 slow)           ✅ W4
│   │   └── test_loader.py           — 6 测试                       ✅ W4
│   └── memory/                    (慢测试: 需 Redis/PG)
│       ├── test_memory_manager.py   — 7 测试 (标记 slow)           ✅ W5
│       ├── test_semantic_memory.py  — 4 测试 (标记 slow)           ✅ W5
│       └── test_working_memory.py   — 8 测试 (标记 slow)           ✅ W5
```

**测试状态:**
- `pytest -m "not slow"` — **129 tests, all passed** ✅ (Agent + Guardrails + Rules + 通信)
- `pytest` (含 slow) — ~180 tests, 需 PostgreSQL/Redis/Qdrant 运行
- 集成测试: **27 passed** ✅
