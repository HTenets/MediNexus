# 模块地图（MODULE_MAP）— v0.1.1

> 状态图例: ✅ 真实可用 · 🚧 已实现未接线/部分 · 📌 规划中

## 后端 backend/

### agents/ — 多智能体
| 模块 | 文件 | 职责 | 状态 |
|------|------|------|------|
| BaseAgent | `agents/base.py` | 抽象基类：`run`/`on_pre_process`/`on_post_process`/工具注册 | ✅ |
| AgentRegistry | `agents/registry.py` | `@registry.register` 按 `name` 注册 | ✅ |
| TriageAgent | `agents/triage/agent.py` + `prompt.py` | 症状评估、科室分诊、紧急程度 | ✅ |
| DoctorAgent | `agents/doctor/agent.py` + `diagnosis_flow.py` + `skills/` | 多轮问诊、鉴别诊断、匹配专科 Skill | ✅ |
| ReviewAgent | `agents/review/agent.py` + `prompt.py` | 独立 RAG 复核、用药禁忌、证据等级 | ✅ |
| FollowupAgent | `agents/followup/agent.py` + `prompt.py` | 随访计划、用药提醒 | ✅ |
| CoordinatorAgent | `agents/coordinator/agent.py` | 多科室会诊（**已实现、已注册，但未接入路由**） | 🚧 |

### app/ — API 与数据层
| 模块 | 文件 | 职责 |
|------|------|------|
| 入口 | `app/main.py` | FastAPI，WebSocket `/ws/{session_id}`，装配 rag/llm/supervisor |
| 路由聚合 | `app/api/router.py` | 前缀 `/api/v1`（health 无前缀） |
| 认证 | `app/api/auth.py` | register/login/refresh/logout |
| 问诊 | `app/api/consultation.py` | start/get 会话 |
| 患者 | `app/api/patients.py` | CRUD + `/me` |
| 病历 | `app/api/medical_records.py` | 病历读写 |
| 知识 | `app/api/knowledge.py` | `/knowledge/search`、`/knowledge/health` |
| Schemas | `app/schemas/` | HandoverManifest / Consultation / Patient / MedicalRecord / memory |
| Models | `app/models/` | SQLAlchemy 2.0 异步 ORM（user/patient/consultation/medical_record/...） |
| Core | `app/core/` | auth(JWT) / password(bcrypt) / database / rag(get-set) / dependencies / demo_seed |
| Middlewares | `app/middlewares/` | auth(PUBLIC_PATHS 鉴权) / rate_limit / logging |
| Repositories | `app/repositories/` | user / patient / record / consultation 仓储 |

### guardrails/ — 安全护栏
| 模块 | 文件 | 职责 | 状态 |
|------|------|------|------|
| PIISanitizer | `guardrails/pii_sanitizer.py` | 手机号/身份证/邮箱正则脱敏 | ✅ |
| EmergencyDetector | `guardrails/emergency_detector.py` | 6 类紧急信号关键词+正则 | ✅ |
| IdentityVerifier | `guardrails/identity_verifier.py` | 实名认证（**已实现未接入**） | 🚧 |

### knowledge/ — 知识库 & RAG
| 模块 | 文件 | 职责 | 状态 |
|------|------|------|------|
| 工厂 | `knowledge/factory.py` | `create_rag_query`: BM25 + 可选 Qdrant + 知识图谱 | ✅ |
| 检索器 | `knowledge/retriever.py` | 多源检索，RRF(k=60)+Z-score 融合 | ✅ |
| RAG | `knowledge/rag.py` | `RAGQuery.query/_formatted`，KG 增强 | ✅ |
| BM25 | `knowledge/bm25_fallback.py` | 内置 BM25（默认检索路径） | ✅ |
| 源配置 | `knowledge/source.py` | 三源权重 0.8/0.6/0.3 | ✅ |
| 图谱 | `knowledge/graph/` | 症状→疾病一跳映射（内存种子） | ✅ |
| 加载/切片/向量库/种子 | `knowledge/loader.py` `chunker.py` `vector_store.py` `seed_data.py` | 知识处理链 | ✅ |

### memory/ — 分层记忆
| 模块 | 文件 | 职责 |
|------|------|------|
| MemoryManager | `memory/manager.py` | 三层门面 `retrieve/store/store_consultation` |
| WorkingMemory | `memory/working.py` + `_redis.py` | 会话短期（Redis/进程内） |
| EpisodicMemory | `memory/stores/episodic.py` | 历史就诊（consultations 表） |
| SemanticMemory | `memory/stores/semantic.py` | 患者画像（patients 表） |

### llm/ — LLM 客户端
| 模块 | 文件 | 职责 |
|------|------|------|
| Base | `llm/client.py` | `chat`/`chat_stream` 统一接口 |
| Factory | `llm/factory.py` | `create_llm_client` 按 `MEDINEXUS_LLM_PROVIDER` |
| Providers | `llm/providers/{ollama,openai,anthropic}.py` | Ollama / OpenAI(兼容 deepseek/moonshot) / Anthropic |

### orchestration/ — 编排层
| 模块 | 文件 | 职责 |
|------|------|------|
| SupervisorAgent | `orchestration/supervisor.py` | 会话管理 + 路由 + 注入 memory/rag |
| 叙事 | `orchestration/narrative.py` | HandoverManifest→患者口述（`MEDINEXUS_STREAM_NARRATIVE`） |
| 状态 | `orchestration/state.py` | `SessionState` |
| 流 | `orchestration/stream.py` | `StreamManager`/`StreamEvent` 封装 WS 事件 |

### 其他
- `workers/tasks.py` — Celery 任务（**已定义无调用方**）🚧
- `alembic/` — 迁移 `0001_initial_schema.py`

## 前端 frontend/src/app/
| 页面 | 路由 | 状态 |
|------|------|------|
| 登录 | `/login` | ✅ 真实 |
| 问诊 | `/consultation` (+ `chat/*` WS) | ✅ 真实 |
| 复核/总结 | `/consultation/review`、`/summary` | ✅ 真实 |
| 患者管理 | `/patients` | ✅ 真实 |
| 病历 | `/records` | ✅ 真实 |
| 仪表盘 | `/dashboard` | ✅ 真实（去硬编码） |
| 个人中心 | `/profile` | ✅ 真实（设备区标注"尚未接入"） |
| 设置/系统状态 | `/settings`、`/system-status` | 🚧 部分标注待接入 |
| 上传报告/分析演示 | `/upload-report`、`/consultation/analysis` | 📌 演示/未挂主流程 |
