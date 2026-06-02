"""Internal Medicine Skill — 内科."""

from agents.doctor.skills.base import BaseSkill
from typing import Any

INTERNAL_MEDICINE_SYSTEM_PROMPT = """你是一名经验丰富的**内科医生**。你的任务是协助进行内科疾病的诊断和治疗建议。

## 诊断流程
请严格按以下步骤进行分析：

### 步骤 1: 主诉分析
- 提取患者的主诉（主要症状）
- 确定症状的 onset（起病时间）、duration（持续时间）、severity（严重程度）

### 步骤 2: 病史采集
- 现病史（Present Illness）：症状的演变过程
- 既往史（Past History）：高血压、糖尿病、心脏病等慢性病史
- 过敏史（Allergies）：药物过敏
- 家族史（Family History）：家族遗传病史

### 步骤 3: 鉴别诊断
列出 2-4 个可能的诊断，按可能性从高到低排列。

### 步骤 4: 建议检查
- 基础检查：血常规、尿常规、生化
- 针对性检查：根据鉴别诊断推荐

### 步骤 5: 治疗建议
- 生活方式建议
- 药物治疗（如适用）
- 随访安排

## 覆盖疾病范围
常见呼吸系统（感冒、流感、支气管炎、肺炎）、消化系统（胃炎、肠炎、消化性溃疡）、心血管（高血压、冠心病）、内分泌（糖尿病、甲状腺疾病）、泌尿系统（尿路感染）等内科常见病。

## 输出格式
使用以下JSON格式输出：
{{
  "analysis": {{
    "chief_complaint": "主诉",
    "possible_diagnoses": [{{"diagnosis": "诊断名", "likelihood": "高/中/低", "reason": "依据"}}],
    "suggested_exams": ["检查1", "检查2"],
    "treatment_plan": {{
      "lifestyle": ["建议1", "建议2"],
      "medications": [{{"name": "药名", "dosage": "剂量", "evidence_level": "A/B/C", "notes": "备注"}}],
      "follow_up": "随访建议"
    }}
  }},
  "red_flags": ["警示信号1", "警示信号2"],
  "pending_questions": ["还需了解的信息1", "信息2"]
}}

## 警示信号
以下情况须标记为 red_flags:
- 胸痛伴出汗、恶心（可能心肌梗死）
- 呼吸困难、发绀
- 高热不退（>39.5°C 超过 3 天）
- 意识改变、昏厥
- 严重头痛伴颈强直
- 呕血或黑便

## 证据等级说明
- **Level A**: 基于临床指南或大规模随机对照试验
- **Level B**: 基于专家共识或队列研究
- **Level C**: LLM 经验性建议
"""


class InternalMedicineSkill(BaseSkill):
    name = "internal_medicine"
    system_prompt = INTERNAL_MEDICINE_SYSTEM_PROMPT

    async def get_knowledge(self, context: dict[str, Any]) -> str:
        """Return relevant internal medicine knowledge based on context."""
        symptoms = context.get("symptoms", "").lower()
        knowledge_parts = []

        # Respiratory symptoms # 呼吸系统症状
        if any(kw in symptoms for kw in ["cough", "咳嗽", "fever", "发烧", "sore throat",
                                          "喉咙痛", "cold", "感冒", "flu", "流感", "bronchitis",
                                          "支气管炎", "pneumonia", "肺炎", "shortness of breath",
                                          "气短", "呼吸困难"]):
            knowledge_parts.append(
                "【呼吸系统】常见病鉴别:\n"
                "- 普通感冒: 鼻塞、流涕、咽痛, 通常自限性, 7-10天\n"
                "- 流感: 突发高热(>38.5°C)、全身酸痛、乏力, 抗病毒药物(奥司他韦)在48h内有效\n"
                "- 急性支气管炎: 咳嗽为主, 可伴发热, 多数为病毒性, 抗生素无效\n"
                "- 社区获得性肺炎: 发热+咳嗽+咳痰+气促, 需抗生素治疗\n"
                "- COVID-19: 发热、干咳、嗅觉味觉减退, 注意流行病学史"
            )

        # Digestive symptoms # 消化系统症状
        if any(kw in symptoms for kw in ["stomach", "胃", "abdominal", "腹部", "nausea", "恶心",
                                          "vomiting", "呕吐", "diarrhea", "腹泻", "constipation",
                                          "便秘", "heartburn", "烧心", "ulcer", "溃疡"]):
            knowledge_parts.append(
                "【消化系统】常见病鉴别:\n"
                "- 急性胃肠炎: 恶心呕吐+腹泻, 常见于不洁饮食, 补液为主\n"
                "- 胃食管反流: 烧心、反酸, 餐后或平卧加重\n"
                "- 消化性溃疡: 上腹痛(餐前/餐后痛), 可伴黑便\n"
                "- 肠易激综合征: 腹痛+排便习惯改变, 排除器质性病变后诊断"
            )
        
        # Cardiovascular symptoms # 心血管系统症状
        if any(kw in symptoms for kw in ["chest pain", "胸痛", "palpitations", "心悸",
                                          "hypertension", "高血压", "dizziness", "头晕",
                                          "shortness of breath", "气短", "edema", "水肿"]):
            knowledge_parts.append(
                "【心血管系统】常见病鉴别:\n"
                "- 高血压: 收缩压≥140mmHg和/或舒张压≥90mmHg, 需长期管理\n"
                "- 冠心病: 胸痛(劳累诱发, 休息缓解), 警惕心肌梗死(持续胸痛+出汗)\n"
                "- 心力衰竭: 气促+下肢水肿+乏力, BNP/NT-proBNP升高\n"
                "- 心律失常: 心悸+脉律不齐, 需心电图确认"
            )

        # Endocrine symptoms # 内分泌系统症状
        if any(kw in symptoms for kw in ["diabetes", "糖尿病", "thyroid", "甲状腺",
                                          "weight loss", "消瘦", "fatigue", "乏力",
                                          "thirst", "口渴", "polyuria", "多尿"]):
            knowledge_parts.append(
                "【内分泌系统】常见病鉴别:\n"
                "- 2型糖尿病: 多饮多尿多食+消瘦, 空腹血糖≥7.0mmol/L\n"
                "- 甲状腺功能亢进: 心悸+手抖+消瘦+多汗, TSH↓ FT4↑\n"
                "- 甲状腺功能减退: 乏力+怕冷+体重增加+便秘, TSH↑ FT4↓"
            )

        if not knowledge_parts:
            knowledge_parts.append(
                "【内科通用知识】\n"
                "- 详细问诊应包括: 起病时间、诱因、症状演变、伴随症状、诊疗经过\n"
                "- 注意患者的年龄、基础疾病、用药史对诊断的影响"
            )

        return "\n---\n".join(knowledge_parts)

    async def match_symptoms(self, symptoms: str) -> float:
        s = symptoms.lower()
        # 对明显的内科症状高度自信
        high_confidence = ["fever", "发烧", "cough", "咳嗽", "cold", "感冒", "flu", "流感",
                          "stomach", "胃", "diarrhea", "腹泻", "hypertension", "高血压",
                          "diabetes", "糖尿病", "headache", "头痛"]
        if any(kw in s for kw in high_confidence):
            return 0.9
        # 对内科症状中等自信
        medium = ["chest pain", "胸痛", "dizziness", "头晕", "nausea", "恶心", "fatigue", "乏力"]
        if any(kw in s for kw in medium):
            return 0.6
        return 0.0
