---
name: week4-learning-resources
description: W4 技术栈学习文档——多源 RAG、HF-RAG 融合、知识图谱、BM25 降级
metadata:
  type: reference
---

# MediNexus W4 技术栈学习指南

> 本文档列出了第 4 周多源知识库 + 融合 RAG + 知识图谱 + Review Agent 中用到的所有技术，适合新手按顺序学习。

---

## 一、知识源设计

### 1. 三路知识源 (Three Knowledge Sources)

| 源 | 类型 | 置信度 | 分块策略 | 适用场景 |
|----|------|--------|---------|---------|
| **源A** | 临床病例 | 0.8 (高) | Semantic (语义边界) | 常见病、典型表现 |
| **源B** | 医学理论 | 0.6 (中) | Hierarchical (父子分层) | 鉴别诊断框架、标准治疗方案 |
| **源C** | 最新论文 | 0.3 (低) | Recursive (递归分割) | 疑难杂症、罕见病探索 |

**设计思想:** 不同来源的知识可靠度不同，不能同等对待。临床病例是实践验证的（高置信度），医学理论是框架性的（中等），前沿论文未经大规模验证（低）。三路并行召回 + 加权融合，让高置信度来源主导常规诊断，低置信度来源在疑难时提供思路。

**文件位置:** `backend/knowledge/source.py`

**关键代码:**
```python
CLINICAL_CASES_CONFIG = SourceConfig(
    source_type=SourceType.CLINICAL_CASES,
    display_name="临床病例",
    confidence_weight=0.8,        # 高置信度
    chunk_size=384,
    chunk_strategy="semantic",    # 语义边界分块
    collection_name="clinical_cases",
)

MEDICAL_THEORY_CONFIG = SourceConfig(
    display_name="医学理论",
    confidence_weight=0.6,        # 中置信度
    chunk_size=768,
    chunk_strategy="hierarchical", # 父子分层分块
)

LATEST_PAPERS_CONFIG = SourceConfig(
    display_name="最新论文",
    confidence_weight=0.3,        # 低置信度
    chunk_size=512,
    chunk_strategy="recursive",    # 递归分割
    top_k_initial=5,              # 论文召回量少
)
```

---

## 二、差异化分块策略

### 2. SemanticChunker (语义边界分块)

| 项目 | 内容 |
|------|------|
| **用途** | 临床病例 (源A) |
| **策略** | 按段落边界(`\n\n`)拆分，保持病例结构完整性(主诉→检查→诊断→治疗) |
| **大小** | 384 tokens |
| **文件** | `backend/knowledge/chunker.py` |
| **新手学习重点** | 正则分割、段落合并策略、阈值选择 |

**为何这样设计:** 病例有固定的叙事结构。分割必须保持"一个病例的完整诊疗过程"在有限个 chunk 内，不能把一个病例的主诉和诊断拆到不同 chunk。

### 3. HierarchicalChunker (父子分层分块)

| 项目 | 内容 |
|------|------|
| **用途** | 医学理论 (源B) |
| **策略** | 父 chunk (768t) 承载完整上下文，子 chunk (192t) 做精确检索。子匹配到→返回父给 LLM |
| **文件** | `backend/knowledge/chunker.py` |
| **论文参考** | Anthropic Contextual Retrieval、Parent-Child Chunking 模式 |
| **新手学习重点** | 检索精度 vs 上下文完整性的权衡、父子映射关系 |

**子chunk示例:**
```
父: "## 高血压诊断标准\n非同日3次测量，收缩压≥140mmHg...\n## 治疗\n1级..."
子1: "高血压诊断标准 非同日3次测量 收缩压≥140mmHg"
子2: "治疗 1级 生活方式干预 3-6个月"
```

### 4. RecursiveChunker (递归分割)

