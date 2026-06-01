---
name: week2-learning-resources
description: W2 技术栈学习文档——Agent 框架、LangGraph、WebSocket 流式通信
metadata:
  type: reference
---

# MediNexus W2 技术栈学习指南

> 本文档列出了第 2 周 Agent 框架 + 导诊 Agent 中用到的所有技术，适合新手按顺序学习。

---

## 一、Agent 框架核心

### 1. LangGraph

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | Agent 编排框架，定义诊断流程的状态图（StateGraph）——每个节点是一个 Agent，边是路由逻辑 |
| **如何使用** | `orchestration/graph.py`：构建 `StateGraph(GraphState)` → `add_node("triage", fn)` → `add_conditional_edges()` → `compile()` → `ainvoke()` |
| **关键概念** | `StateGraph`（状态图）、`GraphState`（TypedDict 状态）、`Node`（处理函数）、`ConditionalEdge`（条件路由）、`END`（终止节点） |
| **关键代码** | `workflow = StateGraph(GraphState)` → `workflow.add_node("triage", triage_fn)` → `workflow.add_conditional_edges("triage", router)` → `app = workflow.compile()` |
| **与普通图的区别** | 每个节点接收当前状态，返回状态更新；边决定下一个执行哪个节点；内置流式和并行支持 |
| **新手学习重点** | StateGraph 的节点/边概念、TypedDict 状态定义、条件路由（`add_conditional_edges`）、`ainvoke` vs `astream` |
| **官方文档** | https://langchain-ai.github.io/langgraph/ |

### 2. BaseAgent 抽象类

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 所有 Agent 的基类，定义统一的 `run()` 接口 + 生命周期钩子 |
| **文件位置** | `backend/agents/base.py` |
| **核心接口** | `async def run(context) -> HandoverManifest` — 每个 Agent 必须实现 |
| **预留钩子** | `on_pre_process(context)` — 处理前调用（身份验证/PII 脱敏）；`on_post_process(manifest)` — 处理后调用（审计日志） |
| **扩展点** | `register_tool(name, fn)` 注册工具函数；`execute_tool(name, **kwargs)` 调用工具 |
| **新手学习重点** | `ABC`（抽象基类）、`@abstractmethod`、`async/await` 在接口设计中的应用、Hook 模式 |

### 3. AgentRegistry 注册中心

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 全局 Agent 注册表，通过装饰器 `@registry.register` 自动注册所有 Agent 类型；支持按名称创建 Agent 实例 |
| **文件位置** | `backend/agents/registry.py` |
| **关键代码** | `@registry.register` 装饰器 → `registry.get("triage")` 获取类 → `registry.create("triage")` 创建实例 |
| **设计模式** | 注册表模式（Registry Pattern）、单例模式（模块级 `registry` 实例） |
| **新手学习重点** | 类装饰器、单例模式、工厂方法（`create`） |

### 4. HandoverManifest — Agent 通信协议

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | Agent 间传递的结构化消息格式，避免自由文本解析错误 |
| **文件位置** | `backend/app/schemas/agent.py` |
| **字段说明** | `facts`（已确认事实）、`pending_questions`（待问问题）、`risk_flags`（风险标记）、`evidence_level`（证据等级 A/B/C）、`context`（任意上下文） |
| **证据等级** | A = 指南推荐（Guideline）、B = 专家共识（Consensus）、C = LLM 生成（LLM-generated） |
| **新手学习重点** | Pydantic `BaseModel` 字段定义、结构化通信 vs 自由文本、版本兼容性 |

---

## 二、Agent 实现

### 5. TriageAgent — 导诊 Agent

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 分析患者症状，判断紧急程度和建议科室 |
| **文件位置** | `backend/agents/triage/agent.py` + `prompt.py` |
| **双模式运行** | LLM 模式（调用大模型智能分析）→ 解析失败时降级为关键词模式 |
| **关键词匹配** | 中英文双语关键词（`_guess_department()`）、三级紧急度（routine/urgent/emergency） |
| **输出** | `HandoverManifest` 包含分诊结果、待问问题、风险标记 |
| **注册方式** | `@registry.register` 装饰器在类定义时自动注册 |
| **新手学习重点** | 策略模式（LLM vs 关键词降级）、同步/异步双实现、中英文 NLP 基础 |

### 6. SupervisorAgent — 路由与会话管理

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 管理会话生命周期，根据当前 Agent 输出决定下一步路由 |
| **文件位置** | `backend/orchestration/supervisor.py` |
| **路由逻辑** | Triage → Doctor → Review → Followup → Complete；紧急情况 → Emergency Protocol |
| **SessionState** | `session_id`、`patient_id`、`current_agent`、`history`（对话历史）、`context`（共享上下文） |
| **关键方法** | `create_session()` 新建会话 → `run_agent()` 执行当前 Agent → `route()` 决定下一个 |
| **新手学习重点** | 状态机路由设计、会话管理、`SessionState` 数据类 |

