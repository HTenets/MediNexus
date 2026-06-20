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
  "patient_id": "string | null",
  "symptoms": "string"
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

### POST `/api/v1/consult/{consult_id}/complete`
完成问诊并提交 SOAP 数据作为情景记忆。

**Request:**
```json
{
  "subjective": "头痛两天，伴低热",
  "objective": "体温37.8°C，咽部充血",
  "assessment": "急性上呼吸道感染",
  "plan": "对症处理，休息补液",
  "diagnosis": "感冒"
}
```

**Response (200):**
```json
{
  "session_id": "session_abc123...",
  "status": "completed",
  "message": "就诊已完成，病历已保存"
}
```

### GET `/api/v1/consult/{consult_id}/history`
获取患者历史就诊记录。

### GET `/health`
健康检查。 → `{"status": "ok"}`

---

## Mock API (开发用)

所有 mock 端点挂载在 `/api/v1/mock/` 下，返回硬编码假数据。

| 端点 | 参数 | 用途 |
|------|------|------|
| `GET /mock/knowledge-cases` | `?query=` | 按症状返回临床病例 |
| `GET /mock/knowledge-theory` | `?query=` | 医学理论/指南 |
| `GET /mock/knowledge-papers` | `?query=` | 前沿论文摘要 |
| `GET /mock/consultation/{id}` | — | SOAP 就诊数据 |
| `GET /mock/records/{patient_id}` | — | 患者历史记录 |
| `GET /mock/profile/{patient_id}` | — | 患者档案 + AI 记忆 |
| `GET /mock/dashboard/{patient_id}` | — | 体征 + 风险 + 建议 |
| `GET /mock/system-status` | — | 服务健康状态 |
| `GET /mock/patients` | — | 患者列表 |

---

## WebSocket

### WS `/ws/{session_id}`
流式对话端点。

**客户端 → 服务端:**
```json
{"type": "message", "content": "我头痛两天了"}
```

**服务端 → 客户端 (6 种事件):**

| event | data | 说明 |
|-------|------|------|
| `agent_start` | `{"agent": "triage"}` | Agent 开始处理 |
| `token` | `{"token": "..."}` | 逐字流式输出 |
| `agent_end` | `{"summary": "...", "manifest": {...}}` | 处理完成 |
| `error` | `{"message": "...", "code": "..."}` | 错误 |
| `info` | `{"message": "..."}` | 系统通知 |
| `emergency` | `{"type":"emergency", "message":"...", "actions":[...]}` | 🚨 紧急 (演示级) |

---

## 数据模型

### HandoverManifest
```python
class HandoverManifest(BaseModel):
    facts: list[str] = []
    pending_questions: list[str] = []
    risk_flags: list[str] = []
    evidence_level: str = "C"   # A=指南 B=共识 C=LLM
    context: dict[str, Any] = {}
```

### SOAPCompletionRequest
```python
class SOAPCompletionRequest(BaseModel):
    subjective: str = ""     # 主诉
    objective: str = ""      # 查体
    assessment: str = ""     # 诊断
    plan: str = ""           # 方案
    diagnosis: str = ""      # 诊断结论
```

### SessionState
```python
@dataclass
class SessionState:
    session_id: str
    patient_id: str
    current_agent: str = "triage"
    history: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
```
