"""Document loading pipeline — crawler/scraper interfaces for knowledge sources.

In Phase 1, this provides:
  - Interface definitions for crawlers
  - Test/seed data loading
  - Text file loading utilities

Full crawler implementations (PubMed API, guideline websites) come in Phase 2.
"""

import csv
import json
import logging
import os
from typing import Any

from knowledge.source import SourceType, SOURCE_CONFIGS
from knowledge.chunker import get_chunker
from knowledge.vector_store import VectorStore
from knowledge.bm25_fallback import BM25Fallback

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load, chunk, and index documents into the knowledge base."""

    def __init__(self, vector_store: VectorStore | None = None,
                 bm25_fallback: BM25Fallback | None = None,
                 embedder: Any | None = None):
        self.vector_store = vector_store
        self.bm25_fallback = bm25_fallback
        self.embedder = embedder

    # ── Load from file ────────────────────────────────────────────────── #

    async def load_text_file(self, path: str, source_type: SourceType,
                             metadata: dict[str, Any] | None = None) -> int:
        """Load a single text file, chunk it, and index into vector store and BM25."""
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            return 0

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        return await self.load_text(text, source_type, metadata={
            **(metadata or {}),
            "source_file": os.path.basename(path),
            "source_type": source_type.value,
        })

    async def load_text(self, text: str, source_type: SourceType,
                        metadata: dict[str, Any] | None = None) -> int:
        """Load raw text, chunk by source strategy, index into stores."""
        cfg = SOURCE_CONFIGS[source_type]
        chunker = get_chunker(source_type, cfg.chunk_size, cfg.chunk_overlap)
        metadata = metadata or {}

        chunks = chunker.chunk(text, metadata)
        if not chunks:
            logger.warning("No chunks produced for %s", source_type.value)
            return 0

        logger.info("Chunked %s into %d chunks", source_type.value, len(chunks))

        # Index into vector store
        vs_count = 0
        if self.vector_store and self.embedder:
            texts = [c["text"] for c in chunks]
            embeddings = await self._batch_embed(texts)
            vs_count = await self.vector_store.upsert_chunks(
                cfg.collection_name, chunks, embeddings,
            )

        # Index into BM25 fallback
        bm25_count = 0
        if self.bm25_fallback:
            texts = [c["text"] for c in chunks]
            metas = [c.get("metadata", {}) for c in chunks]
            self.bm25_fallback.index_documents(source_type, texts, metas)
            bm25_count = len(texts)

        logger.info("Indexed %d chunks (vector=%d, bm25=%d) into %s",
                     len(chunks), vs_count, bm25_count, source_type.value)
        return len(chunks)

    # ── Batch load directory ──────────────────────────────────────────── #

    async def load_directory(self, directory: str, source_type: SourceType,
                             pattern: str = "*.txt") -> int:
        """Load all matching files in a directory."""
        import glob
        total = 0
        for filepath in glob.glob(os.path.join(directory, pattern)):
            count = await self.load_text_file(filepath, source_type)
            total += count
        logger.info("Loaded %d total chunks from %s (%s)", total, directory, source_type.value)
        return total

    # ── Embedding Helper ──────────────────────────────────────────────── #

    async def _batch_embed(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        """Batch embed texts."""
        if not self.embedder:
            return []
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                emb = await self.embedder(text) if hasattr(self.embedder, "__call__") else []
                results.append(emb)
        return results

    # ── Seed data ─────────────────────────────────────────────────────── #

    def load_seed_cases(self) -> list[dict[str, Any]]:
        """Load built-in seed clinical cases for development/testing."""
        return SEED_CLINICAL_CASES

    def load_seed_theory(self) -> list[dict[str, Any]]:
        """Load built-in seed medical theory snippets for development/testing."""
        return SEED_MEDICAL_THEORY

    def load_seed_papers(self) -> list[dict[str, Any]]:
        """Load built-in seed paper abstracts for development/testing."""
        return SEED_PAPER_ABSTRACTS


# ── Seed Data ──────────────────────────────────────────────────────────── #

SEED_CLINICAL_CASES = [
    {
        "text": """患者男性，35岁，因"发热、咳嗽3天"就诊。
主诉: 发热(Tmax 38.5°C)、咳嗽(干咳为主)、咽痛。
查体: 咽部充血，双肺呼吸音清。
诊断: 急性上呼吸道感染(感冒)。
处理: 对乙酰氨基酚退热，多饮水休息。预后良好，3-5天自限。""",
        "metadata": {"id": "case_001", "disease": "感冒", "department": "内科"},
    },
    {
        "text": """患者女性，28岁，因"面部及手臂红色皮疹伴瘙痒2天"就诊。
