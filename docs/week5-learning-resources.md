---
name: week5-learning-resources
description: W5 技术栈学习文档——三层记忆系统、SOAP 病历、Session→Redis 迁移、Follow-up Agent
metadata:
  type: reference
---

# MediNexus W5 技术栈学习指南

> 本文档列出了第 5 周记忆系统 + SOAP 病历 + Follow-up Agent 中用到的所有技术，适合新手按顺序学习。

---

## 一、三层记忆系统架构

### 整体设计

```
┌─────────────────────────────────────────────────┐
│              MemoryManager                        │
│    统一接口: retrieve(patient_id) → LLM context   │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ WorkingMemory │  │EpisodicMem │  │SemanticMem│ │
│  │   (Redis)    │  │ (PostgreSQL)│  │(PostgreSQL)│ │
│  │              │  │            │  │           │ │
│  │ current_agent│  │ consultation│  │ patient   │ │
│  │ context dict │  │  history   │  │  profile  │ │
│  │ TTL 3600s    │  │  SOAP fields│  │ allergies │ │
│  └──────┬───────┘  └─────┬──────┘  └─────┬─────┘ │
│         │                │               │        │
│         ▼                ▼               ▼        │
│         Redis        PostgreSQL         PostgreSQL│
└─────────────────────────────────────────────────┘
```

| 记忆层 | 存储 | 数据 | 生命周期 | 用途 |
|--------|------|------|---------|------|
| **Working** | Redis | `current_agent` + `context` | 会话期 (TTL 1h) | 断线重连、路由决策 |
| **Episodic** | PostgreSQL | 历史就诊记录 (SOAP) | 永久 | 复诊加载历史 |
| **Semantic** | PostgreSQL | 患者档案 (过敏/既往史/家族史) | 永久 | 诊断参考 |

**文件位置:** `backend/memory/manager.py`（统一入口）

---

## 二、Working Memory (Redis)

### 1. 设计原理

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 替代 SupervisorAgent 中原来 `_sessions: dict` 的内存存储 |
| **文件位置** | `backend/memory/working.py` |
| **技术** | Redis (`aioredis`) |
| **TTL** | 3600 秒 (1 小时)，会话通常在这个时间内完成 |
| **Key 设计** | `session:<id>:agent` 和 `session:<id>:context` |

### 2. 迁移了什么

| 字段 | 原来 (内存 dict) | 现在 (Redis) |
|------|-----------------|-------------|
| `current_agent` | `SessionState.current_agent` | `session:<id>:agent` |
| `context` | `SessionState.context` | `session:<id>:context` (JSON 序列化) |
| `history` | `SessionState.history` | 仍在内存中 (太大, 不适合 Redis TTL) |

### 3. 关键代码

```python
from redis import asyncio as aioredis

async def set_current_agent(self, session_id: str, agent_name: str) -> bool:
    key = f"session:{session_id}:agent"
    await redis_client.set(key, agent_name, ex=SESSION_TTL)

async def get_context(self, session_id: str) -> dict:
    key = f"session:{session_id}:context"
    val = await redis_client.get(key)
    return json.loads(val) if val else {}
```

> **注意:** Redis 5.x+ 中 `setex()` 已弃用，使用 `set(key, value, ex=ttl)` 替代。

### 4. 为什么不分 history 也迁过去

对话历史可能很长（数百轮），Redis 的 TTL 机制不适合存储大量数据。history 的持久化由 PostgreSQL 的 `Consultation` 表负责。

---

## 三、Episodic Memory (PostgreSQL)

### 5. SOAP 病历格式

**S**ubjective（主观）— 患者主诉、症状描述
**O**bjective（客观）— 查体、检查结果
**A**ssessment（评估）— 诊断、鉴别诊断
**P**lan（计划）— 治疗方案、随访计划

```sql
-- Consultation 表的 SOAP 字段
subjective  TEXT  -- 主诉："发热咳嗽3天"
objective   TEXT  -- 查体："咽部充血，双肺呼吸音清"
assessment  TEXT  -- 诊断："急性上呼吸道感染"
plan        TEXT  -- 方案："退热药 + 多饮水，休息3天"
```

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 存储历史就诊记录，支持复诊时加载 |
| **文件位置** | `backend/memory/stores/episodic.py` |
| **技术** | SQLAlchemy 2.0 async + PostgreSQL |
| **关键方法** | `recall(patient_id)` → 最近 N 次就诊; `store(SOAP)` → 保存; `format_history()` → LLM 文本 |

### 6. 数据库降级策略

所有数据库操作在 `try/except` 中优雅降级:

