# MediNexus 数据流 (Data Flow)

> 描述请求从进入系统到输出结果的完整路径。
> 涵盖 REST / WebSocket / Agent Pipeline 三种数据流。
> 决策基线: 患者自助问诊 | Ollama 默认 + BYO Key 降级 | 紧急演示级

---

## 1. REST 问诊流 (POST /consult)

```mermaid
sequenceDiagram
    participant Client as 前端/客户端
    participant API as FastAPI (consultation.py)
    participant Supervisor as SupervisorAgent
    participant Registry as AgentRegistry
    
    Client->>API: POST /api/v1/consult {symptoms, patient_id?}
    API->>Supervisor: create_session(session_id, patient_id)
    Supervisor->>Supervisor: 构造 SessionState(current_agent="triage")
    Supervisor-->>API: SessionState
    API-->>Client: 201 {session_id, patient_id, status, current_agent}
```

---

## 2. WebSocket 流式问诊流

```mermaid
sequenceDiagram
    participant Client as 前端
    participant WS as WebSocket (main.py)
    participant Stream as StreamManager
    participant Supervisor as SupervisorAgent
    participant Agent as TriageAgent
    participant Registry as AgentRegistry
    
    Client->>WS: ws.connect(/ws/{session_id})
    WS->>WS: 接受连接
    WS-->>Stream: emit_info("欢迎使用...")
    Stream-->>Client: {"event": "info", "data": {"message": "..."}}
    
    loop 对话循环
        Client->>WS: {"type": "message", "content": "我头痛"}
        WS->>WS: JSON 解析校验
        WS-->>Stream: emit_agent_start("triage")
        Stream-->>Client: {"event": "agent_start", "data": {"agent": "triage"}}
        
        WS->>Supervisor: run_agent(session, user_input)
        Supervisor->>Registry: get("triage") → TriageAgent 类
        Registry-->>Supervisor: TriageAgent 类
        Supervisor->>Agent: context = {symptoms, messages, llm_client, ...}
        Supervisor->>Agent: on_pre_process(context) [Plugin 注入点]
        Agent->>Agent: run(context)
        Note over Agent: LLM 模式 | 关键词降级模式
        Agent-->>Supervisor: HandoverManifest {facts, risk_flags, ...}
        Supervisor->>Supervisor: route() → 决定下一个 Agent
        Supervisor-->>WS: HandoverManifest
        
        WS->>WS: 渲染 summary_text
        loop 逐字输出
            WS-->>Stream: emit_token(ch)
            Stream-->>Client: {"event": "token", "data": {"token": "字"}}
        end
        
        WS-->>Stream: emit_agent_end(summary, manifest)
        Stream-->>Client: {"event": "agent_end", "data": {...}}
    end
    
    Client->>WS: ws.disconnect
    WS->>WS: 清理资源
```

---

## 3. Agent Pipeline 内部数据流

```mermaid
flowchart TB
    subgraph Input["用户输入"]
        A1["POST /consult (REST)"]
        A2["WebSocket message"]
    end
    
    subgraph Orchestration["编排层"]
        B["SupervisorAgent.route()"]
        C["SupervisorAgent.run_agent()"]
        D["ConsultationGraph (LangGraph)"]
    end
    
    subgraph Agents["Agent Pipeline"]
        T["TriageAgent<br/>评估紧急度+科室"]
        Doc["DoctorAgent<br/>+ Skill<br/>诊断推理"]
        R["ReviewAgent<br/>处方审查"]
        F["FollowupAgent<br/>随访计划"]
        Coor["CoordinatorAgent<br/>多科室会诊"]
        Em["⚠️ 紧急协议 (演示级)<br/>写日志 + 前端展示急救信息<br/>不接入真实急救系统"]
    end
    
    subgraph Output["输出"]
        O1["HandoverManifest → WebSocket 流式输出"]
        O2["结构化病历 → 数据库"]
        O3["随访计划 → scheduler"]
        O4["免责声明 → 每次医疗回答后附加"]
    end
    
    Input --> B
    B --> C
    
    C --> T
    T -->|"emergency"| Em
    T -->|"routine/urgent"| Doc
    
    Doc -->|"有处方, 需审查"| R
    Doc -->|"无需处方"| F
    
    R -->|"审查通过"| F
    R -->|"审查不通过"| Doc
    
    Coor -->|"多科室意见"| R
    Doc -->|"需会诊"| Coor
    
    F --> O1
    F --> O2
    F --> O3
    F -.->|"所有输出均附带"| O4
    Em --> O1
    
    D -.->|"备选: LangGraph 状态图"| Agents
```

---

## 4. 数据格式转换

```
用户输入 (string)
    ↓
SupervisorAgent 构造 context dict:
  {
    "symptoms": "我头痛两天了",
    "messages": [...],
    "patient_history": "...",
    "llm_client": None | LLMClient,
    ... (plugin 注入的额外数据)
  }
    ↓
on_pre_process (Plugin Hook) → 可修改 context
    ↓
Agent.run(context) → 内部使用 context 做推理
    ↓
HandoverManifest:
  {
    "facts": ["患者症状: 头痛两天", "推荐科室: 内科"],
    "pending_questions": ["持续时间", "疼痛程度(1-10)"],
    "risk_flags": [],
    "evidence_level": "C",
    "context": {"triage_result": {...}, "department": "internal_medicine"}
  }
    ↓
on_post_process (Plugin Hook) → 可修改 manifest
    ↓
SupervisorAgent:
  - session.context.update(manifest.context)  # 累积上下文
  - route() 决定下一个 agent
  - session.current_agent = next_agent
    ↓
StreamManager → emit_token/emit_agent_end → WebSocket → 前端渲染
```

