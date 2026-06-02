# MediNexus 构建状态 (Build Status)

> 追踪每个组件的实现状态。对 AI 而言: 知道什么已就绪、什么待实现。
> 时间: 第 2 周结束 (2026-06-01), 即将进入第 3 周。
> 决策基线: 详见 [[design-decisions]]

---

## 总体进度 (已调整: 基于设计决策)

```
第1周 ████████████████████ 100%  项目基础设施
第2周 ████████████████████ 100%  Agent 框架 + Triage Agent
第3周 ████████████████████ 100%  Skill 系统 + Doctor Agent ✅ 已升级为: Ollama 优化 + 中英双语 + 降级路径
第4周 ░░░░░░░░░░░░░░░░░░░░   0%  RAG 知识库 + Review Agent   [增强: 参考级需要双语知识库]
第5周 ░░░░░░░░░░░░░░░░░░░░   0%  记忆系统 + 病历管理 + Followup
第6周 ████████████████████ 100%  前端完整产品 [强度提升: 全页面+响应式+免责声明]
第7周 ░░░░░░░░░░░░░░░░░░░░   0%  安全 + Guardrail + Coordinator [缩减: 紧急降为演示级]
第8周 ░░░░░░░░░░░░░░░░░░░░   0%  部署 + 文档 + BYO Key 说明 + Ollama 部署指南
```

### 设计决策摘要 (影响各周)
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
| SupervisorAgent | `orchestration/supervisor.py` | 路由逻辑 + 会话管理 |
| StreamManager | `orchestration/stream.py` | WebSocket 流式事件 |
| Consultation API | `app/api/consultation.py` | POST/GET + WebSocket |
| Main entry | `app/main.py` | FastAPI 应用 + WS 端点 |
| Router | `app/api/router.py` | 路由汇总前缀 |
| Config | `app/config.py` | pydantic-settings 配置 |
| Database core | `app/core/database.py` | async SQLAlchemy |
| Health API | `app/api/health.py` | 健康检查 |
| LLM Client | `llm/client.py` | 抽象 + chat/chat_stream |
| LLM providers | `llm/providers/` | OpenAI/Anthropic/Ollama |
| 前端 chat 组件 | `src/components/chat/` | ChatContainer, ChatMessage, ChatInput |
| WebSocket 客户端 | `src/lib/websocket.ts` | 含自动重连 |
| API 客户端 | `src/lib/api.ts` | REST 封装 |
| 集成测试 | `tests/integration/` | 12 个测试用例 |
| Patient model | `app/models/patient.py` | ORM 模型 |
| Consultation model | `app/models/consultation.py` | ORM 模型 |

### 🏗 部分完成 (骨架就绪, 待实现核心逻辑)

| 组件 | 文件 | 已就绪 | 待完成 |
|------|------|--------|--------|
| DoctorAgent | `agents/doctor/agent.py` | 类定义 + BaseAgent 继承 | run() 核心诊断逻辑 |
| Doctor prompt | `agents/doctor/prompt.py` | — | 诊断推理提示词 |
| DiagnosisFlow | `agents/doctor/diagnosis_flow.py` | 状态枚举 | 状态机转换逻辑 |
| Skill base | `agents/doctor/skills/base.py` | 类定义 | 完整抽象接口 |
| Skill loader | `agents/doctor/skills/loader.py` | 骨架 | 动态加载实现 |
| Skill registry | `agents/doctor/skills/registry.py` | 骨架 | 注册/查找逻辑 |
| ReviewAgent | `agents/review/agent.py` | 类定义 + stub run() | 8 维审查矩阵 |
| Review prompt | `agents/review/prompt.py` | — | 审查提示词 |
| Review rules | `agents/review/rules/` | 文件结构 | 药物相互作用 + 禁忌症规则 |
| CoordinatorAgent | `agents/coordinator/agent.py` | 类定义 + invite 方法 | 会诊状态机 + 专家汇总 |
| Coordinator prompt | `agents/coordinator/prompt.py` | — | 会诊提示词 |
| ConsultationProtocol | `agents/coordinator/consultation_protocol.py` | — | 会诊协议 |
| FollowupAgent | `agents/followup/agent.py` | 类定义 + schedule | 完整随访逻辑 |
| Followup prompt | `agents/followup/prompt.py` | — | 随访提示词 |
| Followup scheduler | `agents/followup/scheduler.py` | — | 调度实现 |
| Patients API | `app/api/patients.py` | 文件存在 | CRUD 实现 |
| Records API | `app/api/medical_records.py` | 文件存在 | CRUD 实现 |
| Redis core | `app/core/redis.py` | 文件存在 | 连接初始化 |
| Logging middleware | `app/middlewares/logging.py` | 文件存在 | 请求/响应日志 |
| Dockerfiles | `infrastructure/docker/` | 基础骨架 | 多阶段构建 |
| Frontend pages | `src/app/pages/` | consultation + records + profile | 完整 UI 和数据绑定 |