```python
async def recall(self, patient_id: str) -> list[dict]:
    try:
        async with DbSession() as session:
            result = await session.execute(...)
            return result.scalars().all()
    except Exception as e:
        logger.error("DB failed: %s", e)
        return []  # ← 优雅降级: 返回空列表而非崩溃
```

---

## 四、Semantic Memory (PostgreSQL)

### 7. 患者画像

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 管理患者稳定的档案信息 |
| **文件位置** | `backend/memory/stores/semantic.py` |
| **数据分类** | `allergy`(过敏史), `past_illness`(既往史), `family`(家族史), `medication`(长期用药) |
| **表结构** | `patients`(基本信息) + `medical_histories`(JSONB 历史条目) |

**MedicalHistory 的 content 字段示例:**
```json
{"name": "青霉素过敏", "reaction": "皮疹", "severity": "中"}
{"name": "2型糖尿病", "diagnosed_date": "2023-05", "status": "控制中"}
{"name": "阿司匹林", "dosage": "100mg qd", "purpose": "冠心病二级预防"}
```

---

## 五、MemoryManager 协调层

### 8. 统一检索接口

```python
class MemoryManager:
    async def retrieve(self, patient_id: str, query: str = "") -> str:
        """
        检索所有三层记忆，合并为 LLM 可读文本。
        输出示例:
        
        ## 患者档案
        **姓名:** 张三
        **过敏史:** 青霉素过敏
        
        ## 患者历史就诊记录
        ### 就诊 #1 (2026-05-28)
        **主诉:** 发热咳嗽3天
        **诊断:** 上呼吸道感染
        """
        parts = []
        profile = await self.semantic.format_profile(patient_id)
        if profile: parts.append(profile)
        history = await self.episodic.format_history(patient_id, limit=3)
        if history: parts.append(history)
        return "\n\n".join(parts)
```

### 9. 在 SupervisorAgent 中的注入点

```python
# orchestration/supervisor.py
context = {
    **session.context,
    "symptoms": user_input,
    "patient_id": session.patient_id,
    "messages": session.history[-10:],
    "llm_client": llm_client,
}

# 注入患者记忆
if session.patient_id:
    patient_memory = await memory_manager.retrieve(session.patient_id, query=user_input)
    if patient_memory:
        context["patient_memory"] = patient_memory
```

每个 Agent 通过 `context.get("patient_memory", "")` 读取历史信息。

---

## 六、延迟导入模式 (Lazy Import)

### 10. 为什么要用

Python 的模块级导入会在 import 时立即执行。对于依赖 PostgreSQL/Redis 的模块，即使测试不需要数据库，导入也会失败:

```python
# ❌ 模块级导入 — 导入时立刻连数据库
from app.core.database import AsyncSession   # 如果没有 asyncpg → ImportError

# ✅ 方法内延迟导入 — 仅在该方法被调用时才尝试导入
async def recall(self, patient_id):
    from app.core.database import AsyncSession  # 调用时才导入
```

| 应用于 | 文件 | 原因 |
|--------|------|------|
| `episodic.py` | 所有 DB 操作 | 测试不需要 DB |
| `semantic.py` | 所有 DB 操作 | 测试不需要 DB |
| `knowledge/` (W4) | 类似 | 测试不需要 Qdrant |

---

## 七、SupervisorAgent 重构

### 11. 变更总结

```
W4 之前                        W5
─────────                      ─────────
_sessions: dict[str, SessionState]  →  _sessions 只存 metadata + history
  session.current_agent  (内存)     →  Redis (memory_manager.set_current_agent)
  session.context (内存)            →  Redis (memory_manager.set_context)
  get_session() 同步                →  async, fallback to Redis
  run_agent() 不注入记忆            →  自动注入 patient_memory
```

### 12. 断线重连流程

```
用户重连 /ws/{session_id}
       │
       ▼
supervisor.get_session(session_id)
       │
       ├─ _sessions 中有? → 直接返回
       │
       └─ _sessions 中没有?
              │
              ▼
          memory_manager.session_exists() → Redis 检查
              │
              ├─ Redis 有? → 从 Redis 恢复 current_agent + context
              │              → 重建 SessionState → 返回
              │
              └─ Redis 也没有? → session not found
```

---

## 八、Follow-up Agent

### 13. 随访计划生成

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 基于诊断结论生成随访计划、用药提醒、警示信号 |
| **文件位置** | `backend/agents/followup/agent.py` |
| **输入** | `context["diagnosis"]` (来自 DoctorAgent 的诊断结果) |
| **输出** | `HandoverManifest` 包含: 复诊安排、用药提醒、警示信号、追问 |

### 14. 随访排程器