### 7. 诊断流程状态机 (DiagnosisFlow)

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | Doctor Agent 内部的诊断流程控制（状态机骨架） |
| **文件位置** | `backend/agents/doctor/diagnosis_flow.py` |
| **状态** | INITIAL → HISTORY_TAKING → DIFFERENTIAL → TREATMENT → COMPLETED |
| **新手学习重点** | 状态模式（State Pattern）、流程控制抽象 |

---

## 三、流式通信

### 8. WebSocket (后端)

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 后端与前端之间的双向实时通信通道，用于流式传输 Agent 输出 |
| **FastAPI 用法** | `@app.websocket("/ws/{session_id}")` → `await websocket.accept()` → `websocket.receive_text()` / `send_text()` |
| **消息协议** | 客户端 → 服务端：`{"type": "message", "content": "..."}`；服务端 → 客户端：`{"event": "token", "data": {"token": "..."}}` |
| **事件类型** | `agent_start`、`token`、`agent_end`、`error`、`info` |
| **文件位置** | `backend/app/main.py`（WebSocket 端点）、`orchestration/stream.py`（事件管理） |
| **新手学习重点** | WebSocket 握手、文本帧、`asyncio` 异步读写、异常处理（断线重连） |
| **官方文档** | https://fastapi.tiangolo.com/advanced/websockets/ |

### 9. StreamManager — 事件流管理

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 封装 WebSocket 发送逻辑，提供类型化事件方法 |
| **文件位置** | `backend/orchestration/stream.py` |
| **主要方法** | `emit_agent_start(agent)` → `emit_token(token)` → `emit_agent_end(summary, manifest)` |
| **事件格式** | JSON 信封：`{"event": "token", "data": {"token": "..."}}` |
| **新手学习重点** | 生产者-消费者模式、事件驱动设计、JSON 序列化 |

### 10. WebSocket (浏览器端)

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 浏览器中建立 WebSocket 连接，接收服务端流式事件 |
| **文件位置** | `frontend/src/lib/websocket.ts` |
| **核心 API** | `new WebSocket(url)` → `ws.onmessage` → `ws.send()` → `ws.close()` |
| **增强功能** | 自动重连（指数退避）、事件监听器模式（`on()` / 取消订阅）、连接状态回调 |
| **关键类** | `ConsultationSocket` 封装了全部 WebSocket 逻辑 |
| **新手学习重点** | `WebSocket` 构造函数、`onopen/onmessage/onclose/onerror` 事件、重连策略 |
| **官方文档** | https://developer.mozilla.org/en-US/docs/Web/API/WebSocket |

---

## 四、前端组件

### 11. React 函数组件与 Hooks

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 构建 Chat 对话界面 |
| **文件位置** | `frontend/src/components/chat/`（ChatMessage、ChatInput、ChatContainer） |
| **关键 Hooks** | `useState`（消息列表/连接状态）、`useEffect`（WebSocket 事件绑定）、`useCallback`（发送函数缓存）、`useRef`（textarea 引用） |
| **流式渲染** | `setInterval` 每 30ms 追加 3 个字符；`setTimeout` 逐 token 追加 |
| **新手学习重点** | `useState` 状态管理、`useEffect` 副作用与清理、`useRef` DOM 引用、组件组合模式 |
| **官方文档** | https://react.dev/reference/react |

### 12. Tailwind CSS 样式

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 快速实现对话气泡、输入框、布局样式 |
| **关键类** | `flex justify-end/start`（消息对齐）、`rounded-2xl rounded-br-sm`（气泡圆角）、`animate-pulse`（闪烁光标）、`transition-colors`（悬停过渡） |
| **新手学习重点** | Flexbox 布局、`max-w-[75%]` 任意值、`animate-*` 动画、条件 className |
| **官方文档** | https://tailwindcss.com/docs |

---

## 五、测试

### 13. Pytest + pytest-asyncio

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 测试所有 Agent 和编排逻辑 |
| **文件位置** | `tests/integration/test_agent_communication.py`（Agent 通信测试）、`tests/integration/test_consultation_flow.py`（完整问诊流程测试） |
| **异步测试** | `asyncio_mode = "auto"` 自动检测 async 测试函数；或使用 `@pytest.mark.asyncio` 装饰器 |
| **测试模式** | 单元测试（验证单个类/方法）+ 集成测试（验证 Triage→Supervisor 完整流程） |
| **运行命令** | `make test` 或 `cd backend && python -m pytest tests/ -v` |
| **新手学习重点** | `assert` 断言、`@pytest.mark.asyncio`、测试夹具（fixture）、参数化测试 |
| **官方文档** | https://docs.pytest.org/ https://pytest-asyncio.readthedocs.io/ |

