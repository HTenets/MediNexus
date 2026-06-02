---
name: week3-learning-resources
description: W3 技术栈学习文档——Skill 系统、Doctor Agent、Ollama 兼容策略、降级模式
metadata:
  type: reference
---

# MediNexus W3 技术栈学习指南

> 本文档列出了第 3 周 Skill 系统 + Doctor Agent 中用到的所有技术，适合新手按顺序学习。

---

## 一、Skill 系统架构

### 1. BaseSkill — 科室技能抽象基类

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 每个医疗科室封装为一个独立的 Skill，提供标准化的诊断知识接口 |
| **文件位置** | `backend/agents/doctor/skills/base.py` |
| **核心方法** | `get_knowledge(context)` — 基于症状返回相关科室知识；`get_tools()` — 返回工具定义（可选）；`match_symptoms(symptoms)` — 症状匹配置信度 [0.0, 1.0] |
| **设计思想** | 策略模式：将不同科室的诊断逻辑隔离到独立类中，Doctor Agent 通过接口调用，不依赖具体实现 |
| **新手学习重点** | 抽象基类（ABC）、策略模式、接口隔离原则 |

**关键代码:**
```python
class BaseSkill(ABC):
    name: str = ""
    system_prompt: str = ""

    @abstractmethod
    async def get_knowledge(self, context: dict[str, Any]) -> str:
        """Return specialty knowledge relevant to symptoms/history."""
        ...

    async def get_tools(self) -> list[dict]:
        return []  # Optional: tool definitions

    async def match_symptoms(self, symptoms: str) -> float:
        return 0.0  # Optional: override for auto-routing confidence
```

### 2. SkillRegistry — 技能注册与自动路由

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 管理所有 Skill 实例，根据分诊科室或症状描述自动匹配最佳 Skill |
| **文件位置** | `backend/agents/doctor/skills/registry.py` |
| **三级路由策略** | ① 精确科室匹配（TriageAgent 的 `department` 输出）→ ② `match_symptoms()` 置信度评分（阈值 0.3）→ ③ 返回第一个注册 Skill 作为降级 |
| **核心方法** | `register(skill)` / `get(name)` / `list_skills()` / `auto_route(symptoms, department)` |
| **设计模式** | 注册表模式（Registry Pattern）+ 单例模式（模块级 `registry` 实例） |
| **新手学习重点** | 多级路由设计、置信度阈值选择、注册表与工厂模式的区别 |

**关键代码 — auto_route 路由逻辑:**
```python
async def auto_route(self, symptoms: str, department: str = "") -> BaseSkill | None:
    # 1. 精确科室匹配
    if department and department in self._skills:
        return self._skills[department]

    # 2. 症状置信度评分
    if symptoms:
        best_score = 0.0
        best_skill = None
        for skill in self._skills.values():
            score = await skill.match_symptoms(symptoms)
            if score > best_score:
                best_score = score
                best_skill = skill
        if best_score > 0.3:  # confidence threshold
            return best_skill

    # 3. 首注册降级
    if self._skills:
        return next(iter(self._skills.values()))
    return None
```

### 3. Skill Loader — 内置 Skill 加载

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 发现并注册所有内置 Skill |
| **文件位置** | `backend/agents/doctor/skills/loader.py` |
| **加载方式** | `load_builtin_skills()` 导入 4 个 Skill 类 → 实例化 → 注册到全局 `registry` |
| **扩展预留** | 外部目录扫描接口已定义，具体实现延迟到 v0.3.0+（社区 Skill） |
| **新手学习重点** | 延迟加载（lazy loading）、插件发现机制 |

---

## 二、内置 Skill 详解

### 4. 内科 Skill (InternalMedicineSkill)

| 项目 | 内容 |
|------|------|
| **文件** | `builtin/internal_medicine/skill.py` |
| **系统提示词** | 约 300 行中文，覆盖内科完整诊断流程 + JSON 输出格式 |
| **知识覆盖** | 呼吸系统（感冒/流感/支气管炎/肺炎）、消化系统（胃肠炎/溃疡/胃食管反流）、心血管（高血压/冠心病/心衰）、内分泌（糖尿病/甲亢/甲减） |
| **知识检索** | `get_knowledge()` 通过关键词匹配症状，返回对应系统知识 |
| **症状匹配** | 高置信度词(`fever`/`cough`/`stomach`/`糖尿病`等)→0.9；中等词(`chest pain`/`dizziness`)→0.6 |
| **Ollama 优化** | 提示词用 `##` 分段、JSON Schema 完整写出、关键约束在开头重复 |