| 项目 | 内容 |
|------|------|
| **文件位置** | `backend/agents/followup/scheduler.py` |
| **5 种计划模板** | `chronic_disease`(30天), `post_surgery`(7天), `medication_monitoring`(14天), `mental_health`(14天), `routine`(7天) |
| **诊断→计划映射** | `get_plan_for_diagnosis("高血压")` → `"chronic_disease"` |
| **优先级规则** | 心理健康 > 术后 > 用药监测 > 慢性病 > 常规 |

**排程生成:**
```python
def generate_schedule(patient_id, consultation_id, plan_type) -> list[ScheduledFollowup]:
    """为指定计划模板生成一系列复诊日期。"""
    plan = DEFAULT_PLANS[plan_type]
    now = datetime.now(timezone.utc)
    schedule = []
    for i in range(plan.total_visits):
        due = now + timedelta(days=plan.interval_days * (i + 1))
        schedule.append(ScheduledFollowup(
            patient_id=patient_id, due_date=due,
            visit_number=i + 1, total_visits=plan.total_visits,
        ))
    return schedule
```

**诊断匹配优先级 (避免误判):**
```python
# ❌ W4 的问题: "抑郁症" 先匹配了 "chronic_disease"
#    因为 chronic_keywords 包含了 "抑郁症"
# ✅ W5 修复: 心理关键词优先匹配
mental_keywords > post_op_keywords > medication_keywords > chronic_keywords
```

---

## 九、API 扩展

### 15. 新增端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/consult/{id}/complete` | POST | 完成问诊，提交 SOAP 数据，存入记忆 |
| `/api/v1/consult/{id}/history` | GET | 获取患者历史就诊记录 |

**SOAP 请求体:**
```json
{
  "subjective": "发热咳嗽3天",
  "objective": "咽部充血，体温38.2°C",
  "assessment": "急性上呼吸道感染",
  "plan": "对乙酰氨基酚退热，多饮水休息",
  "diagnosis": "感冒"
}
```

---

## 十、设计模式总结

| 模式 | 使用位置 | 说明 |
|------|---------|------|
| **外观模式 (Facade)** | `MemoryManager` | 统一三层记忆的调用接口 |
| **延迟初始化 (Lazy Init)** | `episodic.py`, `semantic.py` | DB 连接在用到时才建立 |
| **降级模式 (Graceful Degradation)** | 所有记忆操作 | DB/Redis 不可用时返回默认值而非崩溃 |
| **数据类 (Data Class)** | `FollowupPlan`, `ScheduledFollowup` | 纯数据容器，带业务逻辑方法 |
| **分层架构 (Layered Architecture)** | Working → Episodic → Semantic | 不同时效性的数据存储在不同层 |
| **策略模式 (Strategy)** | `get_plan_for_diagnosis()` | 不同诊断类型映射到不同随访计划 |

---

## 十一、关键命令速查

```bash
# 运行 Agent 相关测试 (不含记忆/DB 依赖)
cd backend && python -m pytest tests/unit/agents/ -v

# 运行 Follow-up Agent 测试
cd backend && python -m pytest tests/unit/agents/test_followup_agent.py -v

# 运行记忆系统测试 (需要 Redis + PostgreSQL 运行)
cd backend && python -m pytest tests/unit/memory/ -v

# 运行全部测试
cd backend && python -m pytest tests/ -v

# 验证记忆系统导入
cd backend && python -c "from memory import MemoryManager; print('OK')"

# 验证 SupervisorAgent 使用 Redis 会话
cd backend && python -c "from orchestration.supervisor import memory_manager; print(type(memory_manager).__name__)"
```

---

## 十二、常见问题

### Q: 三层记忆和 SessionState 有什么区别？

**A:** 三个维度不同:
- **Working** (Redis) = 当前会话的"进行到哪里了"（临时）
- **Episodic** (PostgreSQL) = "以前看过什么病"（历史）
- **Semantic** (PostgreSQL) = "这个患者有什么特征"（画像）
- **SessionState** = 当前对话的上下文（内存中，运行时）

### Q: 为什么 get_session 变成 async 了？

**A:** 因为 `current_agent` 和 `context` 现在存在 Redis 中，读取需要异步网络 IO。这是为了断线重连的能力付出的代价。

### Q: SOAP 病历和 HandoverManifest 是什么关系？

**A:** `HandoverManifest` 是 Agent 间通信的"快递单"，而 SOAP 是存数据库的"病历格式"。DoctorAgent 输出 `HandoverManifest` → 从中提取 SOAP 字段 → 调用 `complete` API 存入 PostgreSQL。

### Q: 没有 PostgreSQL 时记忆系统能工作吗？

**A:** 可以。所有 DB 操作都有 try/except 兜底: 没有 DB 时 `recall()` 返回空列表，`store()` 返回 False，系统不会崩溃。