主诉: 接触新护肤品后出现红色斑丘疹，剧烈瘙痒。
查体: 面部、前臂伸侧可见红色斑丘疹，边界不清，有抓痕。
诊断: 接触性皮炎。
处理: 停用可疑护肤品，外用糠酸莫米松乳膏，口服西替利嗪。1周后复诊好转。""",
        "metadata": {"id": "case_002", "disease": "接触性皮炎", "department": "皮肤科"},
    },
    {
        "text": """患者男性，55岁，因"活动后胸痛1个月，加重2小时"入院。
主诉: 1个月前开始快步走时出现胸骨后压榨样疼痛，休息3-5分钟缓解。
2小时前静息状态下出现持续胸痛，伴大汗、恶心。
查体: BP 90/60mmHg，HR 100bpm，心音低钝。
ECG: V1-V4导联ST段抬高。
诊断: 急性前壁ST段抬高型心肌梗死。
处理: 急诊PCI，阿司匹林300mg+替格瑞洛180mg负荷。
转归: PCI后胸痛缓解，住院7天出院。""",
        "metadata": {"id": "case_003", "disease": "心肌梗死", "department": "心内科"},
    },
]

SEED_MEDICAL_THEORY = [
    {
        "text": """【感冒与流感鉴别要点】
普通感冒: 鼻塞、流涕、打喷嚏为主要症状，发热较轻(<38.5°C)，全身症状不明显。
流感: 突发高热(>38.5°C)、全身肌肉酸痛、乏力、头痛明显，呼吸道症状相对较轻。
治疗: 感冒对症治疗即可；流感在发病48h内可用奥司他韦抗病毒。
证据等级: A (CDC指南)""",
        "metadata": {"id": "theory_001", "topic": "感冒流感鉴别", "evidence": "A"},
    },
    {
        "text": """【胸痛鉴别诊断】（重要）
心源性胸痛:
  1. 心绞痛: 劳力诱发，休息或硝酸甘油缓解，持续<15分钟
  2. 心肌梗死: 持续>30分钟，伴大汗、恶心，硝酸甘油不缓解
非心源性胸痛:
  1. 肋间神经痛: 刺痛，与体位有关，按压可诱发
  2. 胃食管反流: 烧灼感，与饮食有关，平卧加重
  3. 焦虑症: 胸闷、气短，与情绪有关，体检无异常
警示: 所有胸痛患者应首先排除心源性原因。""",
        "metadata": {"id": "theory_002", "topic": "胸痛鉴别诊断", "evidence": "A"},
    },
    {
        "text": """【高血压诊断标准与治疗】
诊断: 非同日3次测量，收缩压≥140mmHg和/或舒张压≥90mmHg。
分级:
  1级: 140-159/90-99mmHg
  2级: 160-179/100-109mmHg
  3级: ≥180/110mmHg
治疗:
  1级无靶器官损害: 生活方式干预3-6个月
  1级有靶器官损害/2级以上: 药物治疗
  一线用药: ACEI/ARB(普利类/沙坦类)、CCB(地平类)
证据等级: A (中国高血压防治指南)""",
        "metadata": {"id": "theory_003", "topic": "高血压", "evidence": "A"},
    },
]

SEED_PAPER_ABSTRACTS = [
    {
        "text": """Title: Machine Learning for Early Detection of Sepsis Using Electronic Health Records
Authors: Zhang et al.
Journal: Nature Digital Medicine, 2025
Abstract: This study presents a deep learning model for early sepsis prediction
using routine EHR data. The model achieves AUC 0.92 (95% CI 0.90-0.94) on a
multicenter validation cohort of 50,000 patients. Key features include heart rate
variability, white blood cell trajectory, and lactate trend. Early detection
(>4 hours before clinical diagnosis) could reduce mortality by 15%.
Note: Large-scale validation needed before clinical deployment.""",
        "metadata": {"id": "paper_001", "year": "2025", "journal": "Nature Digital Medicine",
                     "confidence_note": "前沿研究，尚未大规模临床验证"},
    },
    {
        "text": """Title: LLM-Augmented Clinical Reasoning: A Systematic Review
Authors: Smith et al.
Journal: JAMA, 2024
Abstract: Systematic review of 47 studies on LLM applications in clinical reasoning.
Finding: LLMs show promise in differential diagnosis generation (accuracy 72-85%)
but struggle with rare diseases and complex multimorbidity cases.
Recommendation: LLMs should be used as assistive tools, not autonomous diagnostics.
Human oversight remains essential for safe clinical deployment.""",
        "metadata": {"id": "paper_002", "year": "2024", "journal": "JAMA",
                     "confidence_note": "系统综述，参考价值高"},
    },
]
