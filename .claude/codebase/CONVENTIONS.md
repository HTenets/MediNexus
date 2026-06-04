# MediNexus 代码约定 (Code Conventions)

> AI 修改代码时须遵守的约定。维护代码风格一致性。
> 决策基线: 患者自助问诊(A) | 参考级准确度 | Ollama 默认 + BYO Key | 中文为主英文备用 | 紧急演示级

---

## 1. 项目结构约定

### Agent 目录结构
```
backend/agents/<agent_name>/
├── __init__.py
├── agent.py       # Agent 类实现 (继承 BaseAgent)
└── prompt.py      # 系统提示词
```

- Doctor Agent 额外包含 `skills/` 子目录
- Review Agent 额外包含 `checkers/` + `rules/` 子目录

### API 路由
- 所有路由挂载在 `/api/v1` 下
- 路由文件在 `backend/app/api/` 中
- 在 `router.py` 中统一 include

---

## 1a. Ollama 优先原则 (LLM 策略)

```
默认模式   → Ollama (本地模型, 免费)
增强模式   → Claude/GPT-4o (用户 BYO Key)
降级模式   → 规则引擎/关键词匹配 (无 LLM)
```

### 每个 Agent 必须实现降级路径
```python
async def run(self, context: dict[str, Any]) -> HandoverManifest:
    llm = context.get("llm_client")
    if llm:
        return await self._llm_run(context)     # 正常 LLM 模式
    else:
        return self._rule_run(context)           # 降级模式
```

### 降级模式必须在输出中明确标注
```python
# 降级时, 在 facts 首行添加模式标注
facts.insert(0, "[模式: 规则引擎] 当前为离线降级模式, 建议配置 LLM Key 获得完整体验")
```

### Skill 提示词设计原则 (针对 Ollama/本地模型)
- 提示词结构明确: 用 `##` 分隔段落, 用 `###` 分隔子项
- 输出格式要求具体: 直接给出 JSON Schema 而非模糊描述
- 示例驱动: 在每个指令后附带 1-2 个少样本示例
- 避免依赖模型长上下文: 关键约束写在提示词开头

---

## 1b. 医疗免责声明 (Patient-Facing Content)

所有返回给患者用户的内容**必须附加免责声明**:

```python
MEDICAL_DISCLAIMER = (
    "⚠️ **医疗免责声明**\n\n"
    "本回答由 AI 生成, 仅供参考, 不构成医疗诊断建议。\n"
    "如有身体不适, 请及时前往正规医疗机构就诊。\n"
    "如遇紧急情况, 请立即拨打 120 急救电话。"
)
```

### 应用规则
- 每个 `HandoverManifest` 的 `facts` 末尾追加免责声明 (后端)
- 每个前端聊天消息末尾渲染免责区域 (前端)
- 紧急情况 (`EMERGENCY_DETECTED`): 免责声明替换为急救指引

---

## 1c. 紧急事件协议 (演示级)

紧急事件**不接入真实急救系统**, 仅在应用层面做演示:

```python
# 紧急检测 → 做两件事:
# 1. 后端日志记录
logger.warning("EMERGENCY_DETECTED: session=%s, details=%s", session_id, details)

# 2. WebSocket 发送 emergency 事件 (前端展示急救信息)
await stream.emit_emergency({
    "type": "emergency",
    "message": "检测到紧急情况信号",
    "actions": ["请立即拨打 120", "保持患者平躺", "勿随意移动患者"],
})
```

### WebSocket 事件协议扩展
```typescript
// 新增事件类型
{ event: "emergency", data: { type: string, message: string, actions: string[] } }
```

---

## 1d. BYO Key 原则 (Bring Your Own Key)

- 项目**不内置任何 API Key**
- 用户通过 `.env` 文件配置自己的 LLM Key
- 配置文档在 W8 产出, 但代码层已支持空 Key 降级

```bash
# .env 示例 (非必需)
MEDINEXUS_LLM_PROVIDER=ollama    # ollama | openai | anthropic
MEDINEXUS_OPENAI_KEY=sk-...      # 可选
MEDINEXUS_ANTHROPIC_KEY=sk-ant-... # 可选
MEDINEXUS_OLLAMA_BASE_URL=http://localhost:11434  # Ollama 默认
```

---

## 1e. 多源知识库约定 (W4)

### 三路置信度 (固定值)
```python
# backend/knowledge/source.py
CLINICAL_CASES_CONFIG.confidence_weight = 0.8  # 临床病例 — 高
MEDICAL_THEORY_CONFIG.confidence_weight  = 0.6  # 医学理论 — 中
LATEST_PAPERS_CONFIG.confidence_weight   = 0.3  # 最新论文 — 低
```

