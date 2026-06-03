"""Knowledge source definitions — 3 sources with different chunking and confidence weights.

Source A: Clinical Cases (临床病例)   — weight=0.8, high confidence
Source B: Medical Theory (医学理论)   — weight=0.6, medium confidence
Source C: Latest Papers (最新论文)    — weight=0.3, low confidence
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    CLINICAL_CASES = "clinical_cases"    # 源A
    MEDICAL_THEORY = "medical_theory"    # 源B
    LATEST_PAPERS = "latest_papers"      # 源C


@dataclass
class SourceConfig:
    """Configuration for a knowledge source."""

    source_type: SourceType
    display_name: str
    description: str
    confidence_weight: float
    chunk_size: int
    chunk_overlap: int
    chunk_strategy: str  # "semantic" | "hierarchical" | "recursive"
    collection_name: str  # Qdrant collection name

    # Retrieval settings
    top_k_initial: int = 10       # initial recall per source
    top_k_final: int = 5          # final after fusion
    similarity_threshold: float = 0.3

    # BM25 fallback
    bm25_index_path: str = ""


# ── Built-in source configurations ──────────────────────────────────────── #

CLINICAL_CASES_CONFIG = SourceConfig(
    source_type=SourceType.CLINICAL_CASES,
    display_name="临床病例",
    description="真实临床病例, 经实践验证的诊断和治疗方案",
    confidence_weight=0.8,
    chunk_size=384,
    chunk_overlap=40,
    chunk_strategy="semantic",
    collection_name="clinical_cases",
    top_k_initial=10,
)

MEDICAL_THEORY_CONFIG = SourceConfig(
    source_type=SourceType.MEDICAL_THEORY,
    display_name="医学理论",
    description="教科书、临床指南、专家共识等理论性知识",
    confidence_weight=0.6,
    chunk_size=768,        # 父子分块: parent=768, child=192
    chunk_overlap=80,
    chunk_strategy="hierarchical",
    collection_name="medical_theory",
    top_k_initial=8,
)

LATEST_PAPERS_CONFIG = SourceConfig(
    source_type=SourceType.LATEST_PAPERS,
    display_name="最新论文",
    description="PubMed/arXiv 前沿研究, 用于疑难杂症探索",
    confidence_weight=0.3,
    chunk_size=512,
    chunk_overlap=50,
    chunk_strategy="recursive",
    collection_name="latest_papers",
    top_k_initial=5,       # 论文召回量少, 因为置信度低
)

# Registry
SOURCE_CONFIGS: dict[SourceType, SourceConfig] = {
    SourceType.CLINICAL_CASES: CLINICAL_CASES_CONFIG,
    SourceType.MEDICAL_THEORY: MEDICAL_THEORY_CONFIG,
    SourceType.LATEST_PAPERS: LATEST_PAPERS_CONFIG,
}

# ── Helpers ─────────────────────────────────────────────────────────────── #

@dataclass
class RetrievedChunk: # 检索到的片段类
    """A single retrieved chunk with metadata."""

    text: str
    source: SourceType
    score: float           # raw similarity score 原始相似度分数
    z_score: float = 0.0   # normalized score 归一化分数
    confidence_weight: float = 0.0 
    final_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.confidence_weight = SOURCE_CONFIGS[self.source].confidence_weight


@dataclass
class FusionResult:
    """Result of multi-source fusion."""

    chunks: list[RetrievedChunk]
    source_counts: dict[str, int]
    query: str
    activated_sources: list[SourceType]
