# 依赖图（DEPENDENCY_GRAPH）— v0.1.1

## 核心依赖边
- `main.py` → `create_rag_query()` + `create_llm_client()` → 注入 `supervisor.rag_query` / `supervisor.llm_client`
- `SupervisorAgent` → 注入 `MemoryManager` + `rag_query` 给各 Agent（`run_agent` / `_recall_memory`）
- `agents`（BaseAgent）→ 调用 `guardrails`（pii_sanitizer、emergency_detector）于 `on_pre_process` 前置钩子
- `Narrative` → 依赖 `llm.client`（`stream_narrative` 用 `llm.chat_stream`）
- `ReviewAgent` → 依赖 `rag_query`（supervisor 注入）独立查询知识库
- `DoctorAgent` → 依赖 `skills/`（专科知识）+ `memory`（patient_history）
- 前端 `lib/api.ts` → 后端 REST（`/api/v1`）+ `lib/websocket.ts` → 后端 WS `/ws/{id}`

## 影响范围提示
- 改 `supervisor.py` 路由/注入逻辑 → 影响全部 Agent 行为
- 改 `rag.py` / `retriever.py` / `source.py` → 影响 ReviewAgent 与 `/knowledge/search` 质量
- 改 `guardrails/` → 影响所有 Agent 输入安全（前置钩子全局生效）
- 改 `memory/manager.py` → 影响复诊档案注入
- 改 `llm/factory.py` → 影响全部 LLM 调用与降级