---

## 六、TypeScript

### 14. TypeScript 类型系统

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 前端代码类型安全，定义 WebSocket 事件类型和组件 Props |
| **文件位置** | `frontend/src/lib/websocket.ts`（`WsEventType`、`WsEvent`、`ConsultationSocket` 类） |
| **关键语法** | `type`（联合类型/对象类型）、`interface`（接口定义）、泛型（`Record<string, unknown>`）、可选链（`?.`） |
| **配置** | `tsconfig.json` 中 `paths: {"@/*": ["./src/*"]}` 实现路径别名 |
| **新手学习重点** | 基础类型、`type` vs `interface`、泛型函数、`tsconfig.json` 配置 |
| **官方文档** | https://www.typescriptlang.org/docs/ |

---

## 七、项目架构设计模式

### 15. 本周使用的设计模式

| 模式 | 使用位置 | 说明 |
|------|---------|------|
| **抽象基类 (Template Method)** | `BaseAgent.run()` | 定义算法骨架，子类实现具体逻辑 |
| **注册表 (Registry)** | `AgentRegistry` | 全局维护 Agent 类映射，支持按名称创建 |
| **单例 (Singleton)** | `registry` 模块级实例 | 整个进程共享同一个注册实例 |
| **策略 (Strategy)** | TriageAgent 双模式 | LLM 和关键词两种策略可切换 |
| **状态机 (State Machine)** | `SupervisorAgent.route()` | 依据当前状态决定下个 Agent |
| **观察者 (Observer)** | `ConsultationSocket.on()` | 事件监听/发布模式 |
| **生产者-消费者** | `StreamManager` + WebSocket | 后端生产事件，前端消费渲染 |
| **钩子 (Hook)** | `on_pre_process` / `on_post_process` | 生命周期拦截点，供 Plugin 注入 |

---

## 八、新手学习路线图（建议顺序）

如果你刚到第 2 周，建议按这个顺序学：

```
Step 1: WebSocket 基础 → 看 MDN 文档，理解双向通信
Step 2: FastAPI WebSocket → 官方示例，跑通 echo server
Step 3: LangGraph StateGraph 官方教程 (Quick Start)
Step 4: 读本项目 BaseAgent + AgentRegistry 源码
Step 5: 读本项目 TriageAgent 源码（理解双模式设计）
Step 6: 读本项目 SupervisorAgent 源码（理解路由逻辑）
Step 7: 读本项目 stream.py + main.py WebSocket 端点
Step 8: 读前端 ChatContainer 组件（理解前后端联动）
Step 9: Pytest + pytest-asyncio → 写一个简单的 async 测试
```

每个步骤花 **半天到 1 天**，按需深入，不必全覆盖。

---

## 九、关键命令速查

```bash
# 后端开发
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
cd backend && python -m pytest tests/ -v
cd backend && python -m pytest tests/integration/ -v

# 前端开发
cd frontend && npm run dev

# 测试指定文件
cd backend && python -m pytest tests/integration/test_consultation_flow.py -v -k "triage"

# 查看代码覆盖率（需要安装 pytest-cov）
cd backend && python -m pytest tests/ --cov=agents --cov=orchestration -v
```

---

## 十、快速参考：Agent 数据流

```
用户输入 "我头痛两天了"
       │
       ▼
WebSocket /ws/{session_id}
       │
       ▼
main.py: websocket_endpoint()
       │
       ▼
SupervisorAgent.run_agent(session, "我头痛两天了")
       │
       ├─ registry.get("triage") → TriageAgent
       ├─ agent.on_pre_process(context)    # 钩子: 身份验证等
       ├─ agent.run({"symptoms": "我头痛两天了"})
       │      ├─ _keyword_triage() → department="internal_medicine"
       │      └─ return HandoverManifest(facts=[...], context={...})
       ├─ agent.on_post_process(manifest)  # 钩子: 审计日志等
       ├─ session.history.append(user_msg + agent_response)
       └─ SupervisorAgent.route() → next = "doctor"
       │
       ▼
StreamManager
       │
       ├─ emit_agent_start("triage")
       ├─ emit_token("•") → emit_token("Patient symptoms:...")
       ├─ emit_token("•") → emit_token("Urgency: routine")
       └─ emit_agent_end(summary="...", manifest={...})
       │
       ▼
前端 ChatContainer 逐 token 渲染
```
