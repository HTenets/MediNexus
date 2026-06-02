"""ENT Skill — 耳鼻喉科."""

from agents.doctor.skills.base import BaseSkill
from typing import Any

ENT_SYSTEM_PROMPT = """你是一名经验丰富的**耳鼻喉科医生**。你的任务是协助进行耳鼻喉疾病的诊断和治疗建议。

## 诊断流程

### 步骤 1: 症状分析
- 耳: 耳痛/听力下降/耳鸣/耳漏/眩晕
- 鼻: 鼻塞/流涕/鼻出血/嗅觉减退/面部压痛
- 咽喉: 咽痛/声音嘶哑/吞咽困难/异物感/咳嗽

### 步骤 2: 病史采集
- 病程: 急性/慢性
- 诱因: 感冒/过敏/声带使用/环境因素
- 既往史: 过敏性鼻炎史、鼻窦炎史、中耳炎史、手术史
- 危险因素: 吸烟/饮酒/职业暴露

### 步骤 3: 鉴别诊断

### 步骤 4: 治疗建议

## 覆盖疾病范围
中耳炎、鼻炎、鼻窦炎、咽炎、扁桃体炎、喉炎、声带结节、梅尼埃病、突发性耳聋、过敏性鼻炎。

## 输出格式
使用以下JSON格式输出：
{{
  "analysis": {{
    "affected_area": "耳/鼻/咽喉",
    "possible_diagnoses": [{{"diagnosis": "诊断名", "likelihood": "高/中/低", "reason": "依据"}}],
    "treatment_plan": {{
      "medications": [{{"name": "药名", "usage": "用法", "evidence_level": "A/B/C"}}],
      "procedures": ["建议操作(如适用)"],
      "lifestyle": ["建议1", "建议2"]
    }}
  }},
  "red_flags": ["警示信号"],
  "pending_questions": ["还需了解的信息"]
}}

## 警示信号
- 突发性听力下降（72h内 → 耳鼻喉急诊, 需激素治疗）
- 单侧鼻塞伴血涕（需排除鼻腔肿瘤）
- 声音嘶哑超过3周（需喉镜检查排除喉癌）
- 眩晕伴听力下降/耳鸣（可能梅尼埃病）
- 吞咽剧痛伴张口受限（可能扁桃体周围脓肿）
- 颈部肿块伴声嘶（需排查喉部恶性肿瘤）

## 证据等级说明
- **Level A**: 基于临床指南或随机对照试验
- **Level B**: 基于专家共识或病例系列
- **Level C**: LLM 经验性建议
"""


class ENTSkill(BaseSkill):
    name = "ent"
    system_prompt = ENT_SYSTEM_PROMPT

    async def get_knowledge(self, context: dict[str, Any]) -> str:
        symptoms = context.get("symptoms", "").lower()
        knowledge_parts = []

        # Ear symptoms
        if any(kw in symptoms for kw in ["ear", "耳朵", "tinnitus", "耳鸣", "hearing", "听力",
                                          "ear pain", "耳痛", "ear discharge", "耳漏",
                                          "vertigo", "眩晕", "dizziness", "头晕"]):
            knowledge_parts.append(
                "【耳部常见病】\n"
                "- 急性中耳炎: 耳痛+发热+听力下降, 常见于儿童, 抗生素(阿莫西林)治疗, Level A\n"
                "- 分泌性中耳炎: 耳闷+听力下降, 常继发于感冒, 观察/鼓膜穿刺\n"
                "- 突发性耳聋: 72h内突发的感音神经性耳聋, 需尽早激素治疗, Level A\n"
                "- 梅尼埃病: 发作性眩晕(持续20min-12h)+耳鸣+听力波动+耳闷\n"
                "- 良性阵发性位置性眩晕(BPPV): 体位改变诱发眩晕, 手法复位(Epley法)有效, Level A"
            )

        # Nose symptoms
        if any(kw in symptoms for kw in ["nasal", "鼻", "runny nose", "流涕", "stuffiness",
                                          "鼻塞", "sneeze", "打喷嚏", "sinus", "鼻窦",
                                          "nosebleed", "鼻出血", "smell", "嗅觉", "allergic",
                                          "过敏"]):
            knowledge_parts.append(
                "【鼻部常见病】\n"
                "- 过敏性鼻炎: 阵发性喷嚏+清水涕+鼻塞+鼻痒, 鼻喷激素一线治疗(糠酸莫米松), Level A\n"
                "- 急性鼻窦炎: 鼻塞+脓涕+面部压痛+发热, 抗生素(阿莫西林克拉维酸)疗程10-14天, Level A\n"
                "- 慢性鼻窦炎: >12周, 鼻喷激素+生理盐水冲洗, Level A\n"
                "- 鼻出血: 常见于Little区, 压迫止血, 避免挖鼻, 反复出血需电凝\n"
                "- 警示: 单侧鼻塞+血涕+面部麻木 → 需排除鼻腔肿瘤"
            )

        # Throat symptoms
        if any(kw in symptoms for kw in ["sore throat", "咽痛", "喉咙痛", "pharyngitis", "咽炎",
                                          "tonsillitis", "扁桃体", "hoarse", "声嘶", "laryngitis",
                                          "喉炎", "swallow", "吞咽", "cough", "咳嗽",
                                          "voice", "声音", "vocal", "声带"]):
            knowledge_parts.append(
                "【咽喉部常见病】\n"
                "- 急性咽炎/扁桃体炎: 咽痛+发热, 病毒性为主, A组链球菌需抗生素治疗\n"
                "  - Centor评分: 发热>38°C+扁桃体渗出+颈部淋巴结肿大+无咳嗽, ≥3分考虑链球菌\n"
                "- 急性喉炎: 声嘶+咳嗽, 声带休息+充分饮水, 避免过度用嗓\n"
                "- 声带结节/息肉: 持续性声嘶, 常见于过度用嗓者, 言语治疗/手术切除\n"
                "- 咽喉反流: 咽异物感+清嗓+声嘶+烧心, 质子泵抑制剂(奥美拉唑)治疗, Level A\n"
                "- 警示: 声嘶>3周 → 需喉镜检查排除喉癌"
            )

        if not knowledge_parts:
            knowledge_parts.append(
                "【耳鼻喉科通用知识】\n"
                "- 耳鼻喉疾病常相互关联(鼻窦炎可引起中耳炎)\n"
                "- 过敏性鼻炎是哮喘的危险因素, 需综合管理\n"
                "- 吸烟是头颈部肿瘤的主要危险因素"
            )

        return "\n---\n".join(knowledge_parts)

    async def match_symptoms(self, symptoms: str) -> float:
        s = symptoms.lower()
        high_confidence = ["ear", "耳朵", "tinnitus", "耳鸣", "hearing", "听力",
                          "nasal", "鼻塞", "sore throat", "咽痛", "sinus", "鼻窦",
                          "runny nose", "流涕", "sneeze", "打喷嚏", "allergic rhinitis",
                          "过敏性鼻炎", "扁桃体", "tonsil"]
        if any(kw in s for kw in high_confidence):
            return 0.9
        medium = ["cough", "咳嗽", "hoarse", "声嘶", "vertigo", "眩晕", "nosebleed", "鼻出血"]
        if any(kw in s for kw in medium):
            return 0.5
        return 0.0
