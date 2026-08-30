---
name: architecture-decisions
description: MediNexus 架构关键决策记录 (ADR)
metadata: 
  node_type: memory
  type: reference
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# 架构决策记录

## ADR-001: Agent 间通信协议
**决定:** 所有 Agent 间通信使用结构化 `HandoverManifest` (Pydantic 模型), 而非自由文本。
**原因:** 调研阶段发现 Agent 交接时自由文本导致信息丢失和误解。
**格式:** `{facts[], pending_questions[], risk_flags[], evidence_level, context}`

## ADR-002: 证据等级标记
**决定:** 所有临床建议带 `evidence_level` 标记 (A/B/C)。
**原因:** 调研发现 LLM 生成的有害建议因语气自信更容易被采纳。
**规则:** A=指南, B=共识, C=LLM 生成。Review Agent 据此决定审查严格度。

## ADR-003: 分层 Guardrail
**决定:** Guardrail 分 L1(在线同步), L2(异步), L3(离线) 三级。
**原因:** Guardrail 延迟影响用户体验, L1 必须在 100ms 内完成。
**当前实现:** L1 位置在 `supervisor.py` 的 pre-process hook 中。

## ADR-004: 分层记忆系统
**决定:** 三层次记忆 (Working + Episodic + Semantic) 而非单层。
**原因:** 不同场景需要不同粒度和时效的记忆。
**架构:** MemoryManager 协调各层检索, 按需注入 Agent context。

## ADR-005: LLM Provider 抽象
**决定:** 统一 `BaseLLMClient` 接口, 支持多 Provider 切换。
**原因:** 避免锁定单一 LLM 提供商, 支持降级策略 (Claude → GPT-4o → Ollama)。

## ADR-006: Skill 模块化
**决定:** 科室知识封装为独立 Skill, 通过 Loader 动态加载。
**原因:** 社区贡献 Skill 无需修改核心代码。

## ADR-007: 代码结构文档化
**决定:** 建立 `.claude/codebase/` 目录维护 AI 可读的代码图谱。
**原因:** AI 长程开发需要结构化的上下文感知, 减少无效读取。

## ADR-008: Ollama 默认 + BYO Key
**决定:** 默认 LLM 使用 Ollama 本地模型, 用户可自备 Key 使用 Claude/GPT。
**原因:** 零成本启动, 开源项目不内置 Key, 用户自主选择 Provider。
**实现:** `llm/` 层已支持多 Provider, 新增降级路径标注和模式提示。

## ADR-009: 患者自助问诊定位
**决定:** 目标用户为普通患者（非医生辅助工具）。
**原因:** 产品定位聚焦, 避免同时满足两个场景导致两边做不好。
**实现:** 前端每次医疗回答后附加免责声明; Agent 输出语言通俗易懂。

## ADR-010: 紧急情况演示级
**决定:** 紧急检测仅做日志记录和前端展示, 不接入真实急救系统。
**原因:** 避免法律风险, 保持项目聚焦。
**实现:** `emergency` WebSocket 事件 + 前端急救信息展示。

## ADR-011: 参考级医疗准确度
**决定:** 诊断建议可溯源到文献/指南, 但不要求临床验证。
**原因:** 患者自助场景下, 参考级准确度足够提供价值, 临床级成本过高。
**实现:** W4 双语 RAG 知识库(指南+药品说明), Review Agent 核查逻辑。

## ADR-012: 降级模式透明
**决定:** Agent 使用规则引擎降级时, 必须在输出中明确告知用户。
**原因:** 用户有权知道当前是 LLM 还是规则引擎, 避免误判可靠度。
**实现:** `facts` 首行插入 `[模式: 规则引擎]` 标注。

## ADR-013: 完整前端产品
**决定:** v0.1.0 前端实现完整产品级体验(全页面+响应式+移动端适配)。
**原因:** 开源项目需要良好的第一印象, 前端质量直接影响项目可信度。
**实现:** W6 高强度投入, 所有页面覆盖加载态/空态/错误态。

## ADR-014: 社区 Skill 延迟到 v0.3.0+
**决定:** 外部 Skill 加载和分发机制延迟到 v0.3.0 实现。
**原因:** v0.1.0 聚焦核心闭环, 避免基础设施分散注意力。
**实现:** `loader.py` 预留接口不动, 仅维护 `builtin/` 内置 Skill。
