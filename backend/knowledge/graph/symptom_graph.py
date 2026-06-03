"""SymptomGraph — Builds symptom→disease mapping from structured data.

Designed to import data from:
  - OpenKG DiseaseKG (Chinese, 44k entities, 312k relations)
  - QASystemOnMedicalGraph (Neo4j, 4.2k stars)

Output: JSON file loadable by KnowledgeGraph.load_from_json()
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ── Built-in seed data ─────────────────────────────────────────────────── #
# Basic symptom→disease mappings for common conditions.
# In production, replace with data from OpenKG or Neo4j import.

SEED_SYMPTOM_MAP: dict[str, list[tuple[str, str, float]]] = {
    # Respiratory 呼吸的
    "头痛": [("感冒", "常见症状", 0.6), ("偏头痛", "核心症状", 0.8), ("紧张性头痛", "常见症状", 0.5),
             ("脑膜炎", "伴随症状（需警惕）", 0.3), ("高血压", "可能症状", 0.4)],
    "发热": [("感冒", "常见症状", 0.7), ("流感", "核心症状", 0.8), ("肺炎", "核心症状", 0.7),
             ("支气管炎", "常见症状", 0.5), ("COVID-19", "核心症状", 0.8)],
    "咳嗽": [("感冒", "常见症状", 0.6), ("支气管炎", "核心症状", 0.8), ("肺炎", "常见症状", 0.6),
             ("哮喘", "可能症状", 0.4), ("咽炎", "常见症状", 0.5)],
    "咳痰": [("支气管炎", "核心症状", 0.7), ("肺炎", "常见症状", 0.6), ("COPD", "常见症状", 0.5)],
    "咽喉痛": [("咽炎", "核心症状", 0.9), ("扁桃体炎", "核心症状", 0.8), ("感冒", "常见症状", 0.5)],
    "鼻塞": [("感冒", "常见症状", 0.6), ("过敏性鼻炎", "核心症状", 0.8), ("鼻窦炎", "常见症状", 0.5)],
    "流涕": [("感冒", "常见症状", 0.5), ("过敏性鼻炎", "核心症状", 0.8)],

    # Digestive 消化系统的
    "腹痛": [("急性胃肠炎", "核心症状", 0.6), ("消化性溃疡", "常见症状", 0.5),
             ("肠易激综合征", "常见症状", 0.4), ("阑尾炎", "可能症状", 0.3)],
    "腹泻": [("急性胃肠炎", "核心症状", 0.8), ("食物中毒", "常见症状", 0.6),
             ("肠易激综合征", "常见症状", 0.5)],
    "恶心": [("急性胃肠炎", "常见症状", 0.5), ("胃食管反流", "可能症状", 0.3),
             ("偏头痛", "伴随症状", 0.4)],
    "呕吐": [("急性胃肠炎", "常见症状", 0.5), ("脑膜炎", "伴随症状（需警惕）", 0.3)],
    "烧心": [("胃食管反流", "核心症状", 0.9), ("消化性溃疡", "可能症状", 0.4)],
    "便秘": [("肠易激综合征", "常见症状", 0.5), ("功能性便秘", "核心症状", 0.8)],

    # Cardiovascular 心血管系统的症状
    "胸痛": [("冠心病", "核心症状", 0.7), ("心肌梗死", "紧急症状", 0.6),
             ("肋间神经痛", "可能症状", 0.3), ("焦虑症", "可能症状", 0.3)],
    "心悸": [("心律失常", "核心症状", 0.7), ("焦虑症", "常见症状", 0.5),
             ("甲状腺功能亢进", "常见症状", 0.5)],
    "气短": [("心力衰竭", "核心症状", 0.6), ("哮喘", "常见症状", 0.5),
             ("肺炎", "常见症状", 0.5), ("COPD", "核心症状", 0.7)],
    "头晕": [("高血压", "常见症状", 0.5), ("贫血", "常见症状", 0.4),
             ("颈椎病", "可能症状", 0.4), ("梅尼埃病", "核心症状", 0.6)],

    # Dermatology 皮肤系统的症状
    "皮疹": [("湿疹", "核心症状", 0.7), ("荨麻疹", "核心症状", 0.7),
             ("接触性皮炎", "常见症状", 0.6), ("过敏性皮炎", "常见症状", 0.6)],
    "瘙痒": [("湿疹", "常见症状", 0.6), ("荨麻疹", "核心症状", 0.7),
             ("接触性皮炎", "常见症状", 0.5)],
    "痤疮": [("痤疮", "核心症状", 0.9)],
    "脱发": [("脂溢性皮炎", "常见症状", 0.5), ("斑秃", "核心症状", 0.7)],

    # Mental Health 心理系统的症状
    "失眠": [("焦虑症", "常见症状", 0.5), ("抑郁症", "常见症状", 0.6),
             ("睡眠障碍", "核心症状", 0.8)],
    "焦虑": [("焦虑症", "核心症状", 0.9), ("抑郁症", "伴随症状", 0.4)],
    "抑郁": [("抑郁症", "核心症状", 0.9), ("双相情感障碍", "可能症状", 0.3)],
    "乏力": [("贫血", "常见症状", 0.5), ("甲状腺功能减退", "常见症状", 0.4),
             ("抑郁症", "常见症状", 0.4), ("慢性疲劳综合征", "核心症状", 0.6)],

    # ENT 耳鼻喉系统的症状
    "耳鸣": [("突发性耳聋", "伴随症状", 0.5), ("梅尼埃病", "核心症状", 0.7),
             ("噪音性耳聋", "常见症状", 0.4)],
    "听力下降": [("突发性耳聋", "核心症状", 0.8), ("中耳炎", "常见症状", 0.5),
                 ("老年性耳聋", "核心症状", 0.6)],
    "眩晕": [("梅尼埃病", "核心症状", 0.8), ("BPPV", "核心症状", 0.7),
             ("颈椎病", "可能症状", 0.3)],

    # Musculoskeletal 骨骼系统的症状
    "腰痛": [("腰椎间盘突出", "核心症状", 0.7), ("腰肌劳损", "核心症状", 0.6),
             ("肾结石", "可能症状", 0.3)],
    "关节痛": [("骨关节炎", "核心症状", 0.7), ("类风湿关节炎", "核心症状", 0.6)],
}

SEED_DISEASE_INFO: dict[str, dict[str, Any]] = {
    "感冒": {"department": "内科", "severity": "轻"},
    "流感": {"department": "内科", "severity": "中"},
    "肺炎": {"department": "内科", "severity": "中-重"},
    "支气管炎": {"department": "内科", "severity": "中"},
    "COVID-19": {"department": "内科/传染科", "severity": "中-重"},
    "高血压": {"department": "内科", "severity": "慢病"},
    "冠心病": {"department": "心内科", "severity": "重"},
    "心肌梗死": {"department": "心内科/急诊", "severity": "危重"},
    "心力衰竭": {"department": "心内科", "severity": "重"},
    "心律失常": {"department": "心内科", "severity": "中-重"},
    "急性胃肠炎": {"department": "内科/消化科", "severity": "轻-中"},
    "消化性溃疡": {"department": "消化科", "severity": "中"},
    "胃食管反流": {"department": "消化科", "severity": "慢病"},
    "肠易激综合征": {"department": "消化科", "severity": "慢病"},
    "咽炎": {"department": "耳鼻喉科", "severity": "轻"},
    "扁桃体炎": {"department": "耳鼻喉科", "severity": "中"},
    "过敏性鼻炎": {"department": "耳鼻喉科", "severity": "慢病"},
    "鼻窦炎": {"department": "耳鼻喉科", "severity": "中"},
    "中耳炎": {"department": "耳鼻喉科", "severity": "中"},
    "突发性耳聋": {"department": "耳鼻喉科/急诊", "severity": "急"},
    "梅尼埃病": {"department": "耳鼻喉科", "severity": "慢病"},
    "湿疹": {"department": "皮肤科", "severity": "轻-中"},
    "荨麻疹": {"department": "皮肤科", "severity": "轻"},
    "痤疮": {"department": "皮肤科", "severity": "轻-中"},
    "接触性皮炎": {"department": "皮肤科", "severity": "轻"},
    "焦虑症": {"department": "心理科", "severity": "中"},
    "抑郁症": {"department": "心理科", "severity": "中-重"},
    "睡眠障碍": {"department": "心理科", "severity": "中"},
    "偏头痛": {"department": "神经内科", "severity": "中"},
    "紧张性头痛": {"department": "神经内科", "severity": "轻"},
    "脑膜炎": {"department": "神经内科/急诊", "severity": "危重"},
    "贫血": {"department": "内科", "severity": "中"},
    "甲状腺功能亢进": {"department": "内分泌科", "severity": "中"},
    "甲状腺功能减退": {"department": "内分泌科", "severity": "慢病"},
    "腰椎间盘突出": {"department": "骨科", "severity": "中"},
    "腰肌劳损": {"department": "骨科", "severity": "轻"},
    "骨关节炎": {"department": "骨科", "severity": "慢病"},
    "哮喘": {"department": "呼吸科", "severity": "慢病"},
    "COPD": {"department": "呼吸科", "severity": "慢病"},
}


class SymptomGraphBuilder:
    """Build and export symptom→disease graph data."""

    def __init__(self):
        self.symptom_map = dict(SEED_SYMPTOM_MAP)
        self.disease_info = dict(SEED_DISEASE_INFO)

    def merge_from_openkg(self, json_path: str):
        """Merge data from OpenKG-format JSON (future)."""
        logger.info("OpenKG import not yet implemented. Using seed data.")
        pass

    def export_json(self, output_path: str):
        """Export symptom map to JSON file."""
        data = {}
        for symptom, relations in self.symptom_map.items():
            data[symptom] = [
                {"disease": d, "relation": r, "weight": w}
                for d, r, w in relations
            ]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"symptoms": data, "diseases": self.disease_info},
                      f, ensure_ascii=False, indent=2)
        logger.info("Exported %d symptoms to %s", len(data), output_path)

    def get_diseases_for_symptom(self, symptom: str) -> list[dict]:
        """Get disease suggestions for a symptom (for KG building)."""
        return [
            {"disease": d, "relation": r, "weight": w}
            for d, r, w in self.symptom_map.get(symptom, [])
        ]
