---
name: handover-manifest
description: Agent 间通信协议 HandoverManifest 定义和使用规范
metadata: 
  node_type: memory
  type: reference
  originSessionId: ffec3202-7440-45bc-a8c6-7add1b375b89
---

# HandoverManifest — Agent 通信协议

**位置:** `backend/app/schemas/agent.py`

```python
class HandoverManifest(BaseModel):
    facts: list[str] = []                # 已确定的事实/结论
    pending_questions: list[str] = []     # 还需收集的信息
    risk_flags: list[str] = []           # 风险标记 (如 EMERGENCY_DETECTED)
    evidence_level: str = "C"            # A=指南 B=共识 C=LLM生成
    context: dict[str, Any] = {}         # 跨 Agent 共享上下文
```

## 使用规则

1. **所有 Agent 通信必须使用此模型** — 禁止直接传自由文本
2. `facts` — 用项目符号列表形式的人类可读描述
3. `risk_flags` — 大写蛇形命名 (如 `EMERGENCY_DETECTED`)
4. `evidence_level` — 必须设置, 不允许留空
5. `context` — Agent 通过此字段传递非结构化数据给下游

## 数据流

```
TriageAgent.run()
  → HandoverManifest(context.triage_result)
  → session.context.update(manifest.context)
  → route() → next agent

DoctorAgent.run()
  → HandoverManifest(context.diagnosis_result, context.prescription)
  → ...
```

## 相关

- [[architecture-decisions]] (ADR-001, ADR-002)
