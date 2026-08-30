---
name: project-status
description: MediNexus 当前开发状态（v0.1.1 去伪存真）
metadata: 
  node_type: memory
  type: project
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# MediNexus 项目状态（v0.1.1）

**当前版本:** v0.1.1（2026-08-30 完成「去伪存真」审计与补齐）
**上游里程碑:** v0.2.0（视觉重设计，独立排期，不在此版本）

## 真实可用（✅）
- 四 Agent 问诊链路（Triage → Doctor(+Skill) → Review → Followup），LLM + 规则降级双通道
- `SupervisorAgent` 状态机路由 + `HandoverManifest` 标准交接协议
- 真流式 WebSocket 输出（直连 LLM `chat_stream`，无 LLM 时整段下发，无打字模拟）
- PII 脱敏 + 紧急检测护栏（Agent 前置钩子强制执行）
- JWT 签发 / 刷新 / 注册登录（bcrypt 直接哈希；刷新端点已放行）
- 患者 / 病历 / 会话持久化（PostgreSQL 17 + Alembic；无库时内存降级）
- 自研三层记忆（Working / Episodic / Semantic），复诊自动注入患者档案
- RAG 多源检索 + 知识图谱（BM25 默认，Qdrant 可选，ReviewAgent 独立检索）
- 专科 Skill 系统（内 / 皮肤 / 耳鼻喉 / 心理 / 骨科），按症状自动匹配
- 前端去假数据：dashboard / records / profile 接真实接口，不再写死 `patient_demo_001`

## 已实现但未接线 / 规划中
- 🚧 `CoordinatorAgent` 多科室会诊：代码完成并通过测试，但**未接入路由**（触发词过宽，启用会劫持多数日常问诊）→ v0.2.0
- 🚧 Celery 异步任务：任务已定义，无调用方
- 🚧 `IdentityVerifier` 实名认证：有实现与测试，未接入流水线
- 📌 数字孪生 3D 可视化、可穿戴设备同步、报告上传解析、随访预约（界面标注或未接后端）

## 已移除（避免误用）
- LangGraph 状态图编排（与 `SupervisorAgent` 重复且零调用）
- Mem0 库（三层记忆为自研，未依赖 Mem0）
- 死代码：`mock_data.py` / `core/redis.py` / `graph_rag.py`

## 关键决策（详见 ADR / 路线图）
- 默认 BM25 全文检索；配置 `MEDINEXUS_QDRANT_URL` 且有嵌入服务时切换向量检索
- 密码哈希直接使用 bcrypt（移除 passlib，因其与 bcrypt ≥ 4.1 不兼容）
- 视觉重设计移出 v0.1.1，单独立为 v0.2.0

## 相关
- [[architecture-decisions]]（ADR-001~014，位于 `.claude/codebase/`）
- [[design-decisions]]（D1~D7，位于 `.claude/codebase/`）
- 当前权威路线图：`docs/plan/v0.1.1-plan.md`
- 真伪审计基准：根 `README.md`「实现状态」表
