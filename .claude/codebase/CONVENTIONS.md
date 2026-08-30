# 代码约定（CONVENTIONS）— v0.1.1

## 命名
- Agent 类后缀 `Agent`（`TriageAgent` 等），每个 Agent 独立子目录 `agents/<name>/agent.py` + `prompt.py`。
- 用 `@registry.register` 装饰器按 `instance.name` 注册，便于 supervisor 路由。
- LLM Provider 客户端统一继承 `BaseLLMClient`，实现 `chat()` / `chat_stream()`。
- Pydantic 模型请求/响应分离（`XxxRequest` / `XxxResponse`），字段带中文 `description`，必要时 `Field(pattern=...)`。

## 结构
- 后端分层：`agents/`（智能体）、`app/`（api/schemas/models/repositories/core/middlewares）、`guardrails/`、`knowledge/`、`memory/`、`llm/`、`orchestration/`、`workers/`。
- 路由前缀：所有 REST 挂 `/api/v1`；子路由 `/consult`、`/patients`、`/records`、`/auth`、`/knowledge`、`/health`。
- 前端：`frontend/src/app/`（页面）、`components/`（组件）、`lib/`（api.ts / websocket.ts）。

## 异步
- 全程 `async def` + `await`；DB 用 SQLAlchemy 2.0 `AsyncSession`；LLM/RAG/记忆均为 async。

## 错误处理与降级
- 护栏/记忆/检索一律 **best-effort**：`try/except` 仅 `logging.warning` + 降级，**绝不阻断问诊**。
- WebSocket 返回结构化 `error` 事件（含 `code`），前端按事件渲染。
- 无 LLM 时（provider 返回 None）自动降级规则引擎；无 Redis/DB 时降级进程内存储。

## 交接协议
- Agent 间通过 `HandoverManifest`（Pydantic）结构化交接：`facts/pending_questions/risk_flags/evidence_level/context`。
- 规则引擎降级输出首行标注 `[模式: 规则引擎]`。