---

## 5. LLM 模式选择 (运行时决策)

```mermaid
flowchart LR
    Input["context.llm_client"] --> Check{"llm_client 是否可用?"}
    Check -->|"可用 (Ollama / BYO Key)"| LLM["LLM 模式: 调用 chat() 获取推理结果"]
    Check -->|"不可用 (无 Key / 连接失败)"| Rule["规则引擎模式: 关键词降级"]
    LLM --> Output["输出 + 证据等级标记"]
    Rule --> Output2["输出 + 首行标注 [模式: 规则引擎]"]
```

### 模式标注规则
| 模式 | 标注方式 | 位置 |
|------|---------|------|
| Ollama 本地模型 | 无 (正常模式) | — |
| 用户 BYO Key (Claude/GPT) | 无 (正常模式) | — |
| 降级-规则引擎 | `"[模式: 规则引擎] 当前为离线降级模式..."` | facts 首行 |
| 降级-LLM 超时 | `"[模式: 降级] LLM 服务异常, 使用备用规则..."` | facts 首行 |

---

## 6. 免责声明注入流程

```mermaid
flowchart TB
    subgraph AgentOutput["Agent 输出"]
        M["HandoverManifest.facts"]
        R["risk_flags 含 EMERGENCY_DETECTED?"]
    end
    
    subgraph Inject["免责声明注入 (main.py WebSocket 处理)"]
        Check2{"risk_flags 含 emergency?"}
        NormalDisclaimer["追加: 医疗免责声明<br/>'不构成医疗诊断建议...'"]
        Emergency["替换为: 急救指引<br/>'请立即拨打 120...'"]
    end
    
    subgraph StreamOutput["流式输出"]
        Emit["emit_token() → 渲染声明<br/>emit_agent_end()"]
    end
    
    M --> Check2
    R --> Check2
    Check2 -->|"否"| NormalDisclaimer
    Check2 -->|"是"| Emergency
    NormalDisclaimer --> Emit
    Emergency --> Emit
```

---

## 7. RAG 知识库数据流 (W4 新增)

```mermaid
flowchart TB
    subgraph Input["查询输入"]
        Q["症状/诊断文本"]
    end

    subgraph Sources["三路知识源"]
        A["临床病例库 (0.8)<br/>Semantic Chunking<br/>384 tokens"]
        B["医学理论库 (0.6)<br/>Hierarchical Chunking<br/>768 parent / 192 child"]
        C["最新论文库 (0.3)<br/>Recursive Chunking<br/>512 tokens"]
    end

    subgraph Vector["向量检索 (Qdrant)"]
        Emb["Embedding<br/>(bge-m3 / text2vec)"]
        VS["VectorStore.search_batch<br/>并行搜索 3 个集合"]
    end

    subgraph Fusion["融合层 (HF-RAG)"]
        R1["RRF 源内融合<br/>score = 1/(k+rank)"]
        ZS["Z-score 跨源标准化<br/>z = (score-μ)/σ"]
        CW["置信度加权<br/>0.8 / 0.6 / 0.3"]
        SORT["排序 → Top-K"]
    end

    subgraph Fallback["降级路线"]
        BM25["BM25Okapi 全文搜索<br/>自实现 + 中文分词"]
    end

    subgraph KG["知识图谱增强"]
        KGQ["KnowledgeGraph<br/>症状→疾病一跳映射"]
    end

    subgraph Output["输出"]
        FMT["query_formatted()<br/>→ LLM Context"]
    end

    Q --> Emb
    Emb --> VS
    
    VS --> A
    VS --> B
    VS --> C

    A -- "Qdrant 可用" --> R1
    B --> R1
    C --> R1

    A -- "Qdrant 不可用" --> BM25
    B --> BM25
    C --> BM25

    BM25 --> SORT

    R1 --> ZS
    ZS --> CW
    CW --> SORT

    SORT --> FMT

    Q --> KGQ
    KGQ --> FMT

    FMT --> Output
```

### 降级策略

```
Qdrant 可用 + Embedding 正常 → 向量检索路线
Qdrant 不可用 / Embedding 失败 → BM25 全文搜索路线 (自动切换)
Review Agent → 独立 RAGQuery 实例 (不共享 Doctor 的 RAG 结果)
```

---

## 8. 关键数据结构关系

```
SessionState (运行时)
  ├── session_id      → WebSocket 路由
  ├── patient_id      → Patient model FK
  ├── current_agent   → AgentRegistry key
  ├── history         → [{role, content}]
  └── context         → 跨 Agent 共享字典
        ├── triage_result  → {urgency, department, reason, key_info_gaps}
        ├── diagnosis      → DoctorAgent 输出 (TODO)
        ├── prescription   → ReviewAgent 输入 (TODO)
        └── ...plugin 注入字段

HandoverManifest (Agent 间通信)
  ├── facts[]            → 显示给用户的事实列表
  ├── pending_questions[] → 还需追问的问题
  ├── risk_flags[]        → 风险标记
  ├── evidence_level      → A/B/C
  └── context             → 跨 Agent 共享 (合并入 session.context)

Consultation (持久化)
  ├── id, patient_id
  ├── status: active → triaged → diagnosed → reviewed → completed
  ├── diagnosis: Text
  └── created_at
```
