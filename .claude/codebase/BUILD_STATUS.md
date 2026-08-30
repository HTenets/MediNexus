# 构建状态（BUILD_STATUS）— v0.1.1

> 更新: 2026-08-30（去伪存真审计完成）

## 版本
- 当前: **v0.1.1**（"完善/去伪"，视觉重设计移入 v0.2.0）
- 测试: **250 passed**（pytest）

## 已实现并真实可用（✅）
- 四 Agent 双模式问诊链路（LLM + 规则降级）
- SupervisorAgent 状态机路由 + HandoverManifest 交接
- 真流式 WebSocket（直连 LLM `chat_stream`，无打字模拟）
- PII 脱敏 + 紧急检测护栏（前置钩子）
- JWT 签发/刷新/登录（bcrypt 直哈希；refresh/logout 已放行）
- 患者/病历/会话持久化（PostgreSQL 17 + Alembic；无库内存降级）
- 自研三层记忆（working/episodic/semantic），复诊注入档案
- RAG 多源检索 + 知识图谱（BM25 默认，Qdrant 可选）
- 专科 Skill（内/皮肤/耳鼻喉/心理/骨科）
- 前端去假数据（dashboard/records/profile 接真实接口）

## 已实现但未接线 / 规划中（🚧/📌）
- 🚧 CoordinatorAgent（多科室会诊，触发词过宽未接入）
- 🚧 Celery 异步任务（无调用方）
- 🚧 IdentityVerifier（未接入流水线）
- 📌 数字孪生 3D、可穿戴同步、报告上传解析、随访预约

## 已移除（曾误标为可用）
- LangGraph `orchestration/graph.py`（与 SupervisorAgent 重复且零调用）
- Mem0 库（三层记忆为自研，未依赖 Mem0）
- 死代码：`mock_data.py`、`core/redis.py`、`graph_rag.py`

## 验收
- [x] `pytest` 250 passed
- [x] `tsc --noEmit` 无错误
- [x] `npm run build`（17 路由）
- [ ] 全新环境 `docker-compose` + `alembic upgrade head` 全流程可用（手动验收中）