### 5. 皮肤科 Skill (DermatologySkill)

| 项目 | 内容 |
|------|------|
| **文件** | `builtin/dermatology/skill.py` |
| **系统提示词** | 含皮肤科 5 步诊断流程（皮损描述→伴随症状→病史→鉴别→治疗） |
| **知识覆盖** | 荨麻疹、痤疮（分级治疗）、湿疹/特应性皮炎、真菌感染（体癣/足癣） |
| **症状匹配** | 关键词命中率匹配 (`rash`/`itch`/`acne`/`eczema` 等)，`score = min(命中率 × 3, 0.95)` |

### 6. 耳鼻喉科 Skill (ENTSkill)

| 项目 | 内容 |
|------|------|
| **文件** | `builtin/ent/skill.py` |
| **知识覆盖** | 耳部（中耳炎/分泌性中耳炎/突发性耳聋/梅尼埃病/BPPV）、鼻部（过敏性鼻炎/鼻窦炎/鼻出血）、咽喉（咽炎/扁桃体炎/喉炎/声带结节/咽喉反流） |
| **警示信号** | 突发性听力下降（72h 急诊）、单侧鼻塞+血涕、声嘶>3 周、吞咽剧痛+张口受限 |

### 7. 心理科 Skill (MentalHealthSkill)

| 项目 | 内容 |
|------|------|
| **文件** | `builtin/mental_health/skill.py` |
| **特色工具** | `calculate_phq9(responses)` — 9 题抑郁筛查；`calculate_gad7(responses)` — 7 题焦虑筛查；含严重度分级 |
| **PHQ-9 分级** | 0-4 无/轻微 → 5-9 轻度 → 10-14 中度 → 15-19 中重度 → 20-27 重度 |
| **GAD-7 分级** | 0-4 无/轻微 → 5-9 轻度 → 10-14 中度 → 15-21 重度 |
| **自杀检测** | `match_symptoms("suicidal")` 返回 **0.95**（最高优先级），触发 crisis response（热线号码替换 facts） |
| **覆盖范围** | 抑郁障碍、焦虑障碍、睡眠障碍、压力/职业倦怠 |
| **治疗建议** | SSRI 药物（舍曲林/艾司西酞普兰）+ CBT 心理治疗，含 Level A/B/C 证据等级 |

---

## 三、Doctor Agent

### 8. DoctorAgent — 双模式诊断 Agent

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 接收 TriageAgent 的分诊结果，自动加载匹配的 Skill，进行诊断推理 |
| **文件位置** | `backend/agents/doctor/agent.py` |
| **双模式** | LLM 模式（注入 Skill 提示词 + 知识 → 调用 LLM → 解析 JSON）↔ 规则引擎模式（关键词 → 结构化建议） |
| **Skill 集成** | `skill_registry.auto_route(symptoms, department)` → 匹配 Skill → system_prompt + knowledge 注入 LLM |
| **注册方式** | `@agent_registry.register` 装饰器 + `agents/__init__.py` 导入触发 |

**LLM 模式数据流:**
```
context = {symptoms, department, patient_history, llm_client, ...}
  │
  ▼
skill = skill_registry.auto_route(symptoms, department)
  │
  ▼
system_prompt = skill.system_prompt + "\n\n" + skill.get_knowledge(context)
  │
  ▼
llm_response = await llm.chat([{role: "system", content: system_prompt},
                                {role: "user", content: user_msg}])
  │
  ▼
_parse_diagnosis_response(llm_response)  →  dict
  │  支持三种输入:
  │  ① 纯 JSON → json.loads()
  │  ② Markdown ```json ``` 代码块 → re.search() 提取
  │  ③ 非结构化文本 → 返回空 dict, 降级到规则引擎
  │
  ▼
_build_facts(parsed, symptoms, skill) →  Human-readable facts list
  │
  ▼
HandoverManifest(facts, pending_questions, risk_flags, evidence_level="C")
```

**规则引擎降级模式:**
```
无 LLM 时:
  facts[0] = "[模式: 规则引擎] 当前为离线降级模式, 建议配置 LLM Key 获得完整体验"
  
  按 skill.name 分发到对应方法:
    _add_internal_medicine_facts() → 感冒/胃肠炎/头痛 各有建议
    _add_dermatology_facts()       → 瘙痒/痤疮 各有建议
    _add_ent_facts()               → 咽痛/耳部/鼻部 各有建议
    _add_mental_health_facts()     → 焦虑/抑郁/失眠 + 自杀危机替换
    _add_general_facts() + _add_symptom_specific_facts() → 兜底
  
  所有建议标注: "证据等级: C (LLM 经验性建议)"
```

