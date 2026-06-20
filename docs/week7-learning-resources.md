---
name: week7-learning-resources
description: W7 技术栈学习文档——安全护栏、多科室会诊、审计日志
metadata:
  type: reference
---

# MediNexus W7 技术栈学习指南

> 本文档列出了第 7 周 Guardrail（安全护栏）+ Coordinator Agent（多科室会诊）中用到的所有技术，适合新手按顺序学习。

---

## 一、Guardrail 安全护栏系统

### 1. 架构概览

```
用户输入
    │
    ├──→ EmergencyDetector (关键词 + 正则 + 可选LLM)
    ├──→ PIISanitizer (正则替换 / 掩码)
    │
    ▼
SupervisorAgent
    │
    ├──→ IdentityVerifier (患者ID匹配 + JWT验证)
    │
    ▼
Agent Pipeline (Triage → Doctor → Review → Followup)
```

**文件位置:** `backend/guardrails/`

### 2. EmergencyDetector — 紧急信号检测

| 项目 | 内容 |
|------|------|
| **文件位置** | `backend/guardrails/emergency_detector.py` |
| **检测方式** | 三层次: 关键词(快速) → 正则(语义) → LLM(模糊,可选) |
| **关键词数量** | 50+ 中英文关键词 (suicide/自杀/chest pain/胸痛/呼吸困难/大出血/中风等) |
| **正则模式** | 7 条语义正则（`"想"+"自杀"`, `"胸"+"痛"+"出汗"`, `"呼吸"+"困难"+"过敏"`） |
| **紧急分类** | SUICIDE / CARDIAC / RESPIRATORY / NEUROLOGICAL / HEMORRHAGE |
| **响应输出** | 按分类分发急救指引 + 热线号码 |

**demo 限制:** 不接入真实急救系统，仅在应用层做日志和前端展示。

### 3. PIISanitizer — PII 脱敏 (PII：Personally Identifiable Information)

| 项目 | 内容 |
|------|------|
| **检测方式** | 正则表达式（lookbehind/lookahead 适配中文环境） |
| **支持类型** | 手机号(13-19开头11位)、身份证号(18位含校验位)、邮箱、座机 |
| **三种模式** | `sanitize_text()` — 替换为 `[手机号]`；`mask_pii()` — 部分掩码 `138****5678`；`detect_pii()` — 返回定位列表 |
| **中文兼容** | 使用 `(?<!\d)` 替代 `\b` 边界符，兼容中文字符紧邻数字的情况 |

**关键代码:**
```python
# 使用 lookbehind/lookahead 而非 \b，避免中文边界问题
PII_PATTERNS = [
    (re.compile(r'(?<!\d)1[3-9]\d-?\d{4}-?\d{4}(?!\d)'), "[手机号]"),
    (re.compile(r'(?<!\d)[1-9]\d{5}...\d{3}[\dXx](?!\d)'), "[身份证号]"),
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'), "[邮箱]"),
]
```

### 4. IdentityVerifier — 身份验证

| 项目 | 内容 |
|------|------|
| **作用** | 确保当前会话有权访问患者的敏感数据 |
| **基本校验** | `verify(patient_id, session_patient_id)` — ID匹配检查 |
| **JWT** | 支持注入 Token 验证函数（demo 模式跳过） |
| **审计** | `audit_access()` — 记录谁在什么时候访问了哪些数据 |

---

## 二、Coordinator Agent 多科室会诊

### 5. 会诊流程

```
CoordinatorAgent.run(context)
    │
    ├── 1. 分析病情复杂程度 (COMPLEXITY_TRIGGERS)
    │       ├── 多系统症状 → 多科室会诊
    │       ├── 皮肤+发热 → 皮肤科+内科
    │       ├── 心理+躯体 → 心理科+内科
    │       └── 单一症状 → 不需要会诊
    │
    ├── 2. 邀请专科医生 (调用 Skill 生成意见)
    │       └── SpecialistOpinion { specialty, diagnosis[], confidence }
    │
    └── 3. 综合会诊报告
            ├── 各专科意见汇总
            ├── 共识诊断
            └── 分歧记录
```

### 6. ConsultationProtocol 数据结构

```python
@dataclass
class SpecialistOpinion:
    specialty: str                  # 科室名称
    agent_instance: str = "doctor"  # 提供意见的 Agent
    diagnosis: list[str]            # 诊断列表
    recommendations: list[str]      # 建议
    confidence: float = 0.5         # 置信度 0.0-1.0
    evidence_level: str = "C"

@dataclass
class ConsultationReport:
    session_id: str
    chief_complaint: str
    specialties_involved: list[str]
    opinions: list[SpecialistOpinion]
    consensus_diagnosis: str
    disagreements: list[str]
```

### 7. 6 种复杂性触发器

| 触发器 | 关键词 | 会诊科室 |
|--------|--------|---------|
| multi_system | multiple, 多处, 全身, 复杂 | internal_medicine |
| cardio_respiratory | chest pain, 胸痛, breathing, 呼吸 | internal_medicine |
| skin_systemic | rash, 皮疹, fever, 发热, joint, 关节 | dermatology + internal_medicine |
| mental_physical | anxiety, 焦虑, insomnia, 失眠 | mental_health + internal_medicine |
| ent_systemic | vertigo, 眩晕, tinnitus, 耳鸣 | ent + internal_medicine |

---

## 三、Middleware 中间件

### 8. LoggingMiddleware — 请求审计日志

| 项目 | 内容 |
|------|------|
| **文件位置** | `backend/app/middlewares/logging.py` |
| **记录内容** | HTTP方法 + 路径 + 状态码 + 耗时(ms) |
| **日志等级** | `medinexus.audit` Logger |
| **示例** | `GET /api/v1/health → 200 (12.3ms)` |

### 9. AuthMiddleware — 认证中间件

| 项目 | 内容 |
|------|------|
| **文件位置** | `backend/app/middlewares/auth.py` |
| **Demo 模式** | 所有请求放行（JWT 可选） |
| **公开路径** | `/health`, `/api/v1/health`, `/docs`, `/openapi.json`, `/ws/*` |
| **生产模式** | 取消注释后启用 JWT 验证 |

---

## 四、审计日志模型

### 10. AuditLog

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True)
    action = Column(String, nullable=False)    # 操作类型
    details = Column(JSON, nullable=True)       # 操作详情
    created_at = Column(DateTime(timezone=True)) # 时间戳
```

**触发时机:** 每次 Agent 处理患者数据前由 `IdentityVerifier.audit_access()` 记录。

---

## 五、设计模式总结

| 模式 | 使用位置 | 说明 |
|------|---------|------|
| **三阶段检测** | EmergencyDetector | 关键词→正则→LLM，逐级递进 |
| **策略模式** | get_emergency_response() | 按紧急类型分发不同急救响应 |
| **装饰器模式** | middleware | 请求前后注入日志/认证逻辑 |
| **责任链** | CoordinatorAgent._analyze_complexity() | 6 种触发器逐级匹配 |

---

## 六、测试架构

| 测试文件 | 测试数 | 覆盖范围 |
|---------|--------|---------|
| `test_guardrails.py` | 22 | EmergencyDetector(15) + PIISanitizer(9) + IdentityVerifier(3) |
| `test_coordinator.py` | 13 | 会诊触发(5) + 复杂性分析(3) + 协议(3) + 集成(2) |

**运行:**
```bash
cd backend && python -m pytest tests/unit/guardrails/ tests/unit/agents/test_coordinator.py -v
```
