"""KnowledgeGraph — lightweight symptom→disease mapping.

Provides one-hop graph queries to enhance RAG recall.
In production, backed by Neo4j. In development, uses an in-memory(内存) dict.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """Lightweight knowledge graph for symptom→disease→relation queries.

    Architecture:
      - Production: Neo4j (to be added, volume imported from OpenKG DiseaseKG)
      - Development: In-memory dict loaded from JSON

    Current scope: One-hop symptom→disease mapping only.
    """

    def __init__(self, neo4j_uri: str | None = None,
                 neo4j_user: str | None = None,
                 neo4j_password: str | None = None):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self._driver = None

        # In-memory fallback: symptom → list of (disease, relation, weight)
        self._symptom_map: dict[str, list[tuple[str, str, float]]] = {}
        self._disease_map: dict[str, dict[str, Any]] = {}

    # ── Data Loading ──────────────────────────────────────────────────── #

    def load_from_dict(self, data: dict[str, list[tuple[str, str, float]]]):
        """Load symptom→disease mappings from a dictionary.

        Format: {"symptom_name": [("disease_name", "relation", weight), ...]}
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
        """
        self._symptom_map = data
        logger.info("Loaded %d symptoms into KG", len(data))

    def load_from_json(self, json_path: str):
        """Load symptom→disease mappings from a JSON file.

        Expected JSON format:
        {
          "symptoms": {"头痛": [{"disease": "感冒", "relation": "常见症状", "weight": 0.6}, ...]},
          "diseases": {"感冒": {"department": "内科", "severity": "轻"}}
        }
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract symptoms dict and convert to tuple format
            symptom_data = data.get("symptoms", data)
            if isinstance(symptom_data, dict):
                converted = {}
                for symptom, relations in symptom_data.items():
                    tuples = []
                    if isinstance(relations, list):
                        for rel in relations:
                            if isinstance(rel, dict):
                                tuples.append((
                                    rel.get("disease", ""),
                                    rel.get("relation", ""),
                                    rel.get("weight", 0.5),
                                ))
                            elif isinstance(rel, (list, tuple)):
                                tuples.append(tuple(rel))
                    elif isinstance(relations, (list, tuple)):
                        tuples = list(relations)
                    if tuples:
                        converted[symptom] = tuples
                self.load_from_dict(converted)

            # Extract disease info
            disease_info = data.get("diseases", {})
            if disease_info:
                self.set_disease_info(disease_info)

        except Exception as e:
            logger.error("Failed to load KG JSON from %s: %s", json_path, e)

    def set_disease_info(self, info: dict[str, dict[str, Any]]):
        """Set disease metadata (descriptions, departments, severity)."""
        self._disease_map = info

    # ── Query ─────────────────────────────────────────────────────────── #

    async def query(self, text: str, top_k: int = 5) -> str:
        """Query the knowledge graph for symptom→disease relations.

        Returns a formatted string ready for LLM context injection.
        """
        symptoms = self._extract_symptoms(text)
        if not symptoms:
            return ""

        matches = []
        for symptom in symptoms:
            if symptom in self._symptom_map:
                for disease, relation, weight in self._symptom_map[symptom]:
                    matches.append((symptom, disease, relation, weight))

        if not matches:
            return ""

        # Deduplicate and sort by weight 去重并按权重排序
        seen = set()
        unique_matches = []
        for symptom, disease, relation, weight in matches:
            key = (symptom, disease)
            if key not in seen:
                seen.add(key)
                unique_matches.append((symptom, disease, relation, weight))

        unique_matches.sort(key=lambda x: x[3], reverse=True)
        unique_matches = unique_matches[:top_k]

        # Format as readable text
        lines = ["## 知识图谱关联分析", ""]
        current_symptom = ""
        for symptom, disease, relation, weight in unique_matches:
            if symptom != current_symptom:
                lines.append(f"### 症状: {symptom}")
                current_symptom = symptom
            disease_info = self._disease_map.get(disease, {})
            dept = disease_info.get("department", "")
            severity = disease_info.get("severity", "")
            extra = f" ({dept}, {severity})" if dept or severity else ""
            lines.append(f"- **{disease}**{extra} — {relation} (关联度: {weight:.2f})")

        lines.append("")
        lines.append("*知识图谱提供症状-疾病关联参考，请结合临床判断。*")
        return "\n".join(lines)

    async def get_related_diseases(self, symptom: str) -> list[dict[str, Any]]:
        """Get diseases related to a specific symptom."""
        matches = self._symptom_map.get(symptom, [])
        return [
            {
                "disease": disease,
                "relation": relation,
                "weight": weight,
                "info": self._disease_map.get(disease, {}),
            }
            for disease, relation, weight in matches
        ]

    # ── Helpers ───────────────────────────────────────────────────────── #

    def _extract_symptoms(self, text: str) -> list[str]:
        """Extract symptom-like terms from text. Simple keyword-based."""
        # For now, return all known symptoms that appear in the text
        text_lower = text.lower()
        found = []
        for symptom in self._symptom_map:
            if symptom.lower() in text_lower:
                found.append(symptom)
        return found

    def close(self):
        """Close Neo4j connection if open."""
        if self._driver:
            self._driver.close()