### 9. 诊断提示词设计 (Ollama 优化)

| 项目 | 内容 |
|------|------|
| **文件位置** | `backend/agents/doctor/prompt.py` |
| **设计原则** | 明确的分段结构（`##` 标题）、完整的 JSON Schema 输出规格、1-2 个少样本示例、关键约束在提示词开头重复 |
| **证据等级要求** | 所有药物标注 `evidence_level`，默认为 `"C"`（LLM 经验性建议） |
| **红色警戒** | 胸痛+出汗（心梗）、呼吸困难+发绀、高热>39.5°C 超 3 天、意识改变、呕血/黑便 → red_flags 输出 |
| **输出格式** | 严格 JSON，包含 `possible_diagnoses[]`、`treatment_plan`、`red_flags[]`、`pending_questions[]` |

---

## 四、Agent 自动注册机制

### 10. @registry.register 装饰器

| 项目 | 内容 |
|------|------|
| **在项目中的作用** | 所有 Agent 通过装饰器自动注册到全局 `AgentRegistry`，无需手动维护注册表 |
| **触发时机** | `agents/__init__.py` 导入子模块时，类定义上的装饰器立即执行 |
| **注册验证** | `python -c "from agents import registry; print(registry.list_agents())"` → 输出 `['triage', 'doctor', 'review', 'coordinator', 'followup']` |
| **新手学习重点** | 类装饰器（class decorator）、导入时执行 vs 运行时执行、`__init__.py` 的模块初始化作用 |

**关键代码:**
```python
# 在 Agent 类定义上:
@registry.register
class DoctorAgent(BaseAgent):
    def __init__(self):
        super().__init__("doctor")  # 注册名 = "doctor"

# 在 agents/__init__.py 中统一导入触发:
from agents.doctor.agent import DoctorAgent  # 触发 @registry.register
from agents.triage.agent import TriageAgent  # 同上
```

---

## 五、设计模式总结

### 11. W3 新增的设计模式

| 模式 | 使用位置 | 说明 |
|------|---------|------|
| **策略模式 (Strategy)** | Skill 系统 | 每个 Skill 封装一套诊断策略，通过统一接口调用 |
| **工厂方法 (Factory)** | `SkillRegistry.auto_route()` | 根据条件选择合适的 Skill 实例 |
| **适配器模式 (Adapter)** | `_parse_diagnosis_response()` | 将 LLM 自由文本适配为结构化 JSON |
| **模板方法 (Template Method)** | DoctorAgent 双模式 | `run()` 定义骨架，`_llm_diagnose()` / `_rule_diagnose()` 实现具体步骤 |
| **延迟初始化 (Lazy Initialization)** | `_ensure_skills()` | 首次诊断时才加载所有 Skill |
| **责任链 (Chain of Responsibility)** | `auto_route()` 三级路由 | ①科室 → ②症状评分 → ③首注册降级，逐级尝试 |
| **标记接口 (Marker Interface)** | 降级模式标注 | `facts[0]` 的 `[模式: 规则引擎]` 前缀作为降级标记 |

---

## 六、Ollama 兼容策略

### 12. 提示词设计原则

由于 Ollama 运行的本地模型（如 Llama 3、Qwen）能力弱于 Claude/GPT，以下策略确保稳定输出:

| 策略 | 实现方式 | 示例 |
|------|---------|------|
| **结构明确** | 用 `##` 分段，每段聚焦一个主题 | `## 诊断流程` → `### 第一步: 主诉分析` |
| **JSON Schema 完整** | 在提示词中写出完整的 JSON 输出格式 | `{"possible_diagnoses": [{"diagnosis": "...", "likelihood": "高/中/低"}]}` |
| **少样本示例** | 每个指令后附 1-2 个示例 | 明确写出输入→输出的对应关系 |
| **关键约束前置** | 最重要的规则写在提示词开头 | "所有输出必须使用中文" |
| **避免复杂推理链** | 不依赖模型的多步推理 | 明确写出每一步的输入和期望输出 |
| **容错解析** | 三层解析：纯 JSON → Markdown 代码块 → 非结构化文本 | `_parse_diagnosis_response()` |

### 13. 降级策略