### 分块策略
| 源 | 策略 | 方法 | Chunk 大小 |
|----|------|------|-----------|
| 临床病例 | Semantic | `SemanticChunker` — 段落边界 | 384 tokens |
| 医学理论 | Hierarchical | `HierarchicalChunker` — 父子分层 | 768 parent / 192 child |
| 最新论文 | Recursive | `RecursiveChunker` — 分隔符优先级 | 512 tokens |

### BM25 降级
- Qdrant 不可用时自动降级到 BM25 全文搜索
- `backend/knowledge/bm25_fallback.py` 自实现 BM25Okapi
- 中文分词: bi-gram + 单字混合

### Review Agent 独立性
- Review Agent 使用独立的 `RAGQuery` 实例, 不共享 Doctor 的 RAG 结果
- 避免确认偏误: Review 从零开始检索验证

---

## 2. Python 代码约定

### 导入顺序 (3 段式)
```python
# 1. 标准库
import json
import logging
from typing import Any

# 2. 第三方库
from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

# 3. 项目内部
from agents.base import BaseAgent
from app.schemas.agent import HandoverManifest
```

### Agent 实现模板
```python
@registry.register  # ← 自动注册到全局 Registry
class MyAgent(BaseAgent):
    """Docstring: 描述职责, 中文优先, 英文备用."""
    
    def __init__(self):
        super().__init__("agent_name")  # ← name 应与目录名一致
    
    async def run(self, context: dict[str, Any]) -> HandoverManifest:
        # 1. 从 context 提取所需数据
        # 2. 调用 LLM 或规则引擎
        # 3. 构造 HandoverManifest 返回
        ...
```

### 通信协议
- **所有 Agent 间通信** 必须使用 `HandoverManifest`
- 禁止 Agent 之间直接传递自由文本
- `context` 字段用于传递非结构化补充数据

### 证据等级 (Evidence Level)
```python
"A"  # 指南推荐 (Guideline)
"B"  # 专家共识 (Consensus)
"C"  # LLM 生成 (LLM-generated) ← 大部分 Agent 输出标记为此
```

- Review Agent 可据此决定审查严格度
- 不允许不设置 `evidence_level`

### 错误处理
```python
logging.exception(...)  # 用 exception() 而非 error() 以捕获堆栈
# WebSocket 错误通过 stream.emit_error() 返回客户端
# REST 错误通过 HTTPException 返回
```

### 类型注解
- 所有函数参数和返回值必须有类型注解
- 优先用 `|` 语法而非 `Optional` (Python 3.10+): `str | None` 而非 `Optional[str]`

---

## 3. 前端约定

### TypeScript 风格
- 文件名: 小写 kebab-case (`chat-container.tsx`)
- 组件: PascalCase (`ChatContainer`)
- 使用 `'` 单引号而非 `"` 双引号

### 组件导出
```tsx
// 默认导出单个组件
export default function ChatContainer() { ... }
```

---

## 4. WebSocket 事件协议

**严格遵从此事件格式:**

```typescript
// 服务端 → 客户端
type ServerEvent = 
  | { event: "agent_start", data: { agent: string } }
  | { event: "token", data: { token: string } }
  | { event: "agent_end", data: { summary: string, manifest: object } }
  | { event: "error", data: { message: string, code: string } }
  | { event: "info", data: { message: string } }

// 客户端 → 服务端
type ClientEvent = { type: "message", content: string }
```

---

## 5. 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| Agent 类 | `XxxAgent` | `TriageAgent` |
| Agent 实例名 | kebab-case | `"triage"`, `"doctor"` |
| API router | `router = APIRouter()` | — |
| 会话状态 | class `SessionState` | — |
| Graph 状态 | class `GraphState(TypedDict)` | — |
| 测试文件 | `test_<module>.py` | `test_consultation_flow.py` |
| 数据库模型 | 单数 PascalCase | `Patient`, `Consultation` |
| 数据库表 | 复数 snake_case | `patients`, `consultations` |

---

## 6. Git 提交约定

```
<type>: <简短描述 (中文/英文均可)>

- type: feat, fix, refactor, docs, test, chore
- 描述: 中文优先 (如 "feat: 添加 TriageAgent 紧急度检测逻辑")
```

提交信息尾部附加 Co-authored-by:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

---

## 7. 开发工作流

```bash
# 修改前: 阅读相关模块的 MODULE_MAP 了解影响范围
# 修改后: make test 确保测试通过
# 创建新 Agent: 按 Agent 目录模板, 注册 @registry.register
# 创建新 API: 在 app/api/ 下新建文件, 在 router.py 中 include
```
