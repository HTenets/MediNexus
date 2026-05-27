# Doctor Agent Platform — 开源多智能体问诊平台设计方案

> 版本: v1.0 | 日期: 2026-05-26

---

## 目录

1. [项目定位与愿景](#1-项目定位与愿景)
2. [整体系统架构](#2-整体系统架构)
3. [多智能体设计详解](#3-多智能体设计详解)
4. [SFT 微调 vs Skill 扩展 深度分析](#4-sft-微调-vs-skill-扩展深度分析)
5. [知识库与 RAG 设计](#5-知识库与-rag-设计)
6. [记忆机制设计](#6-记忆机制设计)
7. [插件与生态扩展](#7-插件与生态扩展)
8. [后端架构与并发设计](#8-后端架构与并发设计)
9. [前端与客户端设计](#9-前端与客户端设计)
10. [微信小程序集成方案](#10-微信小程序集成方案)
11. [数据存储与病历系统](#11-数据存储与病历系统)
12. [安全与合规](#12-安全与合规)
13. [项目路线图](#13-项目路线图)
14. [开源生态与技术选型总结](#14-开源生态与技术选型总结)

---

## 1. 项目定位与愿景

### 1.1 定位

一个**开源、模块化、可扩展的多智能体 AI 问诊平台**，覆盖从导诊、诊断、处方审查到康复随访的全流程。目标是成为 **AI 医疗助手的开源参考实现**。

### 1.2 核心理念

- **模块化**：每个 Agent 独立部署、独立扩展
- **可插拔**：通过 Plugin/Skill 体系无限扩展科室能力
- **渐进式**：从轻量问诊到专家会诊，逐步升级
- **隐私优先**：病历数据本地化存储，支持私有化部署

### 1.3 目标用户

| 用户类型 | 使用场景 |
|---------|---------|
| 个人用户 | 日常健康咨询、慢病管理、用药查询 |
| 诊所/医院 | 辅助导诊、病历整理、处方预审 |
| 开发者 | 二次开发、接入自有系统、定制科室 Agent |
| 研究者 | 医疗 AI 实验、多智能体协作研究 |

---

## 2. 整体系统架构

### 2.1 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐  │
│  │   Web    │  │  Desktop │  │  Mini  │  │   API    │  │
│  │   App    │  │   Pet    │  │Program │  │  SDK     │  │
│  └────┬─────┘  └────┬─────┘  └────┬───┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼────────────┼────────┘
        │             │             │            │
┌───────┼─────────────┼─────────────┼────────────┼────────┐
│       │     Gateway Layer (API Gateway + WAF)           │
│       │     Rate Limiter · Auth · Load Balancer          │
│       └──────────────┬──────────────────┘               │
└──────────────────────┼──────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────┐
│         Orchestration Layer (Agent Supervisor)           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Agent Communication Bus                 │   │
│  │        (Message Queue + Event Stream)             │   │
│  └──┬───────┬───────┬───────┬───────┬───────┬───────┘   │
│     │       │       │       │       │       │            │
│  ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐     │
│  │Triage│ │Doctor │ │Review│ │Mental│ │Follow│ │Coord.│   │
│  │Agent │ │Agent  │ │Agent │ │Health│ │up    │ │Agent │   │
│  └──┬──┘ └──┬───┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘     │
│     │       │        │       │       │       │            │
└─────┼───────┼────────┼───────┼───────┼───────┼──────────┘
      │       │        │       │       │       │
┌─────┼───────┼────────┼───────┼───────┼───────┼──────────┐
│  Infrastructure Layer                                       │
│                                                             │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  LLM APIs  │ │ VectorDB  │ │ GraphDB  │ │ Message  │  │
│  │(OpenAI/etc)│ │(Qdrant/   │ │(Neo4j/   │ │ Queue    │  │
│  │ + Local    │ │ Milvus)   │ │ Nebula)  │ │(RabbitMQ)│  │
│  │(Ollama)    │ │          │ │          │ │          │  │
│  └────────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌────────────┐ ┌──────────┐ ┌──────────────────────┐   │
│  │  Redis     │ │PostgreSQL│ │ Object Store (S3)    │   │
│  │(Cache/Session)│(病历/用户)│ │(影像/报告/文档)       │   │
│  └────────────┘ └──────────┘ └──────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 2.2 智能体通信模式

```
同步通信 (请求-响应):
  Client → [Gateway] → Supervisor → [Specific Agent] → Response

异步通信 (事件驱动):
  Agent A → [Message Bus] → Agent B (独立处理)
  例如: Doctor Agent 完成诊断 → 触发 Review Agent 审查处方

流式通信 (WebSocket/SSE):
  Client ↔ [Gateway] ↔ Supervisor ↔ Agent (实时对话)

会诊模式 (广播-聚合):
  Coordinator → [Broadcast] → Multiple Department Agents
              → [Aggregate] → Unified Diagnosis
```

---

## 3. 多智能体设计详解

### 3.1 智能体全景图

```
                          ┌──────────────────────┐
                          │    Agent Supervisor   │
                          │   (路由/调度/监控)    │
                          └──────┬───────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
  ┌──────▼──────┐       ┌───────▼───────┐       ┌──────▼──────┐
  │  Triage     │       │   Doctor      │       │   Mental    │
  │  Agent      │──────▶│   Agent       │       │   Health    │
  │  (导诊)     │       │   (诊断)      │       │   Agent     │
  └──────┬──────┘       └───────┬───────┘       │  (心理)     │
         │                      │               └──────┬──────┘
         │                      │                       │
         │              ┌───────▼───────┐               │
         │              │   Review      │               │
         │              │   Agent       │               │
         │              │  (处方审查)    │               │
         │              └───────┬───────┘               │
         │                      │                       │
         │              ┌───────▼───────┐               │
         │              │   Follow-up   │               │
         │              │   Agent       │               │
         │              │  (随访)       │               │
         │              └───────┬───────┘               │
         │                      │                       │
         │              ┌───────▼───────┐               │
         └──────────────│  Coordinator  │◄──────────────┘
                        │  Agent        │
                        │  (会诊协调)   │
                        └───────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
              ┌─────▼──┐  ┌────▼───┐  ┌───▼─────┐
              │Dept A   │  │Dept B  │  │Dept C   │
              │Specialist│  │Special.│  │Special. │
              │Agent    │  │Agent   │  │Agent    │
              └─────────┘  └────────┘  └─────────┘
```

### 3.2 各 Agent 详细设计

#### 3.2.1 Triage Agent (导诊Agent)

**职责**：
- 收集患者主诉、症状、基本信息
- 判断 urgency (紧急程度) — 识别需要立即就医的紧急情况
- 分诊到对应科室
- 如果是复合病/多系统症状，标记并转交 Coordinator

**Workflow**：
```
用户输入 → 症状采集 → 紧急评估
                         ├── 紧急 → 强烈建议就医 + 生成紧急报告
                         └── 非紧急 → 科室分诊 → 转交对应 Doctor Agent
```

**Prompt 设计要点**：
- 必须包含「安全红线」：识别心梗、脑卒中、严重外伤等紧急征象
- 追问策略：信息不足时主动追问关键鉴别点
- 不确定时低阈值转诊，宁高勿低

**技术实现**：
- 不需要 SFT，Prompt engineering + 结构化输出即可
- 输出格式：`{ urgency_level, suspected_departments[], symptoms_summary, risk_flags[] }`

#### 3.2.2 Doctor Agent (医生Agent)

**职责**：
- 基于患者主诉进行诊断推理
- 调用科室 Skill 包获取专科知识
- 生成诊断建议、检查建议、治疗方案
- 输出结构化病历

**架构设计**：

```
Doctor Agent (Base)
├── Skill: 内科 (Internal Medicine)
├── Skill: 皮肤科 (Dermatology)
├── Skill: 耳鼻喉 (ENT)
├── Skill: 外科 (Surgery)
├── Skill: 骨科 (Orthopedics)
├── Skill: 儿科 (Pediatrics)
├── Skill: 神经科 (Neurology)
├── Skill: 中医 (TCM)
├── Skill: 营养科 (Nutrition)
├── Skill: 康复科 (Rehabilitation)
└── Skill: 药剂科 (Pharmacy) → 与 Review Agent 联动
```

**诊断流程**：
```
就诊流程:
1. 主诉收集 ── Triage 传入
2. 现病史采集 ── SOP 式追问（发病时间、性质、诱因、演变、诊疗经过）
3. 既往史采集 ── 基础病、过敏史、用药史
4. 鉴别诊断 ── 列出可能的诊断，按概率排序
5. 辅助检查建议 ── 需要做什么检查来验证
6. 诊断结论 ── 给出明确诊断或「待查」
7. 治疗方案 ── 药物/非药物治疗
8. 注意事项 ── 随访、复诊、警示
```

#### 3.2.3 Review Agent (审查Agent)

**职责**：
- 审查处方合理性（药物相互作用、剂量、禁忌症）
- 审查诊断和治疗方案的一致性
- 审查用药是否符合指南规范
- 标记可疑处方，返回审查意见

**审查维度**：
```
┌────────────────────────────────────────────┐
│          处方审查矩阵                        │
├────────────────────────────────────────────┤
│ 1. 适应症审查：药物是否对应该诊断            │
│ 2. 禁忌症审查：患者过敏史/基础病是否冲突      │
│ 3. 相互作用审查：多药联用是否存在风险         │
│ 4. 剂量审查：是否在安全剂量范围内            │
│ 5. 年龄审查：儿童/老年人剂量是否调整          │
│ 6. 指南合规：是否遵循临床指南推荐             │
│ 7. 重复用药：是否存在同类药物重复             │
│ 8. 抗菌药物：使用是否合理（抗菌药物专项）      │
└────────────────────────────────────────────┘
```

**注意**：Review Agent **只给出审查意见，不修改处方**。修改需回到 Doctor Agent。

#### 3.2.4 Mental Health Agent (心理健康Agent)

**职责**：
- 心理状态评估（焦虑、抑郁、压力等筛查量表）
- 日常心理支持、情绪疏导
- 危机干预：识别自伤/自杀倾向 → 触发预警 + 转介
- 压力和情绪管理建议

**特殊设计**：
- 使用专门的心理学 Prompt，语气温和、非评判
- 集成 PHQ-9、GAD-7 等标准量表
- **安全红线**：一旦检测到自伤/自杀意图 → 立即升级为「危机模式」

#### 3.2.5 Coordinator Agent (会诊协调Agent)

**职责**：
- 管理跨科室会诊流程
- 收集团队各 Agent 意见，生成综合诊断
- 处理复杂病例和疑难杂症
- 管理讨论流程（谁先发言、何时投票）

**会诊流程**：
```
复杂病例触发会诊:
1. Coordinator 收到会诊请求 + 患者完整病历
2. 确定需要哪些科室参与
3. 主持会议流程:
   a. 各科室 Agent 独立给出意见
   b. 汇总展示，标记分歧点
   c. 如有分歧，进行第二轮讨论
   d. 达成共识 → 输出综合诊疗方案
   e. 无法达成共识 → 标记为「疑难杂症」+ 建议转线下
4. 生成会诊记录存档
```

#### 3.2.6 Follow-up Agent (随访Agent)

**职责**：
- 按计划跟踪患者康复情况
- 提醒复诊、用药
- 收集治疗反馈，评估疗效
- 发现异常时通知 Doctor Agent 干预

**工作模式**：
- 定时触发（基于预设的随访计划）
- 通过消息推送与用户交互
- 轻量级对话，聚焦在症状变化、用药依从性、副作用

#### 3.2.7 Emergency/Escalation Agent (应急Agent)

**职责**：
- 持续监控所有对话，识别紧急信号
- 管理升级流程
- 向用户推送紧急就医建议，必要时通知预设联系人
- 传染病预警上报（按当地法规）

**触发条件**：
- 症状关键词：胸痛、大量出血、意识障碍等
- 心理/精神危机：自伤、自杀言论
- 传染病：法定传染病症状组合
- 药物严重不良反应

### 3.3 Agent 间协作流程

```
【完整就诊流程】

用户
  │
  ▼
Triage Agent ── 紧急？──→ Emergency Agent → 就医建议
  │
  ▼ (非紧急)
Doctor Agent (加载对应科室 Skill)
  │
  ├── 简单病例 → 诊断 + 处方
  │                   │
  │                   ▼
  │              Review Agent → 通过？→ 输出最终方案
  │                   │不通过
  │                   ▼
  │             回退 Doctor Agent 修改
  │
  ├── 复杂/复合病例 → Coordinator Agent
  │                        │
  │                        ▼
  │                ┌─ 内科专家 Agent ─┐
  │                ├─ 外科专家 Agent ─┤
  │                └─ 其他相关科室 ──┘
  │                        │
  │                        ▼
  │                   综合会诊意见
  │
  └── 慢病/康复 → Follow-up Agent 接管
```

---

## 4. SFT 微调 vs Skill 扩展 深度分析

### 4.1 核心对比

| 维度 | SFT 微调 | Skill 扩展 (Prompt + RAG) |
|------|---------|------------------------|
| **开发成本** | 高（数据收集、清洗、标注、训练） | 低（编写 Prompt + 知识库） |
| **维护成本** | 高（每次更新需重新训练） | 低（更新 Prompt 或知识库即可） |
| **诊断质量** | 稳定、一致性好 | 依赖 Base Model 能力 |
| **领域深度** | 可深度内化领域知识 | 受限于 Context 长度和检索质量 |
| **灵活性** | 低（固定能力边界） | 高（即时切换和组合） |
| **可解释性** | 较低（黑盒） | 较高（Prompt 透明，可追溯来源） |
| **数据隐私** | 训练数据需脱敏 | 不涉及训练数据 |
| **Base Model 升级** | 需重新训练 | 天然兼容 |
| **合规风险** | 需验证对齐 | Prompt 级别可控 |

### 4.2 推荐策略：Hybrid 方案

```
推荐方案：
┌─────────────────────────────────────────────────────────┐
│  Base LLM (通用能力)                                      │
│  ├── 基础医学知识 (预训练已有)                              │
│  └── 通用对话、推理、遵循指令能力                           │
├─────────────────────────────────────────────────────────┤
│  SFT 层 (可选，推荐有以下场景再做)                           │
│  ├── 医学对话格式对齐 (病历生成、SOAP 格式输出)              │
│  ├── 安全对齐 (无害化、合规)                                │
│  └── 特定诊断推理路径学习 (疑难杂症专项)                     │
├─────────────────────────────────────────────────────────┤
│  Skill 层 (核心扩展方式)                                   │
│  ├── 科室知识 (RAG)                                        │
│  ├── 临床指南 (RAG)                                        │
│  ├── 药物信息 (RAG + API)                                  │
│  ├── 诊疗流程 (Prompt Template)                            │
│  └── 推理框架 (CoT、ToT 等技术)                            │
└─────────────────────────────────────────────────────────┘
```

### 4.3 什么时候需要 SFT？

**强烈建议微调的场景**：
1. **输出格式严格对齐** — 如强制输出标准化 SOAP 病历、ICD-10 编码
2. **安全对齐不够** — Base Model 在医疗场景下出现幻觉或不当建议
3. **特定诊断推理模式** — 如放射影像报告解读（需要视觉语言对齐）
4. **方言/本地化** — 需要掌握特定地区的医疗术语和习惯

**不建议微调的场景**：
1. 依赖最新知识 — 大概率学不到，RAG 更好
2. 需要频繁更新 — 维护成本过高
3. 数据量不足 — 可能降低 Base Model 已有能力
4. 通用科室 — 内科、外科等，Prompt + RAG 已足够

### 4.4 Skill 包设计规范

每个 Skill 包是一个自包含的模块，包含：

```
skills/
├── internal-medicine/          # 内科
│   ├── manifest.json           # 元信息：科室名称、描述、版本、依赖
│   ├── system-prompt.md        # 该科室的系统 Prompt
│   ├── diagnosis-flow.yaml     # 诊断流程定义（SOP）
│   ├── knowledge/              # 知识库条目
│   │   ├── common-diseases.md
│   │   ├── guidelines/         # 临床指南
│   │   └── drug-formulary.md
│   ├── tools/                  # 工具定义
│   │   └── calculator.py       # 例如：心血管风险计算器
│   └── tests/                  # 测试用例
│       └── test-cases.json
├── dermatology/                # 皮肤科
│   ├── manifest.json
│   ├── ...
│   └── tools/
│       └── image-analyzer.py   # 皮损图像分析
├── tcm/                        # 中医
│   ├── manifest.json
│   ├── system-prompt.md
│   ├── knowledge/
│   │   ├── syndrome-differentiation.md  # 辨证论治
│   │   ├── herbal-formulas.md           # 方剂
│   │   └── acupuncture-points.md        # 穴位
│   └── tools/
│       └── formula-recommender.py
└── ...
```

**Skill 核心能力**：
1. **System Prompt**：为该科室定制的角色、行为规范
2. **知识注入**：RAG 向量库 + 知识图谱
3. **诊断流程**：SOP 式的问诊路径
4. **工具集**：计算器、评估量表、图像分析等
5. **测试用例**：验证 Skill 效果的标准化测试

### 4.5 可用模型选型

| 模型 | 适用场景 | 部署方式 |
|------|---------|---------|
| GPT-4o / Claude 4 | 核心诊断 Agent | API 调用 |
| DeepSeek-V3 / Qwen2.5 | 国产替代，性价比 | API / 本地 |
| Meditron / BioMistral | 医学专用小模型 | 本地部署 |
| Llama-3-70b | 私有化部署 | 本地 |
| Qwen2.5-7b/14b | 导诊、随访等轻量任务 | 本地 |

---

## 5. 知识库与 RAG 设计

### 5.1 知识架构

```
┌──────────────────────────────────────────────────────┐
│                   Knowledge Layer                      │
│                                                        │
│  ┌─────────────────┐  ┌───────────────────────────┐  │
│  │  Vector Store    │  │      Graph Store          │  │
│  │  (语义检索)      │  │   (医学知识图谱)           │  │
│  ├─────────────────┤  ├───────────────────────────┤  │
│  │ • 医学教材       │  │ • 疾病-症状关系            │  │
│  │ • 临床指南       │  │ • 药物-靶点-疾病          │  │
│  │ • 药品说明书     │  │ • 手术-并发症-预后         │  │
│  │ • 医学论文摘要   │  │ • 证候-方剂-中药 (中医)    │  │
│  │ • 诊断标准(ICD)  │  │ • 科室-疾病-专长           │  │
│  └─────────────────┘  └───────────────────────────┘  │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │          Hybrid Search Engine                   │   │
│  │   (向量检索 + 关键词 + 图遍历)                  │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 5.2 RAG 技术选型

**传统 RAG 的问题**：
- 医学知识关系密集，纯向量检索丢失关系语义
- 简单问题可以，复杂推理时上下文不完整

**推荐方案：GraphRAG + Agentic RAG 混合**

```
【GraphRAG 流程】

文档 → entity extraction → knowledge graph (疾病/症状/药物/检查)
    ↓
查询 → 识别实体 → 图遍历相关子图 → 构建上下文 → 生成回答

【Agentic RAG 流程】

查询 → Router (判断需要什么知识)
  ├── 事实查询 → 直接向量检索
  ├── 关系查询 → 图谱遍历
  ├── 需要推理 → 多步检索 + 推理
  └── 需要最新 → Web Search (联网)
```

### 5.3 具体技术栈推荐

| 技术 | 用途 | 推荐理由 |
|------|------|---------|
| **Qdrant** / **Milvus** | 向量数据库 | 高可用、支持过滤、云原生 |
| **Neo4j** / **NebulaGraph** | 知识图谱 | 成熟、社区大、Cypher 查询 |
| **LightRAG** | 轻量 GraphRAG | 纯 Python，小项目快速启动 |
| **Microsoft GraphRAG** | 企业级 GraphRAG | 深度知识挖掘，适合医学 |
| **BGE-M3** / **GTE-Qwen2** | Embedding 模型 | 多语言、多粒度 |
| **ColBERT** | 延迟交互检索 | 精排效果好，适合医学精准检索 |

### 5.4 知识库建设策略

**第一阶段（MVP）**：
- 爬取公开医学知识（默沙东诊疗手册、UpToDate 摘要、临床指南公开版）
- 主要用传统 RAG
- 向量库 + BM25 混合检索

**第二阶段（进阶）**：
- 构建医学知识图谱
- 引入 GraphRAG
- Agentic RAG 增强复杂推理

**第三阶段（专业）**：
- 引入多模态（医学影像、病理切片）
- 实时知识更新 pipeline

### 5.5 知识更新机制

```
知识更新 Pipeline:

新文档/指南发布
    ↓
文档预处理 (格式转换、分块)
    ↓
双重索引:
  ├── 向量化 → 存入 VectorDB
  └── 实体/关系抽取 → 更新 Knowledge Graph
    ↓
质量验证 (自动 + 人工抽样)
    ↓
发布新版本 (版本号管理, 可回滚)
```

---

## 6. 记忆机制设计

### 6.1 记忆分层架构

```
┌──────────────────────────────────────────────────────────┐
│                     记忆系统                              │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │                L1: 工作记忆                        │    │
│  │  (当前会话上下文, 限制在 Model 的 Context Window 内)  │    │
│  │  存储: Redis (TTL = 会话结束)                      │    │
│  │                                                      │    │
│  │  ├── 当前对话历史                                    │    │
│  │  ├── 当前就诊状态 (state machine)                    │    │
│  │  └── 临时提取的知识片段                              │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │            L2: 情景记忆 (Episodic Memory)          │    │
│  │  (历史就诊记录, 按时间线组织)                       │    │
│  │  存储: PostgreSQL + 向量化索引                     │    │
│  │                                                      │    │
│  │  ├── 每次就诊完整记录 (主诉/诊断/处方/医嘱)          │    │
│  │  ├── 随访记录                                        │    │
│  │  ├── 检查检验结果                                    │    │
│  │  └── 向量化, 支持语义检索「类似上次的症状」          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │           L3: 语义记忆 (Semantic Memory)          │    │
│  │  (从历史中提取的长期知识, 概括性的患者画像)          │    │
│  │  存储: PostgreSQL (结构化)                        │    │
│  │                                                      │    │
│  │  ├── 患者基础信息 (年龄/性别/血型/过敏史)            │    │
│  │  ├── 既往病史 (高血压/糖尿病等慢病 timeline)        │    │
│  │  ├── 家族病史                                        │    │
│  │  ├── 用药历史 (药物过敏、耐药记录)                   │    │
│  │  ├── 手术史                                          │    │
│  │  └── 生活习惯 (吸烟/饮酒/运动)                      │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │          L4: 程序性记忆 (Procedural Memory)        │    │
│  │  (Agent 自身学到的诊疗技能, 跨患者共享)             │    │
│  │  存储: 向量库 + 配置文件                          │    │
│  │                                                      │    │
│  │  ├── 成功/失败的诊疗模式                             │    │
│  │  ├── 用户对 Agent 的反馈偏好                        │    │
│  │  ├── 高频问题的优化回复模板                          │    │
│  │  └── 跨会话的学习总结 (每日/每周总结)               │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 6.2 记忆 Retrieval 策略

```
就诊时记忆检索流程:

1. 患者发起就诊
2. 从 L3 (语义记忆) 加载患者画像 [同步]
3. 从 L2 (情景记忆) 检索相关历史 [异步]
   ├── 最近 3 次就诊摘要 (始终加载)
   ├── 相关主诉的历史记录 (语义相似度 > 阈值)
   └── 过敏史和药物反应记录 (始终加载)
4. 构建到工作记忆 L1
5. 就诊中持续更新 L1
6. 就诊结束时:
   ├── 写入 L2 (完整就诊记录)
   ├── 更新 L3 (更新患者画像、病史)
   └── L4 选择性更新 (如果收到用户反馈)
```

### 6.3 复诊机制

```
复诊流程:

1. Follow-up Agent 根据预设时间触发复诊
2. 加载历史就诊记录 (L2)
3. 检查原治疗方案执行情况
4. 评估目前症状变化:
   ├── 好转 → 继续原方案 或 减量
   ├── 无变化 → 分析原因, 调整方案
   └── 恶化 → 升级到 Doctor Agent, 重新评估
5. 记录随访结果

复诊触发方式:
├── 主动: Agent 按计划推送 (慢病管理)
├── 被动: 用户主动发起
├── 条件: 检查检验结果出来后自动触发
└── 紧急: 监测到异常指标时立即触发
```

### 6.4 记忆技术选型

| 组件 | 技术 | 用途 |
|------|------|------|
| 工作记忆 (L1) | Redis + Context Window | 极速存取, TTL 自动过期 |
| 情景记忆 (L2) | PostgreSQL + pgvector | 结构化 + 向量检索 |
| 语义记忆 (L3) | PostgreSQL | 结构化查询 |
| 程序性记忆 (L4) | Mem0 / 自研 | 长期学习, 跨用户 |
| 记忆压缩 | LLM Summarization | 关键信息提取, 降 Token |
| 记忆合并 | 定时任务 | 去重/纠错/合并 |

---

## 7. 插件与生态扩展

### 7.1 插件分类

```
Plugins
├── Tool Plugins (工具类)
│   ├── 药品查询 (对接药品数据库)
│   ├── 检查检验解读 (血常规、生化等)
│   ├── 医学计算器 (GFR、CURB-65 等)
│   ├── 影像分析 (AI 读片)
│   └── 医保查询 (药品/项目是否医保)
│
├── Knowledge Plugins (知识类)
│   ├── 对接 UpToDate 等知识库
│   ├── 本地化指南 (中国/美国/欧洲指南)
│   └── 科室专病知识包
│
├── Data Plugins (数据类)
│   ├── HIS 对接 (医院信息系统)
│   ├── EHR 导入 (电子病历)
│   └── 可穿戴设备数据接入
│
├── Notification Plugins (通知类)
│   ├── 微信推送
│   ├── 短信/邮件
│   └── 语音呼叫
│
└── Compliance Plugins (合规类)
    ├── 处方药合规检查
    ├── 抗菌药物管理
    └── 毒麻药品管控
```

### 7.2 插件 SDK 设计

```python
# 插件接口示例

class MedicalPlugin:
    """所有插件的基础类"""

    # 元信息
    name: str
    version: str
    description: str
    author: str
    dependencies: list[str] = []

    # 生命周期
    async def initialize(self, context: PluginContext): ...
    async def shutdown(self): ...

    # 能力声明
    capabilities: list[Capability]

    # 工具定义 (给 Agent 调用)
    tools: list[ToolDef]

    # 钩子 (Hook into Agent 流程)
    async def on_pre_diagnosis(self, context: DiagnosisContext): ...
    async def on_post_diagnosis(self, context: DiagnosisContext): ...
    async def on_pre_review(self, context: ReviewContext): ...


# 插件注册示例
plugin_registry = PluginRegistry()

@plugin_registry.register
class DrugInteractionChecker(MedicalPlugin):
    name = "drug-interaction-checker"
    version = "1.0.0"
    description = "检查药物相互作用"
    capabilities = [Capability.DRUG_CHECK]

    tools = [
        ToolDef(
            name="check_drug_interaction",
            description="检查两种药物之间的相互作用",
            parameters={
                "drug_a": str,
                "drug_b": str,
            }
        )
    ]
```

### 7.3 插件市场

```
┌─────────────────────────────────────────────────────────┐
│                   Plugin Market                          │
│                                                          │
│  Official Plugins (官方维护)                              │
│  ├── 药品数据库 (中国药品批文库)                            │
│  ├── 临床指南库 (各学科指南)                               │
│  ├── 医学计算器集                                      │
│  └── 医保目录查询                                       │
│                                                          │
│  Community Plugins (社区贡献)                             │
│  ├── 中药方剂查询                                       │
│  ├── 针灸穴位推荐                                       │
│  ├── 可穿戴设备接入 (小米/华为/Apple Watch)              │
│  └── 就医导航 (对接医院挂号系统)                          │
│                                                          │
│  Enterprise Plugins (企业)                                │
│  ├── HIS 对接适配器                                      │
│  ├── PACS 影像对接                                       │
│  └── 电子病历系统导入                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 8. 后端架构与并发设计

### 8.1 技术栈推荐

| 层次 | 技术选型 | 说明 |
|------|---------|------|
| **API 框架** | FastAPI (Python) / NestJS (Node) | 异步原生, 性能好 |
| **Agent 框架** | LangGraph (推荐) / CrewAI / AutoGen | 状态图编排 |
| **消息队列** | RabbitMQ / Redis Streams | Agent 间通信 |
| **任务队列** | Celery + Redis | 异步任务 (如知识索引) |
| **实时通信** | WebSocket / SSE | 流式对话 |
| **容器化** | Docker + Kubernetes | 部署编排 |
| **可观测** | OpenTelemetry + Prometheus + Grafana | 监控 |
| **API 网关** | Kong / APISIX / Envoy | 路由/限流/鉴权 |

### 8.2 并发架构设计

```
【水平扩展架构】

                          ┌──────────────┐
                          │  Load        │
                          │  Balancer    │
                          └──────┬───────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼────┐           ┌─────▼─────┐          ┌─────▼─────┐
    │ API     │           │  API      │          │  API      │
    │ Gateway │           │  Gateway  │          │  Gateway  │
    │ 实例 1   │           │  实例 2   │          │  实例 N   │
    └────┬────┘           └─────┬─────┘          └─────┬─────┘
         │                     │                       │
         └─────────────────────┼───────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Redis (Session/   │
                    │   Cache/Lock)       │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
    │ Agent   │          │  Agent    │        │  Agent    │
    │ Worker  │          │  Worker   │        │  Worker   │
    │ 实例 1   │          │  实例 2   │        │  实例 N   │
    │(多个Agent)│         │(多个Agent) │       │(多个Agent)│
    └────┬────┘          └─────┬─────┘        └─────┬─────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Message Queue     │
                    │  (Agent间异步通信)   │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
    │PostgreSQL│          │  Qdrant   │        │  Object   │
    │(主从)    │          │  (集群)   │        │  Store    │
    └─────────┘          └───────────┘        └───────────┘
```

### 8.3 关键并发设计决策

#### 8.3.1 Agent 执行模型

```
【每个就诊会话 = 一个 LangGraph 图执行实例】

1. 用户请求 → API Gateway → Supervisor Agent
2. Supervisor 为本次就诊创建一个「执行上下文」
3. 上下文包含: session_id, patient_id, state_machine
4. 各 Agent 在共享上下文中工作
5. 图执行可以是:
   ├── 同步: 简单流程, 串行 (导诊 → 诊断 → 审查)
   └── 异步: 会诊时多个 Agent 并行执行 → 汇总
```

#### 8.3.2 流式输出实现

```python
# 流式架构示例
from fastapi import FastAPI, WebSocket
from langgraph.graph import StateGraph

app = FastAPI()

@app.websocket("/consult/{session_id}")
async def consult_websocket(websocket: WebSocket):
    await websocket.accept()

    # 创建图执行器
    graph = build_consult_graph()

    # 流式执行
    async for event in graph.astream_events({
        "input": user_message,
        "session_id": session_id,
        "patient_id": patient_id,
    }, version="v1"):
        # 将每个事件推送给客户端
        await websocket.send_json(event)

    # 执行完成
    await websocket.send_json({"type": "done"})
```

#### 8.3.3 并发安全

```python
# 使用 Redis 分布式锁防止资源竞争
async def review_prescription(patient_id: str, prescription: dict):
    async with redis_lock(f"patient:{patient_id}:prescription"):
        # 同一时间只有一个 Review Agent 在处理该患者的处方
        result = await review_agent.review(prescription)
        return result

# 文档级锁: 同一患者病历不会被并发写入
async def update_medical_record(patient_id: str, record: dict):
    async with redis_lock(f"patient:{patient_id}:record"):
        current = await load_record(patient_id)
        updated = merge_records(current, record)
        await save_record(patient_id, updated)
```

#### 8.3.4 弹性伸缩策略

```
自动扩缩容策略:

API Gateway: 基于 CPU/连接数/请求延迟
├── HPA: CPU > 70% 或 延迟 > 500ms → 扩容
└── 最小 2, 最大 20

Agent Worker: 基于队列深度
├── 队列长度 > 100 → 扩容
├── Agent 是 IO 密集型 (LLM API 调用)
├── 每个 Worker 可处理 10-20 并发会话
└── 注意 LLM API Rate Limit, 每个 Worker 需要 Token Bucket

数据库: 读写分离
├── PostgreSQL: 主库写入, 从库读取
├── Qdrant: 分片集群
└── Redis: Cluster 模式
```

### 8.4 工程性最佳实践

#### 8.4.1 LLM API 调用优化

```
1. 连接池复用: httpx.AsyncClient keep-alive
2. 请求级超时: connect=5s, read=60s
3. 退避重试: exponential backoff + jitter
4. 请求合并: 短时间内相同请求合并 (如药品查询)
5. 语义缓存: 相似问题命中缓存 (Embedding 相似度)
6. 请求排队: Token Bucket + Priority Queue
   ├── 紧急咨询 → High Priority
   ├── 常规问诊 → Medium Priority
   └── 随访/通知 → Low Priority
7. Fallback 模型: 主模型超时 → 降级到小模型
```

#### 8.4.2 可观测性

```yaml
# OpenTelemetry 追踪指标
traces:
  - name: "consult.full_flow"     # 完整就诊流程追踪
  - name: "agent.*.latency"       # 各 Agent 延迟
  - name: "llm.call"              # LLM 调用链路
  - name: "rag.retrieval"         # 知识检索链路

metrics:
  - name: "consult.duration_ms"   # 就诊时长
  - name: "agent.queue_depth"     # Agent 队列深度
  - name: "llm.token_usage"       # Token 消耗
  - name: "rag.hit_rate"          # RAG 命中率
  - name: "review.pass_rate"      # 处方审查通过率

logs:
  - level: INFO   # 正常流程日志
  - level: WARN   # 重试、降级、阈值接近
  - level: ERROR  # 调用失败、异常状态
```

#### 8.4.3 Graceful Degradation 降级策略

```
当 LLM API 不可用时:
├── 缓存命中 → 返回缓存结果
├── 小模型替代 → 切换本地小模型
├── 离线模式 → 仅提供知识库查询, 不进行诊断
└── 告知用户 → 服务降级, 建议稍后再试

当数据库不可用时:
├── 本地缓存 → 使用本地缓存的知识
├── 降级到基础 RAG → 跳过 GraphRAG
└── 当前会话不受影响 (工作记忆在 Redis)
```

---

## 9. 前端与客户端设计

### 9.1 多端覆盖

```
Client Layer
├── Web App (PWA)
│   ├── 响应式设计, 移动端友好
│   └── 支持离线缓存 (PWA Service Worker)
│
├── Desktop Pet (桌宠)
│   ├── Electron / Tauri 打包
│   ├── 悬浮球/桌面卡片
│   ├── 常驻后台, 语音唤起
│   └── 可爱医生角色 (Live2D/VRM 模型)
│
├── WeChat Mini Program
│   ├── 方便快捷, 微信生态内使用
│   └── 语音输入支持
│
├── Mobile App (Flutter/React Native)
│   ├── 完整功能体验
│   └── 推送通知
│
└── API SDK
    └── 供第三方系统集成
```

### 9.2 Web App 设计

```
Pages:
├── Home
│   ├── 快速咨询入口 (语音/文字)
│   ├── 个人健康卡片 (今日提醒, 用药计划)
│   ├── 紧急求助按钮
│   └── 最近就诊摘要
│
├── Consultation
│   ├── 对话界面 (流式消息展示)
│   ├── 病历卡片实时生成
│   ├── 处方/检查建议展示
│   └── 结束总结
│
├── Medical Records
│   ├── 就诊历史时间线
│   ├── 病历详情
│   ├── 检查检验结果
│   └── 处方记录
│
├── Health Dashboard
│   ├── 体征数据图表 (可穿戴设备)
│   ├── 用药依从性
│   ├── 症状趋势
│   └── 健康评分
│
├── Profile
│   ├── 个人信息 (基础病/过敏史/家族史)
│   ├── 绑定设备
│   ├── 隐私设置
│   └── 家庭成员管理
│
└── Plugin Market
    ├── 浏览/安装插件
    └── 管理已安装插件
```

### 9.3 Desktop Pet 设计 (亮点功能)

```
┌────────────────────────────────────────────────────┐
│              Desktop Pet (桌宠模式)                  │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  悬浮球: 最小化模式                            │   │
│  │  ┌──────┐                                     │   │
│  │  │ 🩺  │  ← 小医生角色 (Live2D 轻度动画)      │   │
│  │  │      │                                      │   │
│  │  │  "今天感觉怎么样？"                         │   │
│  │  └──────┘                                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  展开卡片模式:                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  🏥 个人医生卡片                               │   │
│  │  ─────────────────                             │   │
│  │  医生: Dr. AI                                  │   │
│  │  今日提醒: 12:00 服用降压药                     │   │
│  │  最近就诊: 3天前 (皮肤科)                      │   │
│  │  天气变化提醒: 今天降温, 注意保暖               │   │
│  │                                                │   │
│  │  [快速问诊] [用药记录] [健康日报]              │   │
│  └────────────────────────────────────────────────┘   │
│                                                      │
│  交互方式:                                           │
│  ├── 双击悬浮球 → 快速问诊                          │
│  ├── 悬停 → 显示健康卡片                            │
│  ├── 拖拽 → 移动位置                                │
│  ├── 右键 → 菜单 (设置/退出/切换角色)              │
│  ├── 语音唤起 → "嗨医生" + 直接提问                 │
│  └── 定时提醒 → 吃药/喝水/休息                      │
└──────────────────────────────────────────────────────┘
```

### 9.4 用户自定义能力

| 自定义项 | 说明 |
|---------|------|
| **医生角色** | 选择 AI 医生的性格 (专业/温柔/幽默) |
| **角色外观** | 桌宠的 Live2D 角色、服装、配饰 |
| **健康目标** | 设置个人健康目标 (减重/控糖/降压) |
| **提醒偏好** | 用药/复诊/健康行为提醒的时间和方式 |
| **知识深度** | 选择回答的专业程度 (通俗/专业/学术) |
| **隐私级别** | 控制数据留存范围 (仅本地/云端加密/匿名) |
| **科室偏好** | 常用科室置顶, 自定义快捷入口 |
| **家庭成员** | 添加家人, 切换管理不同成员的健康档案 |
| **插件选择** | 按需安装/卸载功能插件 |
| **主题** | 浅色/深色/自定义主题色 |

---

## 10. 微信小程序集成方案

### 10.1 技术可行性

微信小程序完全可行，技术限制与对策：

| 限制 | 对策 |
|------|------|
| WebSocket 需在特定场景下使用 | 使用 WebSocket 多线程, 或轮询 |
| 包体积 < 2MB | 核心逻辑放云端, 小程序仅 UI 层 |
| 不能直接调用 LLM API | 通过自建后端中转 |
| 需 HTTPS + 已备案域名 | 必须, 标准部署要求 |
| 个人主体限制 | 建议用企业主体注册医疗健康类目 |

### 10.2 小程序架构

```
微信小程序 ─── HTTPS ─── 后端 API ─── Agent System
    │                                              │
    └── WebSocket (流式对话) ───────────────────────┘
```

### 10.3 小程序功能设计

```
Pages:
├── 首页
│   ├── AI 问诊入口 (大按钮)
│   ├── 我的病历
│   ├── 用药提醒
│   ├── 健康资讯
│   └── 紧急求助
│
├── 问诊页
│   ├── 语音输入 (微信原生语音识别)
│   ├── 文字输入
│   ├── 流式对话展示 (Markdown 渲染)
│   └── 图片上传 (皮损拍照等)
│
├── 个人中心
│   ├── 健康档案
│   ├── 就诊记录
│   └── 设置
│
└── 订阅消息 (模板消息)
    ├── 用药提醒
    ├── 复诊提醒
    └── 健康报告
```

### 10.4 小程序对接要点

```javascript
// 小程序端 SDK 示例
const DoctorAI = {
  async startConsult(description) {
    const ws = wx.connectSocket({
      url: `wss://api.example.com/consult/${sessionId}`,
    });

    ws.onMessage((res) => {
      // 流式渲染 AI 回复
      this.appendMessage(JSON.parse(res.data));
    });

    // 发送用户输入
    ws.send({
      data: JSON.stringify({ type: "user_input", content: description }),
    });
  },

  // 上传图片
  async uploadImage(tempPath) {
    return await wx.uploadFile({
      url: "https://api.example.com/upload",
      filePath: tempPath,
      name: "image",
    });
  },
};
```

---

## 11. 数据存储与病历系统

### 11.1 数据模型

```sql
-- 核心数据模型 (PostgreSQL)

-- 用户基础信息
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100),
    gender VARCHAR(10),
    birth_date DATE,
    blood_type VARCHAR(5),
    height_cm DECIMAL(5,1),
    weight_kg DECIMAL(5,1),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 过敏史
CREATE TABLE allergies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    allergen VARCHAR(200),          -- 过敏原 (药物/食物/其他)
    reaction TEXT,                  -- 反应描述
    severity VARCHAR(20),           -- mild/moderate/severe
    verified_at TIMESTAMPTZ
);

-- 既往病史
CREATE TABLE medical_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    condition_name VARCHAR(200),    -- 疾病名称
    icd_code VARCHAR(20),           -- ICD-10 编码
    diagnosed_at DATE,
    status VARCHAR(20),             -- active/resolved/remission
    notes TEXT
);

-- 就诊记录 (SOAP 格式)
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id),
    agent_id VARCHAR(50),           -- 接诊 Agent
    department VARCHAR(100),        -- 科室
    consultation_type VARCHAR(20),  -- initial/followup/emergency
    chief_complaint TEXT,           -- 主诉 (S)
    history_of_present_illness TEXT,-- 现病史 (S)
    objective_findings TEXT,        -- 客观检查 (O)
    assessment TEXT,                -- 评估/诊断 (A)
    assessment_icd_codes JSONB,     -- 诊断编码列表
    plan TEXT,                      -- 计划 (P)
    risk_level VARCHAR(20),         -- low/medium/high
    status VARCHAR(20),             -- ongoing/completed/cancelled
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 处方
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID REFERENCES consultations(id),
    patient_id UUID REFERENCES patients(id),
    status VARCHAR(20),             -- draft/pending/approved/dispensed
    review_status VARCHAR(20),      -- pending/approved/rejected
    review_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- 处方明细
CREATE TABLE prescription_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_id UUID REFERENCES prescriptions(id),
    drug_name VARCHAR(200),
    drug_code VARCHAR(50),          -- 药品编码
    dosage VARCHAR(100),            -- 剂量 (如 500mg)
    frequency VARCHAR(100),         -- 频率 (如 tid)
    route VARCHAR(50),              -- 途径 (口服/外用/注射)
    duration VARCHAR(100),          -- 疗程 (如 7天)
    quantity INTEGER,
    notes TEXT
);

-- 随访记录
CREATE TABLE followups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consultation_id UUID REFERENCES consultations(id),
    patient_id UUID REFERENCES patients(id),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    symptoms_change TEXT,           -- 症状变化
    adherence TEXT,                 -- 用药依从性
    side_effects TEXT,              -- 副作用
    assessment TEXT,                -- 评估
    plan_adjustment TEXT,           -- 方案调整
    next_followup_at TIMESTAMPTZ
);

-- 知识库文档
CREATE TABLE knowledge_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500),
    source VARCHAR(100),            -- 来源 (教材/指南/药品说明书)
    department VARCHAR(100),        -- 关联科室
    doc_metadata JSONB,             -- 元数据 (作者/版本/出版日期)
    content TEXT,
    embedding_id VARCHAR(100),      -- 向量 ID
    created_at TIMESTAMPTZ DEFAULT NOW(),
    version INT DEFAULT 1
);

-- 索引
CREATE INDEX idx_consultations_patient ON consultations(patient_id);
CREATE INDEX idx_consultations_created ON consultations(created_at DESC);
CREATE INDEX idx_followups_scheduled ON followups(scheduled_at)
    WHERE completed_at IS NULL;
CREATE INDEX idx_knowledge_department ON knowledge_docs(department);
```

### 11.2 病历存储方案

```
病历存储策略:

├── 结构化数据 → PostgreSQL
│   ├── 基本信息、病史、诊断、处方 (关系模型)
│   └── 便于查询统计和批量分析
│
├── 非结构化数据 → PostgreSQL JSONB / Object Store
│   ├── 对话全文、AI 推理过程
│   ├── 检查检验报告原文
│   └── 影像文件 (对接 S3/MinIO)
│
├── 向量索引 → Qdrant
│   ├── 病历语义检索 (找类似病例)
│   └── 知识库语义检索
│
└── 长期归档 → 冷存储 (S3 Glacier / 本地归档)
    ├── 超过 2 年的历史病历
    └── 按需解冻恢复
```

### 11.3 数据导出标准

支持导出标准格式，确保数据可迁移：

- **FHIR R4** (HL7 国际标准) — 结构化病历交换
- **PDF** — 可打印的病历报告
- **JSON** — 机器可读的完整数据导出
- **CSV** — 统计用的表格数据

---

## 12. 安全与合规

### 12.1 安全架构

```
┌─────────────────────────────────────────────────────┐
│                   Security Layer                      │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ 传输安全                                          │ │
│  │  ├── 全链路 TLS 1.3                               │ │
│  │  └── mTLS (Agent 间通信)                          │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │ 认证与授权                                        │ │
│  │  ├── OAuth 2.1 + OpenID Connect                  │ │
│  │  ├── JWT (短时效 Access Token + Refresh Token)   │ │
│  │  ├── RBAC (基于角色的访问控制)                     │ │
│  │  │    ├── 患者: 仅自己病历                        │ │
│  │  │    ├── 医生: 授权患者病历                      │ │
│  │  │    ├── 管理员: 系统管理权限                    │ │
│  │  │    └── 开发者: 只读匿名统计数据                │ │
│  │  └── API Key (第三方接入)                        │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │数据安全                                           │ │
│  │  ├── 存储加密 (AES-256, 静态加密)                 │ │
│  │  ├── 字段级加密 (手机号/身份证等敏感字段)         │ │
│  │  ├── LLM 请求脱敏 (去标识化后调用 API)            │ │
│  │  └── 数据分级管理:                                │ │
│  │       ├── L0: 公开数据 (指南/教材)                │ │
│  │       ├── L1: 内部数据 (匿名统计)                 │ │
│  │       ├── L2: 敏感数据 (病历/处方)                │ │
│  │       └── L3: 极度敏感 (身份证/联系方式)          │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │审计日志                                           │ │
│  │  ├── 所有诊断操作记录 (who/what/when)             │ │
│  │  ├── 数据访问记录                                 │ │
│  │  ├── 模型调用记录 (含 Prompt/Response)            │ │
│  │  └── 不可篡改 (日志 append-only + 签名)            │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### 12.2 医疗合规要点

```
合规清单:

1. 数据本地化 ── 患者数据存储在中国境内服务器
2. 隐私政策 ── 明确告知数据用途、存储期限、用户权利
3. 知情同意 ── 首次使用需用户签署知情同意书
4. 免责声明 ── AI 建议仅供参考, 不能替代线下就医
5. 紧急转介 ── 识别紧急情况必须建议线下就医
6. 模型安全 ── 红队测试, 确保不会给出危险建议
7. 处方合规 ── 根据中国法规, AI 不能直接开具处方
   → 策略: AI 生成「用药建议」, 需药师/医生审核确认
8. 广告法 ── 不推荐具体品牌药品, 推荐成分/通用名
```

### 12.3 隐私保护技术

```
LLM 调用时的去标识化流程:

1. 用户输入 → PII Detection (正则 + NER 模型)
2. 检测到 PII (姓名/电话/地址/身份证号)
3. 替换为占位符: "王小明" → "[患者姓名]"
4. 脱敏后的内容发给 LLM
5. LLM 返回结果, 填入占位符
6. 落库时: 原始内容加密存储, 日志中仅存脱敏版本

可选: 同态加密 / 联邦学习 (对合作医院场景)
```

---

## 13. 项目路线图

### 13.1 阶段规划

```
Phase 1: MVP (2-3个月)
├── 基础框架搭建
│   ├── 多 Agent 架构 (LangGraph)
│   ├── Triage + Doctor + Review 三个核心 Agent
│   ├── 简单 RAG 知识库 (VectorDB)
│   └── FastAPI 后端
├── 前端
│   └── Web App (对话界面 + 病历展示)
├── 部署
│   └── Docker Compose 一键部署
└── 科室: 内科、皮肤科

Phase 2: 完善 (2-3个月)
├── 全部科室 Skill 包 (8-10 个)
├── Coordinator Agent (会诊)
├── Follow-up Agent (随访)
├── Mental Health Agent (心理)
├── GraphRAG 知识图谱
├── 记忆系统 (Mem0 / 自研)
├── 插件系统 SDK
├── 微信小程序
└── 科室: 耳鼻喉、外科、骨科、儿科

Phase 3: 企业级 (3-4个月)
├── Desktop Pet (Tauri + Live2D)
├── Kubernetes 部署
├── 多模态 (影像分析插件)
├── FHIR 标准病历导出
├── 可观测体系 (OTel + Prometheus + Grafana)
├── 联邦学习 / 隐私计算
├── 压力测试 + 性能优化
└── 科室: 中医、神经科、营养科、康复科

Phase 4: 生态 (持续)
├── 插件市场
├── 社区贡献 Guide
├── 企业版 (HIS 对接、定制部署)
├── 移动端 App (Flutter)
└── 国际化 (多语言)
```

### 13.2 开源社区策略

```
开源策略:
├── 代码仓库: GitHub (Apache 2.0 或 AGPL)
├── 文档: 中英文双语
├── 社区渠道
│   ├── GitHub Discussions (技术讨论)
│   ├── Discord/微信群 (日常交流)
│   └── 贡献者指南 CONTRIBUTING.md
├── 激励
│   ├── Good First Issue 标签
│   ├── Plugin 开发者认证
│   └── 企业赞助通道
└── 运营
    ├── 月度 Release
    ├── 技术博客 (架构/实现/案例)
    └── Demo 在线体验站
```

---

## 14. 开源生态与技术选型总结

### 14.1 最终技术栈推荐

| 类别 | 首选 | 备选 | 说明 |
|------|------|------|------|
| **Agent 框架** | LangGraph | CrewAI / AutoGen | 状态图编排, 最灵活 |
| **LLM** | Claude 4 / GPT-4o | DeepSeek-V3 / Qwen2.5 | 根据预算和合规选择 |
| **后端** | FastAPI + Python | NestJS + Node | 异步原生, AI 生态好 |
| **向量库** | Qdrant | Milvus / Pinecone | 云原生, 性能好 |
| **图谱库** | Neo4j | NebulaGraph | 社区成熟 |
| **GraphRAG** | LightRAG (轻量) | Microsoft GraphRAG | 按规模选择 |
| **记忆系统** | Mem0 | 自研 + PostgreSQL | 开箱即用 |
| **消息队列** | RabbitMQ | Redis Streams / Kafka | 可靠性优先 |
| **数据库** | PostgreSQL + pgvector | - | 全能选手 |
| **缓存** | Redis | - | 标准选择 |
| **前端 Web** | React + Next.js | Vue + Nuxt | 生态最好 |
| **桌面端** | Tauri + React | Electron | 更轻量 |
| **小程序** | 原生微信小程序 | uniapp | 原生性能好 |
| **容器化** | Docker + Kubernetes | Docker Compose | 按规模 |
| **监控** | OpenTelemetry + Grafana | Datadog(商业) | 开源标准 |

### 14.2 项目仓库结构建议

```
doctor-agent-platform/
├── agents/                    # Agent 定义
│   ├── base.py               # Base Agent 抽象
│   ├── triage/               # 导诊 Agent
│   ├── doctor/               # 医生 Agent (Base)
│   ├── review/               # 审查 Agent
│   ├── mental_health/        # 心理健康 Agent
│   ├── coordinator/          # 会诊协调 Agent
│   └── followup/             # 随访 Agent
├── skills/                   # 科室 Skill 包
│   ├── internal-medicine/
│   ├── dermatology/
│   ├── ent/
│   └── ...
├── plugins/                  # 插件系统
│   ├── sdk/                  # 插件 SDK
│   ├── official/             # 官方插件
│   └── examples/             # 示例插件
├── knowledge/                # 知识库
│   ├── pipeline/             # 知识处理 Pipeline
│   ├── vector_store/         # 向量库操作
│   └── graph/                # 知识图谱操作
├── memory/                   # 记忆系统
│   ├── working/              # 工作记忆
│   ├── episodic/             # 情景记忆
│   └── semantic/             # 语义记忆
├── backend/                  # 后端服务
│   ├── api/                  # API 路由
│   ├── gateway/              # API Gateway
│   ├── auth/                 # 认证授权
│   └── workers/              # 后台任务
├── frontend/                 # 前端
│   ├── web/                  # Web App
│   ├── desktop-pet/          # 桌宠
│   └── weapp/                # 微信小程序
├── infrastructure/           # 基础设施
│   ├── docker/               # Dockerfile
│   ├── k8s/                  # Kubernetes 配置
│   └── monitoring/           # 监控配置
├── docs/                     # 文档
│   ├── architecture.md
│   ├── api-reference.md
│   └── contribution.md
├── tests/                    # 测试
│   ├── unit/
│   ├── integration/
│   └── evaluation/           # Agent 评估
├── scripts/                  # 工具脚本
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 附录 A: 你的问题逐一解答

### A1. 导诊 Agent
✅ 设计见 3.2.1, 独立 Agent, 负责分诊和紧急评估

### A2. 医生 Agent 是否需要 SFT？
**建议不要一开始就 SFT**。先用 Prompt + RAG + Skill 的方式启动。当出现以下情况再考虑 SFT：
- 输出格式一致性差 (病历格式乱)
- 安全性不够 (经常给出打擦边球的建议)
- 特定科室推理不够深入

### A3. 审查 Agent
✅ 设计见 3.2.3, 8 维审查矩阵覆盖处方全维度

### A4. 还需要哪些 Agent？
除了你提到的 3 个, 建议再加：
- **Mental Health Agent** — 心理支持 (很重要, 覆盖日常健康)
- **Coordinator Agent** — 会诊协调
- **Follow-up Agent** — 复诊随访
- **Emergency Agent** — 应急升级

### A5. 复合病/疑难杂症
- 复合病 → Triage 检测到多系统症状 → Coordinator 发起跨科室会诊
- 疑难杂症 → 会诊后仍无法确诊 → 标记「疑难杂症」→ 建议转线下专家
- 知识层面 → GraphRAG 擅长处理疾病间的关联关系

### A6. 专家会诊
见 3.2.5 Coordinator Agent 设计, 实现广播-聚合-共识流程

### A7. 插件扩展
见第 7 章, 完整的 Plugin SDK + Plugin Market 设计

### B1. Skill 包
是的, 你的理解完全正确。每个科室 = 一个 Skill 包 (Prompt + RAG + Tools), 不需要每个科室微调一个模型。见 4.4

### B2. 日常关心
Mental Health Agent + Nutrition Skill + Rehabilitation Skill 覆盖

### B3. 后端并发
见第 8 章, 水平扩展 + 异步 + 消息队列 + 流式输出

### B4. 预警机制
双重检测: Triage Agent 症状级别 + Emergency Agent 持续监控

### B5. RAG 之外的技术
- **GraphRAG** — 知识图谱增强, 处理复杂关系查询
- **Agentic RAG** — Agent 自主决定检索策略
- **HyDE** — 假设文档检索
- **Self-RAG** — 自反思检索
- **混合检索** (向量 + BM25 + 图遍历)

### B6. 记忆机制
见第 6 章, 四层记忆架构 (L1-L4)

### B7. 复诊
见 6.3, Follow-up Agent 管理复诊全流程

### B8. 后端工程问题
见 8.4, 涵盖连接池、降级、可观测、弹性伸缩

### B9. 前端设计
见第 9 章, 多端覆盖设计

### B10. 微信小程序
见第 10 章, 完全可行, 有详细对接方案

### B11. 桌面美观
见 9.3 Desktop Pet 设计, 悬浮球 + 健康卡片 + Live2D 角色

### B12. 用户自定义
见 9.4, 10+ 项自定义能力

### B13. 病历存档
见第 11 章, PostgreSQL + Object Store + 标准导出格式

---

> **本文档为 v1.0 设计方案, 欢迎讨论和修订。**
>
> 核心原则: 模块化、可扩展、隐私优先、从简单开始逐步演进。

---

## 附录 B: 2024-2025 前沿研究与教训总结

### B.1 关键论文概览

| 论文 | 年份/会议 | 核心贡献 | 对本项目的启示 |
|------|----------|---------|--------------|
| **MedGraphRAG** (Oxford) | ACL 2025 | 首个医学专用 GraphRAG, 11数据集 SOTA | 知识库应走 GraphRAG 路线, 纯向量检索不够 |
| **MedSumGraph** | AI in Medicine 2025 | 融合摘要+GraphRAG, 免微调 | 不需要 SFT, 优化的 GraphRAG 就足够 |
| **Agentic Medical KG (AMG-RAG)** | EMNLP 2025 | 自动化 KG 构建和持续更新, F1 74.1% | KG 自动化构建省人工, 持续更新机制可用 |
| **CMedRAGBot** | Comp. Life Sci. 2025 | 中文医疗 GraphRAG, 提高 ~10% 准确率 | 中文医疗场景的参考实现, 可复用 NER 部分 |
| **MediGRAF** | Front. Digital Health 2026 | Neo4j+向量混合 RAG, 100% 事实查询召回 | 混合检索 (Cypher+向量) 是最可靠方案 |
| **AI Hospital** | COLING 2025 | 多智能体医患模拟, 争议解决机制 | 会诊流程可以借鉴其争议解决设计 |
| **Agent Hospital** (清华) | arXiv 2024 | MedAgent-Zero 自我进化, 93.06% 准确率 | 验证了多智能体模拟+自我进化的可行性 |
| **MMedAgent** (斯坦福/哈佛) | arXiv 2024 | 多模态医疗 Agent, 超 GPT-4o | 多模态能力的设计参考 |
| **SOLVE-Med** | arXiv 2025 | 10个 1B 小模型 + Router, 可本地部署 | 低成本科室专科化的一种思路 |
| **Clinical Agents Don't Care** | medRxiv 2025 | Agent 对患者身份篡改几乎无感知 | **必须加入身份验证 guardrail** |
| **CataractBot 部署报告** | arXiv 2024 | 317 名患者, Expert-in-Loop, 92% 准确率 | **专家在环是成功的必要条件** |
| **Learnings from Large-Scale Deployment** | arXiv 2024 | 生产级医疗聊天机器人部署经验 | 评估/延迟/反馈循环的实战参考 |

### B.2 关键教训与避免的坑

#### 🚨 教训 1: Patient Identity Misbinding — 身份验证必须有

**发现** (Klang et al., 2025): 六个模型完成 120 万次 EHR 工具调用, GPT-4.1 仅识别 17.4% 的头部信息篡改, GPT-5 完全未检测出 MRN/年龄置换。

**对策**: 每个 Agent 在处理病历数据前, 必须执行 **Identity Verification Step**:
```
1. 工具调用前: 验证当前 patient_id 与会话上下文一致
2. 读取病历后: 验证关键字段 (姓名/年龄/MRN) 的逻辑一致性
3. 异常检测: 如果某字段与历史记录冲突, 标记并暂停操作
```

#### 🚨 教训 2: Multi-Agent Handover Failure — 交接是最脆弱环节

**发现** (Bayezian, 2025): Agent A 正确识别的信息, 在交给 Agent B 时丢失或错误分类。Agent 存储了信息但在错误时刻无法访问。

**对策**:
- 用结构化记忆快照 (Structured Memory Snapshot) 替代自由文本传递
- 每个跨 Agent 传递加一个 **Handover Manifest**: 明确列出已确定的事实、待确认项、建议
- 交接后由接收 Agent 做 **Acknowledgement Check**: 确认关键信息已接收

#### 🚨 教训 3: 有害建议采纳率 > 有益建议

**发现** (Penda Health, 2025): 7.8% 的 AI 回复包含有害建议, 其中 **58% 被临床医生采纳**; 而有益建议只有 22% 被采纳。

**对策**:
- 有害模式识别: 定期扫描 Agent 输出, 建立「已知有害模式库」
- 建议分级: 所有治疗建议标记证据等级 (指南/专家共识/LLM 生成)
- Review Agent 不只要审处方, 也要审诊断建议

#### 🚨 教训 4: Guardrail 延迟不可忽视

**发现** (Sword Health, 2025): 增加在线安全护栏 (Guardrail) 带来约 30% 的延迟增加。

**对策**:
- 离线/在线混合: 大部分检查在异步后台进行, 只有关键路径在线检查
- Guardrail 分级:
  - L1 (在线, 必检): 身份验证、紧急信号、自杀倾向
  - L2 (异步, 推荐): 处方审查、诊断一致性
  - L3 (离线, 后台): 方案优化、证据更新

#### 🚨 教训 5: 信息可及 ≠ 信息可用

**发现**: "The gap between having information available in the system and having it accessible at the right moment for the right agent proved to be a dominant challenge."

**对策**: 设计 **Contextual Retrieval** 策略, 不是将所有信息塞进 Prompt, 而是根据当前 Agent 和当前诊疗阶段, 准确推送最相关的信息:
- 导诊阶段: 只需要过敏史和主诉
- 诊断阶段: 需要完整既往史和检查结果
- 审查阶段: 需要药物相互作用数据
- 随访阶段: 需要原诊断 + 用药依从性

### B.3 可复用的技术方案

#### 🏗️ 方案 1: MedGraphRAG 检索流程

```
MedGraphRAG 三重图谱结构:
├── 用户文档图谱 (用户自行上传的医学资料)
├── 可信医学源图谱 (指南/教材/药品说明书)
└── UMLS 医学术语图谱 (统一医学语言系统)

U-Retrieval 机制:
1. Top-down: 从最抽象的术语开始检索 (如 "高血压")
2. 逐步细化到具体内容 (如 "高血压用药指南 2025")
3. Bottom-up: 检索结果反馈, 提炼关键信息
4. 多轮迭代直到满足信息需求
```

**可复用程度**: 高。可直接使用其图谱构建思路, UMLS 可以替换为中文的 ICD-10 / 医学词库。

#### 🏗️ 方案 2: 多智能体争议解决机制 (来自 AI Hospital)

```
AI Hospital 的多 Agent 争议解决流程:

1. 各自诊断: 各科室 Agent 独立给出诊断意见
2. 意见对比: 系统检测分歧点
3. 证据展示: 各方展示支持自己诊断的证据
4. 讨论轮次: 最多 N 轮讨论 (设上限防止死循环)
5. 投票表决: 不同意可直接投票
6. 最终裁定: 结合投票结果和证据强度, 由 Coordinator 裁定

参考价值: 完全适用于本项目的会诊设计
```

#### 🏗️ 方案 3: Mem0 三层记忆架构

作为 2025 年生产级基准, Mem0 提供:
- **记忆存储**: Vector DB (语义) + Graph DB (实体关系) + KV (元数据)
- **动态生命周期**: ADD/UPDATE/DELETE/NOOP 操作, 医疗场景使用 ADD-only
- **遗忘曲线**: 基于艾宾浩斯遗忘曲线的自动衰减, 旧数据自动降权
- **性能**: 92.5% 准确率 (LoCoMo), 延迟 1.4s, Token 消耗 <7K

**推荐**: 直接集成 Mem0 作为记忆层, 替代自研。在它之上做医疗场景的定制 (如病历结构化存储)。

#### 🏗️ 方案 4: Multi-Agent 共识引擎 (来自 ReadMyMRI)

```
3+ 并行 AI 模型 → 共识引擎 (70% 阈值) → 最终输出

效果:
├── 假阳性降低 60%
├── 假阴性降低 50%
└── 报告附带统计置信度

适用场景: 对准确率要求极高的诊断环节
代价: 成本增加 3x (3 个模型调用)
建议: 仅在复杂病例会诊时启用此模式
```

### B.4 调研结论汇总

```
对本项目的核心建议:

✅ 做:
- 使用 GraphRAG + 混合检索 (向量 + Cypher + BM25)
- 使用 Mem0 作为记忆基础设施
- 设计结构化 Agent Handover Manifest
- 实现分级 Guardrail (在线/异步/离线)
- 采用 5 个以内 Agent 的优化团队 (<5 性能最佳)
- 加入 Expert-in-Loop 接口 (医生审核)
- 基于已有开源项目 (MedicaAgent, AI Hospital) 快速启动

❌ 避免:
- 过早 SFT 微调 (先 Prompt + RAG, 证据不足不微调)
- Agent 间自由文本传递 (结构化交接)
- 忽略身份验证 (病人数据篡改检测)
- 无证据等级的治疗建议 (必须标记来源和等级)
- 超过 5 个 Agent 的团队 (协调成本 > 收益)

📦 可直接复用的开源项目:
1. Mem0 → 记忆层
2. Qdrant / Neo4j → 知识库存储
3. MedGraphRAG → GraphRAG 构建流程
4. MedAgentSim → 模拟测试环境
5. MedicaAgent → 中文医疗 Agent 参考
```

---

*附录 B 和 C 基于 2024-2025 年最新论文、开源项目和部署经验整理, 参考文献见各章节链接。*
