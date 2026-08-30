# MediNexus 系统架构（v0.1.1）

> 本文档描述当前 **v0.1.1** 真实实现的架构。能力真伪以根 `README.md`「实现状态」表为准；
> 设计演进与历史设想见 `docs/design/architecture-design.md`（已标注为历史设想，含未落地内容）。

## 1. 总体架构

MediNexus（医枢）是基于**多智能体协作**的开源智能医疗诊断平台，面向普通患者自助问诊（参考级准确度，非临床级）。

```
用户 → TriageAgent → DoctorAgent(+Skill) → ReviewAgent → FollowupAgent → 输出
                              ↑
                    SupervisorAgent（状态机路由 + 记忆/RAG 注入）
```

- **SupervisorAgent**：会话管理 + Agent 路由 + 记忆/RAG 注入；按分诊结果、紧急程度、上下文在 Agent 间路由。
- **HandoverManifest**：Agent 间结构化交接协议（Pydantic 模型），避免自由文本导致的信息丢失。
- **真流式输出**：WebSocket 直连 LLM `chat_stream` 逐 token 下发；无 LLM 时整段下发，不做打字模拟。

## 2. 四智能体

| Agent | 职责 |
|-------|------|
| **TriageAgent** | 症状评估、科室分诊、紧急程度判定（routine / urgent / emergency） |
| **DoctorAgent** | 多轮问诊与鉴别诊断，自动匹配专科 Skill，输出诊断/方案/风险 |
| **ReviewAgent** | 独立检索知识库验证诊断、复核用药禁忌、标注证据等级 A/B/C |
| **FollowupAgent** | 康复计划与用药提醒、健康档案更新 |

> `CoordinatorAgent`（多科室会诊）已实现并通过测试，但**尚未接入路由**（触发词过宽），计入 v0.2.0。

## 3. 分层记忆系统

自研三层记忆（**未依赖 Mem0 库**），跨会话健康档案：

| 层次 | 有 Redis / DB | 无外部依赖 | 功能 |
|------|--------------|-----------|------|
| Working | Redis（TTL） | 进程内字典 | 当前会话短期状态 |
| Episodic | `consultations` 表 | 进程内列表 | 历史就诊记录 |
| Semantic | `patients` 表 | 进程内字典 | 患者画像（过敏史 / 既往史） |

会话终态自动归档为 Episode；记忆故障仅记日志，不阻断问诊。

## 4. 安全护栏

- **PII 脱敏器**：手机号 / 身份证 / 邮箱等自动识别脱敏
- **紧急检测器**：中英文关键词 + 正则，识别 6 类紧急信号，**强制覆盖** Agent 输出并触发应急响应

## 5. RAG 知识增强

- 三源知识库（临床病例 0.8 / 医学理论 0.6 / 最新论文 0.3），RRF + Z-score 融合
- **默认 BM25 全文检索**（内置知识库，零依赖）；配置 `MEDINEXUS_QDRANT_URL` 且有嵌入服务时切换向量检索，BM25 作为降级链路
- 知识图谱（症状 → 疾病）增强召回；对外 `GET /api/v1/knowledge/search`

## 6. LLM 多提供商

统一客户端接口，支持热切换：Ollama（默认，本地）/ OpenAI / Anthropic；无 LLM 时无缝降级规则引擎。

## 7. 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + Python 3.12+，自研 `SupervisorAgent` 状态机 |
| 数据库 | PostgreSQL 17（SQLAlchemy 2.0 异步 + Alembic） |
| 检索 | 内置 BM25（默认）/ Qdrant（可选）/ 知识图谱 |
| 缓存 / 会话 | Redis 7（可选） |
| 记忆 | 自研三层（working / episodic / semantic） |
| 前端 | Next.js 14 + React 18 + Tailwind 3 + shadcn/ui + framer-motion |
| LLM | Ollama / OpenAI / Anthropic 统一接口 |

## 8. 实现状态（节选）

✅ = 真实可用；🚧 = 已实现未接线；📌 = 规划中。完整表见根 `README.md`。

- ✅ 四 Agent 双模式问诊、护栏、JWT、持久化、三层记忆、RAG、真流式、Skill
- 🚧 CoordinatorAgent（未接线）、Celery（无调用）、IdentityVerifier（未接入）
- 📌 数字孪生 3D、可穿戴同步、报告上传解析、随访预约

## 9. 文档导航

- 架构决策（ADR）：`.claude/codebase/architecture-decisions.md`
- 产品设计决策（D1~D7）：`.claude/codebase/design-decisions.md`
- 模块 / Agent 权威清单（AI 索引）：`.claude/codebase/MODULE_MAP.md`
- API 权威清单（AI 索引）：`.claude/codebase/API_SURFACE.md`
- 路线图：`docs/plan/v0.1.1-plan.md`