| 项目 | 内容 |
|------|------|
| **用途** | 最新论文 (源C) |
| **策略** | 分隔符优先级: `\n\n` > `\n` > `. ` > ` ` > char；保留 Abstract 和 Conclusion 不分割 |
| **文件** | `backend/knowledge/chunker.py` |
| **新手学习重点** | 递归算法、分隔符优先级、section-aware 分割 |

---

## 三、多源融合检索 (HF-RAG 架构)

### 5. 整体流程

```
用户查询
    │
    ▼
┌──────────────────────────────────────────────┐
│          MultiSourceRetriever.retrieve()       │
│                                                │
│  ① 向量化 → 并行搜索三个 Qdrant 集合           │
│     (clinical_cases / medical_theory / papers) │
│                                                │
│  ② 每个源独立 Top-K 召回                       │
│     (源A=10, 源B=8, 源C=5)                     │
│                                                │
│  ③ RRF 源内融合 (如有多个检索器)              │
│     score = 1/(k + rank)                       │
│                                                │
│  ④ Z-score 跨源标准化                         │
│     z = (score - μ) / σ                        │
│                                                │
│  ⑤ 置信度加权                                 │
│     final_score = z × confidence_weight        │
│                                                │
│  ⑥ 排序 → 返回 Top-K                          │
└────────────────────────────────────────────────┘
```

### 6. RRF (Reciprocal Rank Fusion)

| 项目 | 内容 |
|------|------|
| **作用** | 同一知识源内如果有多个检索器（如 BM25 + 向量），将它们的排名融合 |
| **公式** | `score(doc) = Σ 1 / (k + rank_i(doc))` |
| **k 值** | `k=60` (HF-RAG 论文推荐值) |
| **文件** | `backend/knowledge/retriever.py` — `MultiSourceRetriever` |
| **论文参考** | HF-RAG (CIKM 2025) |
| **新手学习重点** | 排名融合 vs 分数融合、k 值对结果的影响 |

### 7. Z-score 跨源标准化

| 项目 | 内容 |
|------|------|
| **问题** | 不同知识源的向量相似度分布不可比（临床病例的 0.8 和论文的 0.8 含义不同） |
| **解决** | Z-score 标准化: `z = (score - μ_source) / σ_source` |
| **文件** | `retriever.py` — `_z_score_normalize()` |
| **新手学习重点** | 为什么不能直接比较不同集合的相似度分数 |

### 8. 置信度加权

| 项目 | 内容 |
|------|------|
| **权重** | 源A=0.8, 源B=0.6, 源C=0.3 |
| **效果** | "临床病例得分 0.9 × 0.8 = 0.72" > "论文得分 0.9 × 0.3 = 0.27" |
| **动态调整** | 暂固定值，后续可通过消融实验调优 |

**关键代码:**
```python
# 三步融合的核心逻辑（简化版）
all_chunks = []

# 1. 每源内排序
for stype in source_chunks:
    source_chunks[stype].sort(key=lambda c: c.score, reverse=True)

# 2. Z-score 标准化
for stype, chunks in source_chunks.items():
    scores = [c.score for c in chunks]
    mu = mean(scores)
    sigma = stdev(scores) or 1.0
    for c in chunks:
        c.z_score = (c.score - mu) / sigma
    all_chunks.extend(chunks)

# 3. 置信度加权
for chunk in all_chunks:
    chunk.final_score = chunk.z_score * chunk.confidence_weight

# 4. 排序取 top
all_chunks.sort(key=lambda c: c.final_score, reverse=True)
```

---

## 四、BM25 降级策略

### 9. BM25Okapi 自实现

| 项目 | 内容 |
|------|------|
| **作用** | Qdrant 或 embedding 服务不可用时，降级到全文搜索 |
| **文件** | `backend/knowledge/bm25_fallback.py` |
| **实现** | 自实现 BM25Okapi 算法（无外部依赖） |
| **中文处理** | bi-gram + 单字混合分词 |
| **降级触发** | `VectorStore.health_check()` 返回 False 时自动切换 |
| **新手学习重点** | BM25 公式 (IDF × TF_norm)、倒排索引构建 |