### 📋 待实现 (文件未创建或为预留)

| 组件 | 说明 | 计划周 | 备注 |
|------|------|--------|------|
| 4 个科室 Skill | internal_medicine, dermatology, ent, mental_health | W3 | 提示词须为 Ollama 优化 |
| RAGQuery | Qdrant 向量检索 | W4 | 需双语知识库支持 |
| VectorStore | Qdrant 客户端操作 | W4 | — |
| Knowledge loader | 文档加载/分块 | W4 | 中文+英文指南加载 |
| ReviewAgent 完整 | 审查提示词 + 规则 | W4 | 参考级审查, 非临床级 |
| MemoryManager | Mem0 集成 | W5 | — |
| Episodic memory | 情景记忆 | W5 | — |
| Semantic memory | 语义记忆 | W5 | — |
| Auth/JWT | OAuth 2.0 + JWT | W7 | — |
| Guardrails | Emergency/PII/Identity | W7 | **演示级**: 仅日志+前端提示, 不涉及真实急救 |
| 免责声明系统 | 所有医疗回答后附加 | W6 | **患者自助问诊的必要风控**, 前端+后端都要 |
| BYO Key 配置 | 用户自行配置 LLM Key | W8 | 文档 + env 引导 |
| 降级提示机制 | 降级时输出模式提示 | W3-W4 | 每个 Agent 降级路径须附模式标注 |
| Plugin SDK | Plugin 基类 + 钩子 | — (v0.3.0+) | 延迟 |
| GraphRAG | 知识图谱检索 | — (v0.3.0+) | 延迟 |

---

## 已知问题 / Todo

| 问题 | 位置 | 说明 | 优先级 |
|------|------|------|--------|
| TriageAgent evidence_level 硬编码 | `agents/triage/agent.py:55` | `evidence_level="C"` 写死 | low |
| In-memory session store | `orchestration/supervisor.py:23` | `_sessions: dict` 非持久化 | medium (W5 修复) |
| DoctorAgent stub | `agents/doctor/agent.py` | `run()` 返回空 skeleton | high (W3 修复) |
| ReviewAgent stub | `agents/review/agent.py` | `run()` 返回空 skeleton | medium (W4 修复) |
| CoordinatorAgent stub | `agents/coordinator/agent.py` | `run()` 基本骨架 | medium (W7 修复) |
| FollowupAgent stub | `agents/followup/agent.py` | `run()` 基本骨架 | medium (W5 修复) |
| Has_prescription 硬编码 | `orchestration/supervisor.py:44` | 路由逻辑的条件目前写死 | low |
| **缺失: 免责声明系统** | — | 患者自助问诊须在每次响应后附加医疗免责声明 | **high (W6 前须完成)** |
| **缺失: 降级模式标注** | — | Ollama 降级时须明确告知用户当前模式 | medium (W3-W4) |
| **缺失: BYO Key 文档** | — | 用户配置 LLM Key 的流程未文档化 | low (W8) |

---

## 测试覆盖率

```
tests/
├── integration/
│   ├── test_consultation_flow.py  — 12 测试用例 (完整就诊流程)
│   └── test_agent_communication.py — Agent 通信测试
├── unit/
│   ├── agents/
│   │   ├── test_skill_system.py   — 19 测试用例 (BaseSkill/Registry/BuiltinSkills)  ✅ 新增 W3
│   │   └── test_doctor_agent.py   — 16 测试用例 (规则模式/LLM模式/Skill集成)        ✅ 新增 W3
│   ├── knowledge/  — 待实现
│   └── memory/     — 待实现
```

**总测试数: 62** (27 原有 + 35 新增 W3)
当前测试重点: TriageAgent + DoctorAgent + Skill 系统 + Agent 注册