```
                   LLM 可用?
                  /         \
               是            否
               │              │
         调用 LLM          facts 插入降级标注
         解析 JSON        └── "[模式: 规则引擎]..."
         │                    │
      成功?              按科室分发规则引擎
      /    \               └── 感冒→多喝热水...
    是      否               │
    │       └── 降级到    所有建议标注
  输出      规则引擎       "证据等级: C"
```

---

## 七、测试架构

### 14. Skill 系统测试 (19 用例)

| 测试文件 | `tests/unit/agents/test_skill_system.py` |
|---------|----------------------------------------|
| **TestBaseSkill** | 注册要求 name 非空、get_tools() 默认返回空列表、match_symptoms() 默认返回 0.0 |
| **TestSkillRegistry** | 注册/查找/列表、精确科室路由、症状置信度路由、空注册表处理 |
| **TestBuiltinSkills** | 全部 4 个 Skill 可导入、提示词含中文、get_knowledge() 非空、症状匹配返回 float、内科呼吸知识验证、皮肤科皮疹知识验证、心理科自杀检测、PHQ-9/GAD-7 计算器 |

### 15. DoctorAgent 测试 (16 用例)

| 测试文件 | `tests/unit/agents/test_doctor_agent.py` |
|---------|----------------------------------------|
| **TestDoctorAgentRuleMode** | 空症状处理、降级标注、追问生成、内科/皮肤科/耳鼻喉科/心理科规则断言、自杀危机替换、紧急标记、Skill 自动选择、无科室降级 |
| **TestDoctorAgentLLMIntegration** | Mock LLM 返回 JSON、结构化输出解析、context.diagnosis 存在 |
| **TestDoctorAgentSkillIntegration** | 懒加载机制验证、context.skill_used 记录 |

**Mock LLM 客户端模式:**
```python
class MockLLM:
    async def chat(self, messages: list[dict]) -> str:
        return '''{
            "possible_diagnoses": [
                {"diagnosis": "上呼吸道感染", "likelihood": "高", "reason": "发热咳嗽3天"}
            ],
            "treatment_plan": {
                "lifestyle": ["多休息", "多饮水"],
                "medications": [{"name": "对乙酰氨基酚", "dosage": "500mg", "evidence_level": "C"}]
            },
            "red_flags": [],
            "pending_questions": ["有无咳痰?"]
        }'''
```

---

## 八、关键命令速查

```bash
# 运行所有测试
cd backend && python -m pytest tests/ -v

# 运行 Skill 系统测试
cd backend && python -m pytest tests/unit/agents/test_skill_system.py -v

# 运行 Doctor Agent 测试
cd backend && python -m pytest tests/unit/agents/test_doctor_agent.py -v

# 验证所有 Agent 已注册
python -c "from agents import registry; print(registry.list_agents())"

# 验证 Skill 加载
python -c "from agents.doctor.skills.loader import load_builtin_skills; load_builtin_skills(); from agents.doctor.skills.registry import registry; print(registry.list_skills())"

# 启动后端验证 WebSocket
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 代码覆盖率（需安装 pytest-cov）
cd backend && python -m pytest tests/ --cov=agents --cov=orchestration -v
```

---

## 九、常见问题

### Q: Skill 和 Agent 有什么区别？
**A:** Agent 是完整的"角色"（TriageAgent 负责分诊、DoctorAgent 负责诊断），而 Skill 是 Agent 使用的"知识包"。一个 DoctorAgent 可以根据科室切换不同的 Skill。

### Q: 为什么需要双模式（LLM + 规则引擎）？
**A:** 用户可能没有配置 LLM Key（Ollama 也不一定在运行）。规则引擎确保**零配置也能跑**。降级标注让用户知情。

### Q: 怎么添加一个新的科室 Skill？
**A:** 三步：① 继承 `BaseSkill` 实现 `get_knowledge()`；② 定义 `system_prompt` 和 `match_symptoms()`；③ 在 `loader.py` 的 `load_builtin_skills()` 中添加 import。自动注册。

### Q: 提示词为什么要写那么详细的 JSON Schema？
**A:** 本地模型（Ollama）对模糊指令的响应不如 Claude 稳定。完整的 JSON Schema + 示例显著提升输出格式的可靠性。

### Q: 测试中的 Mock LLM 是什么意思？
**A:** 测试不依赖真实的 LLM 服务。用 `MockLLM` 类模拟 LLM 返回固定 JSON，测试 DoctorAgent 的 JSON 解析逻辑和 HandoverManifest 构建是否正确。
