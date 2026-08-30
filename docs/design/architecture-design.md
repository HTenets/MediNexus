# MediNexus（医枢）架构与设计 — v0.1.1

> 当前版本（2026-08-30 去伪存真）的真实架构与设计说明。能力真伪以根 `README.md`「实现状态」表为准。
> 更精简的概览见 `docs/architecture.md`；AI 可读模块/API/数据流索引见 `.claude/codebase/`。

## 1. 产品定位

面向**普通患者自助问诊**的开源多智能体医疗诊断平台（参考级准确度，非临床级，前端附免责声明）。
四 Agent 协作完成全流程闭环；每个 Agent 既可由 LLM 驱动，也能在无 LLM 时降级为规则引擎。

## 2. 总体架构

```
用户 → TriageAgent → DoctorAgent(+Skill) → ReviewAgent → FollowupAgent → 输出
                              ↑
              SupervisorAgent（状态机路由 + 记忆/RAG 注入）
```

- **SupervisorAgent**：会话管理 + Agent 路由 + 记忆/RAG 注入；按分诊结果、紧急程度、上下文在 Agent 间路由。
- **HandoverManifest**：Agent 间结构化交接协议（Pydantic），字段 `facts/pending_questions/risk_flags/evidence_level/context`。
- **真流式输出**：WebSocket 直连 LLM `chat_stream` 逐 token 下发；无 LLM 时整段下发，不做打字模拟。
- **CoordinatorAgent**（多科室会诊）已实现并通过测试，但**未接入路由**（触发词过宽），计入 v0.2.0。

## 3. 智能体详细设计

### TriageAgent
- 接收主诉，评估症状；输出 `urgency`（routine / urgent / emergency）与 `department`（内/皮肤/耳鼻喉/心理/骨科/全科）。
- 识别信息缺口，生成追问列表，交 HandoverManifest 给 DoctorAgent。

### DoctorAgent
- 接收分诊结果，自动匹配专科 Skill；运行诊断状态机 `DiagnosisState`：
  `INITIAL → HISTORY_TAKING → DIFFERENTIAL → TREATMENT → COMPLETED`。
- LLM 模式：注入 Skill 知识 + 系统提示生成结构化诊断；规则模式：关键字症状匹配，经验性建议。
- 输出诊断、治疗方案、风险评估。

### ReviewAgent
- 经 supervisor 注入的 `rag_query` **独立检索**知识库，验证诊断准确性。
- 检查用药禁忌与相互作用，评估证据等级（A/B/C），标记 `risk_flags`，高风险项强制返回 Doctor 修订。

### FollowupAgent
- 生成康复计划与用药提醒、症状监测与复查建议、健康档案更新。

## 4. 分层记忆设计

自研三层记忆（**未依赖 Mem0**），跨会话健康档案：

| 层次 | 文件 | 存储 | 核心方法 |
|------|------|------|---------|
| Working | `memory/working.py` + `_redis.py` | Redis(TTL) / 进程内 | 会话作用域：set/get_context/set_current_agent |
| Episodic | `memory/stores/episodic.py` | `consultations` 表 / 进程内 | `store_consultation` / `format_recall` |
| Semantic | `memory/stores/semantic.py` | `patients` 表 / 进程内 | `format_profile`（过敏史/既往史） |

- `MemoryManager.retrieve()` 组合 Semantic + Episodic 为 LLM 注入块 `context["patient_memory"]`。
- 注入点：`SupervisorAgent.run_agent` → `_recall_memory` → 写入各 Agent context；会话终态归档 Episode。
- 全部 best-effort：记忆故障仅记日志，不阻断问诊。

## 5. RAG 知识增强设计

- 三源知识库：`CLINICAL_CASES=0.8` / `MEDICAL_THEORY=0.6` / `LATEST_PAPERS=0.3`，RRF(k=60) + Z-score 融合 + 置信度加权。
- `create_rag_query()`（`knowledge/factory.py`）：**默认 BM25 全文检索**（内置，零依赖）+ 可选 Qdrant 向量（需 `MEDINEXUS_QDRANT_URL` + 嵌入服务）+ 知识图谱（症状→疾病一跳映射）。
- 无向量库时 BM25 作为显式 `force_fallback`，不做哈希假嵌入。
- 知识图谱增强召回；`GET /api/v1/knowledge/search` 对外提供三源分桶结果。
- ReviewAgent 凭 `rag_query` 独立查询，与 DoctorAgent 检索解耦。

## 6. 安全护栏设计

- **PIISanitizer**（`guardrails/pii_sanitizer.py`）：正则脱敏手机号/座机/身份证/邮箱为占位符。
- **EmergencyDetector**（`guardrails/emergency_detector.py`）：中英文关键词+正则识别自杀/心脏/呼吸/出血/卒中/休克等 6 类紧急信号。
- 触发位置：`BaseAgent.on_pre_process` 在 `run()` 前先 PII 脱敏再紧急检测；紧急时**强制覆盖** Agent 输出并触发应急响应。

## 7. LLM 多提供商设计

- `BaseLLMClient`（ABC）统一 `chat()` / `chat_stream()`；`create_llm_client`（`llm/factory.py`）按 `MEDINEXUS_LLM_PROVIDER` 选择 Ollama（默认）/ OpenAI（兼容 deepseek/moonshot）/ Anthropic。
- 无可用 Key 时返回 None → 全局降级规则引擎。

## 8. 前端设计

- 技术：Next.js 14 + React 18 + Tailwind 3 + shadcn/ui + framer-motion，App Router。
- 真实接口页面：`/login`、`/consultation`(+WS)、`/consultation/review`、`/summary`、`/patients`、`/records`、`/dashboard`、`/profile`。
- 部分标注待接入：`/settings`、`/system-status`；演示/未挂主流程：`/upload-report`、`/consultation/analysis`。
- 设备接入、报告上传、可穿戴同步等页面区域标注"尚未接入"。

## 9. 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + Python 3.12+，自研 SupervisorAgent 状态机 |
| 数据库 | PostgreSQL 17（SQLAlchemy 2.0 异步 + Alembic） |
| 检索 | 内置 BM25（默认）/ Qdrant（可选）/ 知识图谱 |
| 缓存/会话 | Redis 7（可选） |
| 记忆 | 自研三层（working/episodic/semantic） |
| 前端 | Next.js 14 + React 18 + Tailwind 3 + shadcn/ui |
| LLM | Ollama / OpenAI / Anthropic 统一接口 |

## 10. 实现状态（节选）

✅ 真实可用：四 Agent 双模式、护栏、JWT、持久化、三层记忆、RAG、真流式、Skill。
🚧 已实现未接线：CoordinatorAgent、Celery、IdentityVerifier。
📌 规划中：数字孪生 3D、可穿戴同步、报告上传解析、随访预约。
详细表见根 `README.md`「实现状态」。