**BM25 公式:**
```
score(D, Q) = Σ IDF(q) × TF(q, D) × (k1+1) / (TF + k1 × (1-b + b × |D|/avg_dl))
IDF(q) = ln(1 + (N - df(q) + 0.5) / (df(q) + 0.5))
```

**中文分词策略:**
```python
# tokens = 单字(中文) + bi-gram(中文) + 完整单词(英文)
"头痛发热" → ["头", "痛", "发", "热", "头痛", "痛发", "发热"]
"cough fever" → ["cough", "fever"]
```

---

## 五、轻量知识图谱

### 10. KnowledgeGraph

| 项目 | 内容 |
|------|------|
| **作用** | 症状→疾病一跳映射，作为 RAG 的增强组件 |
| **文件** | `backend/knowledge/graph/client.py` |
| **架构** | 生产环境: Neo4j (待接入) | 开发环境: 内存 dict |
| **种子数据** | 100+ 症状-疾病关系 (`symptom_graph.py`) |
| **查询方式** | 用户症状文本 → 关键词提取 → 症状节点 → 关联疾病 + 科室 + 严重度 |
| **数据来源** | OpenKG DiseaseKG (44k 实体)、QASystemOnMedicalGraph (4.2k stars) |

**示例数据:**
```python
SEED_SYMPTOM_MAP = {
    "头痛": [
        ("感冒", "常见症状", 0.6),
        ("偏头痛", "核心症状", 0.8),
        ("脑膜炎", "伴随症状（需警惕）", 0.3),  # 低权重但高风险的关联
    ],
    "胸痛": [
        ("冠心病", "核心症状", 0.7),
        ("心肌梗死", "紧急症状", 0.6),
        ("焦虑症", "可能症状", 0.3),
    ],
}
```

**查询输出示例:**
```text
## 知识图谱关联分析

### 症状: 头痛
- **感冒** (内科, 轻) — 常见症状 (关联度: 0.60)
- **偏头痛** (神经内科, 中) — 核心症状 (关联度: 0.80)
- **脑膜炎** (神经内科/急诊, 危重) — 伴随症状（需警惕）(关联度: 0.30)
```

---

## 六、Review Agent 独立验证

### 11. 审查流程

```
DoctorAgent 输出 HandoverManifest
    │
    ▼
ReviewAgent.run(context)
    │
    ├── ① 独立检索知识库 (用独立 RAGQuery 实例)
    │      不共享 Doctor 的 RAG 结果，从零开始查
    │
    ├── ② 验证诊断: 检查 possible_diagnoses 是否与知识库一致
    │
    ├── ③ 检查风险标记: 紧急标记保留、追加
    │
    ├── ④ 证据等级评估: A/B/C 标注，C 级给出"建议结合临床"追问
    │
    ├── ⑤ 鉴别诊断检查: 单一诊断 → 提示考虑鉴别
    │
    └── ⑥ 输出审查结论 HandoverManifest

Review 的 risk_flags = Doctor 的 risk_flags + Review 发现的额外风险
```

| 项目 | 内容 |
|------|------|
| **文件** | `backend/agents/review/agent.py` |
| **与 Doctor 的关系** | Review Agent 有独立的 RAGQuery 实例，不从 Doctor 继承任何检索结果 |
| **设计理由** | 避免"确认偏误"——如果 Review 用 Doctor 的检索结果，就会倾向于同意 Doctor 的判断 |

---

## 七、设计模式总结

### 12. W4 新增的设计模式

