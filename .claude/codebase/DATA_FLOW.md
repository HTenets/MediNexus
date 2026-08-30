# 数据流（DATA_FLOW）— v0.1.1

## 问诊流水线（真实路径）

```
用户(WS /ws/{id}?token)
  → main.py 校验 token，建/恢复 SessionState
  → SupervisorAgent.route(): 依 current_agent 与上下文在 Agent 间路由
  → 依次运行:
      TriageAgent  →(HandoverManifest)→
      DoctorAgent(+Skill，DiagnosisState: INITIAL→HISTORY_TAKING→DIFFERENTIAL→TREATMENT→COMPLETED)
      →(HandoverManifest)→
      ReviewAgent(注入 rag_query 独立检索，标 risk_flags/evidence_level)
      →(HandoverManifest)→
      FollowupAgent(随访计划)
  → 每 Agent 运行前: BaseAgent.on_pre_process 先 PII 脱敏，再 EmergencyDetector(紧急则强制覆盖输出)
  → 每 Agent 产出 HandoverManifest → Narrative.render_manifest/stream_narrative
       (MEDINEXUS_STREAM_NARRATIVE=true 时 LLM 流式渲染通俗口述；无 LLM 整段下发，不模拟打字)
  → StreamManager 封装 StreamEvent 经 WS 逐 token/事件下发前端
  → 会话终态(complete/emergency_protocol): SupervisorAgent 归档 Episode + 同步 working memory
```

## 记忆注入
- `SupervisorAgent.run_agent` → `_recall_memory` → `MemoryManager.retrieve()`
  - 组合 `SemanticMemory.format_profile`（过敏史/既往史）+ `EpisodicMemory.format_recall`（既往就诊）为 `context["patient_memory"]`
  - 注入各 Agent；DoctorAgent 并入 `patient_history`，ReviewAgent 并入复核提示（用药禁忌依赖过敏史）

## RAG 检索
- `main.py` 启动 `create_rag_query()`（BM25 始终 + 可选 Qdrant + 知识图谱）→ `set_rag_query()` → `supervisor.rag_query`
- ReviewAgent 经 `rag_query` 独立查询；`GET /api/v1/knowledge/search` 对外暴露三源分桶结果
- 三源权重：CLINICAL_CASES=0.8 / MEDICAL_THEORY=0.6 / LATEST_PAPERS=0.3；RRF(k=60)+Z-score 融合

## 降级链路
- 无 LLM（provider=None）→ 规则引擎，输出首行 `[模式: 规则引擎]`
- 无 Redis/DB → 进程内存储；记忆/检索故障仅记日志不阻断
