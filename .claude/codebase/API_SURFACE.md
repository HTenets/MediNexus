# MediNexus API 表面 (API Surface)

> 所有 REST 路由挂载在 `/api/v1` 下。
> WebSocket 端点挂载在 `/ws/{session_id}`。
> 配置类 `backend/app/config.py`, env 前缀 `MEDINEXUS_`。
> 决策基线: 患者自助问诊 | Ollama 默认 + BYO Key | 紧急演示级

---

## REST API

### POST `/api/v1/consult`
开始一个新的问诊会话。

**Request:**
```json
{
  "patient_id": "string | null",     // null → 自动创建
  "symptoms": "string"               // 患者主诉
}
```

**Response (201):**
```json
{
  "session_id": "session_abc123...",
  "patient_id": "patient_def456...",
  "status": "started",
  "current_agent": "triage",
  "created_at": "2026-06-01T12:00:00"
}
```

**错误:** 无 (自动生成 patient_id)

---

### GET `/api/v1/consult/{consult_id}`
查询问诊会话状态和最近历史。

**Response (200):**
```json
{
  "session_id": "session_abc123...",
  "patient_id": "patient_def456...",
  "status": "active",
  "current_agent": "triage",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "agent", "agent": "triage", "content": {...}}
  ]
}
```

**错误:** status="not_found" 时表示会话不存在

---

### GET `/api/v1/patients/{id}`
获取患者信息。(🏗 建设中)

---

### GET `/api/v1/records/{id}`
获取医疗记录。(🏗 建设中)

---

### GET `/health`
健康检查。

**Response (200):**
```json
{"status": "ok"}
```

---

## WebSocket

### WS `/ws/{session_id}`
流式对话端点。

**协议:**

客户端 → 服务器:
```json
{"type": "message", "content": "我头痛两天了"}
```

服务器 → 客户端 (5 种事件类型):

| event | data | 说明 |
|-------|------|------|
| `agent_start` | `{"agent": "triage"}` | 表示某 Agent 开始处理 |
| `token` | `{"token": "..."}` | 逐字输出的流式文本 |
| `agent_end` | `{"summary": "...", "manifest": {...}}` | Agent 处理完成, 携带 HandoverManifest |
| `error` | `{"message": "...", "code": "..."}` | 错误消息 |
| `info` | `{"message": "..."}` | 信息通知 (欢迎语等) |
| `emergency` | `{"type":"emergency", "message":"...", "actions":["..."]}` | **紧急情况** (演示级, 不接真实急救) |

---

## 数据模型

### HandoverManifest (Agent 通信协议)
```python
class HandoverManifest(BaseModel):
    facts: list[str] = []                # 已确定的事实/结论
    pending_questions: list[str] = []     # 还需收集的信息
    risk_flags: list[str] = []           # 风险标记 (如 EMERGENCY_DETECTED)
    evidence_level: str = "C"            # A=指南 B=共识 C=LLM生成
    context: dict[str, Any] = {}         # 跨 Agent 共享上下文
```

### SessionState (会话状态)
```python
@dataclass
class SessionState:
    session_id: str
    patient_id: str
    current_agent: str = "triage"        # 当前处理 Agent
    history: list[dict] = field(...)     # 对话历史
    context: dict[str, Any] = field(...) # 累积上下文
```

### GraphState (LangGraph TypedDict)
```python
class GraphState(TypedDict):
    session_id: str
    patient_id: str
    current_agent: str
    messages: list[dict]
    context: dict[str, Any]
    pending_questions: list[str]
    risk_flags: list[str]
    evidence_level: str                  # A/B/C
    agent_output: Optional[str]          # 流式输出
    error: Optional[str]                 # 错误信息
```

---

## 重要设计约束

### 免责声明要求
- 患者自助问诊场景 → 每个 `HandoverManifest` 的 `facts` 末尾追加医疗免责声明
- 紧急情况 (`EMERGENCY_DETECTED`) → 免责声明替换为急救指引
- 详见 `CONVENTIONS.md` 第 1b 节

### BYO Key 原则
- 项目不内置 API Key
- 用户通过 `.env` 配置 (`MEDINEXUS_LLM_PROVIDER`, `MEDINEXUS_OPENAI_KEY`, 等)
- 无 Key 时自动降级到规则引擎, 响应中标注降级模式