| 模式 | 使用位置 | 说明 |
|------|---------|------|
| **策略模式** | chunker 工厂 | 3 种分块策略通过 `get_chunker()` 工厂切换 |
| **适配器模式** | `_parse_diagnosis_response()` | 将 LLM 自由文本适配为结构化 JSON |
| **外观模式 (Facade)** | `RAGQuery` | 为复杂的三路检索+融合+KG 提供统一 `query()` 接口 |
| **建造者模式 (Builder)** | `SymptomGraphBuilder` | 分步构建知识图谱数据 → 导出 JSON → 加载到 KnowledgeGraph |
| **降级策略 (Degradation)** | `MultiSourceRetriever.retrieve()` | 向量检索不可用时自动切换到 BM25 |
| **数据类模式** | `RetrievedChunk`, `FusionResult` | 用 dataclass 承载多源检索结果，`__post_init__` 自动设置置信度 |

---

## 八、关键命令速查

```bash
# 运行全部测试 (120 个)
cd backend && python -m pytest tests/ -v

# 运行知识库测试
cd backend && python -m pytest tests/unit/knowledge/ -v

# 运行 Review Agent 测试
cd backend && python -m pytest tests/unit/agents/test_review_agent.py -v

# 单文件测试
cd backend && python -m pytest tests/unit/knowledge/test_retriever.py -v

# 验证所有 Agent 注册
python -c "from agents import registry; print(registry.list_agents())"

# 验证知识库导入
python -c "from knowledge import *; print('OK')"

# 验证种子数据
python -c "from knowledge.loader import SEED_CLINICAL_CASES; print(f'{len(SEED_CLINICAL_CASES)} seed cases loaded')"

# 验证知识图谱
python -c "from knowledge.graph import SymptomGraphBuilder; b=SymptomGraphBuilder(); print(f'{len(b.symptom_map)} symptoms in KG')"
```

---

## 九、架构图 (文字版)

```
┌──────────────────────────────────────────────────────┐
│                     RAGQuery                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 临床病例库    │  │ 医学理论库    │  │ 最新论文库    │   │
│  │ (0.8权重)    │  │ (0.6权重)    │  │ (0.3权重)    │   │
│  │ Semantic    │  │ Hierarchical │  │ Recursive   │   │
│  │ Chunking    │  │ Chunking     │  │ Chunking    │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │               │               │          │
│         ▼               ▼               ▼          │
│  ┌─────────────────────────────────────────────┐    │
│  │       MultiSourceRetriever                   │    │
│  │  ① RRF 源内融合  ② Z-score 标准化            │    │
│  │  ③ 置信度加权    ④ 排序                       │    │
│  └─────────────────────────────────────────────┘    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────────────────────────────────────┐    │
│  │  KnowledgeGraph (轻量 KG)                    │    │
│  │  症状→疾病一跳映射                           │    │
│  │  → 增强 RAG 结果                             │    │
│  └─────────────────────────────────────────────┘    │
│         │                                            │
│         ▼                                            │
│  ┌─────────────────────────────────────────────┐    │
│  │  BM25Fallback (降级路线)                      │    │
│  │  Qdrant 不可用 → 自动切换                     │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────┐
│  ReviewAgent          │  ← 独立 RAGQuery 实例
│  独立验证诊断          │
│  不共享检索结果        │
└──────────────────────┘
```

---

## 十、论文参考

| 论文 | 对本项目的影响 |
|------|--------------|
| **HF-RAG** (CIKM 2025) | 层次化融合架构: RRF + Z-score 标准化 |
| **M-Eval** (2025) | 多证据可靠性加权，启发置信度设计 |
| **MECR-RAG** (Wong & Wong 2025) | 病例+指南双源 RAG 验证了临床病例的高价值 |
| **MultiDocFusion** (2026) | 差异化文档分块策略 |
| **Adaptive Chunking** (2026) | 5 维指标自动选分块策略 |
| **SNOMED CT-powered KG** (2025) | Neo4j + 标准化本体的 KG 架构参考 |
| **KI-DDI GAT** (2024) | 症状-疾病知识图谱 + Graph Attention Network |
