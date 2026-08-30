# API 面（API_SURFACE）— v0.1.1

> 所有 REST 前缀 `/api/v1`（health 除外）。`PUBLIC_PATHS`（免鉴权）：`/health`、`/api/v1/health`、`/api/v1/auth/login`、`/api/v1/auth/register`、`/api/v1/auth/refresh`、`/api/v1/auth/logout`、`/docs`、`/openapi.json`、`/redoc`。其余需 `Bearer` access token（`type=="access"`）。

## REST 路由

### /auth（auth.py）
- `POST /api/v1/auth/register` — 注册并签发 token（public）
- `POST /api/v1/auth/login` — 登录（public；无库回退 demo 账号）
- `POST /api/v1/auth/refresh` — refresh token 换 access（public，已放行）
- `POST /api/v1/auth/logout` — 登出（public，已放行）
- 注：无 `/auth/me`；当前用户由中间件 `request.state.user_id` 提供

### /consult（consultation.py）
- `POST /api/v1/consult` — 新建会话 `start_consultation`（需认证，owner=当前用户）
- `GET /api/v1/consult/{consult_id}` — 会话状态（需认证，越权 403）

### /patients（patients.py）
- `GET /api/v1/patients` — 列表（需认证）
- `POST /api/v1/patients` — 创建（需认证）
- `GET /api/v1/patients/me` — 当前用户个人档案（需认证；无则 404，前端决定是否建档）
- `GET /api/v1/patients/{patient_id}` — 详情（需认证，越权 403）
- `PUT /api/v1/patients/{patient_id}` — 更新
- `DELETE /api/v1/patients/{patient_id}` — 删除

### /records（medical_records.py）
- `GET /api/v1/records/{record_id}` — 单条病历（需认证，越权 403）
- `GET /api/v1/records?patient_id=` — 按患者列（需认证）

### /knowledge（knowledge.py）
- `GET /api/v1/knowledge/search?q=&top_k=` — 三源检索：`cases/theory/papers` 分桶（需认证）
- `GET /api/v1/knowledge/health` — 检索栈健康（public）

### /health
- `GET /health` 与 `GET /api/v1/health` — 服务存活（public）

## WebSocket
- 路径：`/ws/{session_id}?token=<access>`（Query 参数带 token，`_verify_ws_token` 校验 `type=="access"`，失败 `WS_1008_POLICY_VIOLATION` 关闭）
- 前端 `ConsultationSocket` 发送：`{type:"message",content}`、`{type:"ping"}` 心跳、`{type:"finalize"}` 跑完流程
- 服务端事件（StreamEvent）：`agent_start` / `token` / `agent_end` / `error` / `info` / `state_update`

## 关键数据模型（Pydantic / ORM）

### HandoverManifest（schemas/agent.py）
- `facts: list[str]`、`pending_questions: list[str]`、`risk_flags: list[str]`
- `evidence_level: str`（默认 "C"；A 指南 / B 共识 / C LLM 生成）
- `context: dict`

### Consultation（models/consultation.py）
- `status`: active / completed / emergency
- `current_agent`: 默认 "triage"，由 supervisor 路由驱动
- `history: JSON`、`context: JSON`、`diagnosis: Text`

### MedicalRecord（models/medical_record.py，SOAP）
- `subjective / objective / assessment / plan / diagnosis / department / doctor`（均为 Text）

### Patient（models/patient.py）
- `name/gender/dob/phone/id_number/address`、`allergies(JSON)`、`medical_history(JSON)`、`last_visit`、`status`

### User（models/user.py）
- `email/name/password_hash/role`（patient | doctor）

### KnowledgeSearch 返回（knowledge.py）
- `cases/theory/papers` 三桶，每项 `{title,source,journal,content,score,confidence}`
- 顶层 `route / activated_sources / total`
