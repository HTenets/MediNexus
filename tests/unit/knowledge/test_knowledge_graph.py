"""Tests for KnowledgeGraph symptom→disease mapping."""

import pytest
from knowledge.graph import KnowledgeGraph


class TestKnowledgeGraph:
    """KnowledgeGraph — lightweight symptom→disease mapping."""

    def setup_method(self):
        self.kg = KnowledgeGraph()
        self.kg.load_from_dict({
            "头痛": [("偏头痛", "核心症状", 0.8), ("感冒", "常见症状", 0.6)],
            "发热": [("感冒", "常见症状", 0.7), ("肺炎", "常见症状", 0.6)],
            "咳嗽": [("感冒", "常见症状", 0.6), ("支气管炎", "核心症状", 0.8)],
        })
        self.kg.set_disease_info({
            "感冒": {"department": "内科", "severity": "轻"},
            "肺炎": {"department": "内科", "severity": "中"},
        })

    @pytest.mark.asyncio
    async def test_query_returns_formatted_text(self):
        result = await self.kg.query("我头痛发热咳嗽")
        assert result != ""
        assert "偏头痛" in result
        assert "感冒" in result

    @pytest.mark.asyncio
    async def test_query_no_match(self):
        result = await self.kg.query("nothing matches")
        assert result == ""

    @pytest.mark.asyncio
    async def test_get_related_diseases(self):
        diseases = await self.kg.get_related_diseases("头痛")
        assert len(diseases) == 2
        names = [d["disease"] for d in diseases]
        assert "偏头痛" in names
        assert "感冒" in names

    @pytest.mark.asyncio
    async def test_disease_info_returns(self):
        diseases = await self.kg.get_related_diseases("发热")
        assert len(diseases) == 2
        for d in diseases:
            if d["disease"] == "感冒":
                assert d["info"]["department"] == "内科"

    @pytest.mark.asyncio
    async def test_load_from_json(self, tmp_path):
        """JSON loading should work."""
        import json
        json_path = tmp_path / "kg_test.json"
        data = {"symptoms": {
            "test_symptom": [{"disease": "Test Disease", "relation": "test", "weight": 0.5}]
        }, "diseases": {}}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        kg = KnowledgeGraph()
        kg.load_from_json(str(json_path))
        diseases = await kg.get_related_diseases("test_symptom")
        assert len(diseases) == 1
        assert diseases[0]["disease"] == "Test Disease"

    def test_extract_symptoms(self):
        self.kg.load_from_dict({"头痛": [], "发热": []})
        found = self.kg._extract_symptoms("我头痛还发热")
        assert "头痛" in found
        assert "发热" in found
