---
name: design-decisions
description: 2026-06-01 需求对齐讨论确定的 7 项设计决策
metadata: 
  node_type: memory
  type: reference
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# 设计决策基线 (Design Decisions)

> 2026-06-01 讨论确定。这些决策影响所有后续开发。

## 7 项核心决策

### D1: 目标用户 — 患者自助问诊
- 普通用户输入症状，AI 给出参考建议
- **不**要求临床级准确度，**不**用于真实医疗场景
- 前端须显示医疗免责声明
- 架构影响: 参考 [[architecture-decisions]] (ADR-008)

### D2: 医疗准确度 — 参考级
- 诊断建议可溯源到文献/指南，但不需要临床验证
- W4 RAG 需要双语知识库（中文+英文指南、药品说明书）
- 证据等级 A/B/C 标记保留，但以 C 级为主

### D3: LLM 策略 — Ollama 默认 + BYO Key + 降级
- 默认: Ollama 本地模型（免费）
- 增强: 用户通过 `.env` 配置 Claude/GPT-4o Key
- 无 LLM 可用时: 降级到规则引擎/关键词匹配
- 降级输出须标注 `[模式: 规则引擎]`
- 项目**不内置任何 API Key**

### D4: 多语言 — 中文为主英文备用
- UI 语言: 中文（英文后续 v0.2.0）
- Agent 输出: 默认中文，英文用户可切换
- 知识库: 中英文双语索引
- Prompt: 已实现双语（中文为主，英文 fallback）

### D5: Skill 生态 — 社区维护
- `builtin/` 内置 Skill 保留
- 外部加载接口 (loader.py) 预留到 v0.3.0+
- 社区分发机制 v0.3.0+ 再设计

### D6: 前端深度 — 完整产品
- 全页面：首页、问诊对话页、病历页、个人中心
- 响应式布局，移动端可用
- 所有页面覆盖 加载态/空态/错误态
- 医疗回答后附加免责声明

### D7: 紧急情况 — 演示级
- 不接入真实急救系统
- 后端记录日志 + WebSocket 发送 `emergency` 事件
- 前端展示急救信息和一键呼叫提示
- 事件格式: `{event: "emergency", data: {type, message, actions}}`

## 决策影响矩阵

| 决策 | 影响组件 | 修改文件 |
|------|---------|---------|
| D1 患者自助 | 前端所有页面 + WebSocket 渲染 | `frontend/src/app/consultation/`, `main.py` |
| D2 参考级 | RAG 知识库 + Review Agent | `knowledge/`, `agents/review/` |
| D3 Ollama 默认 | 所有 Agent + Config | `agents/*/agent.py`, `app/config.py` |
| D4 中文为主 | Agent prompt + 知识库 | `agents/*/prompt.py`, `knowledge/loader.py` |
| D5 Skill 社区 | 不影响当前架构 | — |
| D6 完整前端 | 所有前端页面 | `frontend/src/app/*` |
| D7 紧急演示级 | Guardrails + WebSocket + 前端 | `guardrails/`, `main.py`, `frontend/` |
