"""Dermatology Skill — 皮肤科."""

from agents.doctor.skills.base import BaseSkill
from typing import Any

DERMATOLOGY_SYSTEM_PROMPT = """你是一名经验丰富的**皮肤科医生**。你的任务是协助进行皮肤疾病的诊断和治疗建议。

## 诊断流程

### 步骤 1: 皮损描述
请采集以下信息:
- 部位: 何处出现? 单侧/双侧? 泛发/局限?
- 形态: 斑疹/丘疹/水疱/脓疱/风团/鳞屑/糜烂/溃疡?
- 颜色: 红/暗红/褐/白/肤色?
- 大小: 点状/片状/具体尺寸?
- 边界: 清晰/模糊?
- 表面: 光滑/粗糙/渗出/结痂?

### 步骤 2: 伴随症状
- 瘙痒程度 (1-10)
- 疼痛/灼热感
- 有无发热、关节痛等全身症状

### 步骤 3: 病史
- 病程: 急性(<2周) / 亚急性(2-6周) / 慢性(>6周)
- 诱因: 药物/食物/接触物/日晒/压力
- 既往史: 过敏史、皮肤病史、系统性疾病史
- 家族史: 类似皮肤病家族史

### 步骤 4: 鉴别诊断

### 步骤 5: 治疗建议

## 覆盖疾病范围
湿疹、荨麻疹、痤疮、银屑病、带状疱疹、真菌感染(体癣/足癣)、接触性皮炎、脂溢性皮炎、过敏性紫癜等常见皮肤病。

## 输出格式
使用以下JSON格式输出：
{{
  "analysis": {{
    "lesion_description": {{"location": "部位", "morphology": "形态", "color": "颜色", "distribution": "分布"}},
    "possible_diagnoses": [{{"diagnosis": "诊断名", "likelihood": "高/中/低", "reason": "依据"}}],
    "treatment_plan": {{
      "topical": [{{"name": "外用药", "usage": "用法", "evidence_level": "A/B/C"}}],
      "oral": [{{"name": "口服药", "dosage": "剂量", "evidence_level": "A/B/C"}}],
      "lifestyle": ["建议1", "建议2"]
    }}
  }},
  "red_flags": ["警示信号"],
  "pending_questions": ["还需了解的信息"]
}}

## 警示信号
- 皮疹伴高热、关节痛（可能系统性红斑狼疮或Stevens-Johnson综合征）
- 短期内迅速扩大的色素痣（需排除黑色素瘤）
- 水疱/大疱伴黏膜受累（可能天疱疮）
- 皮疹+呼吸困难（可能严重过敏反应）
- 紫癜/瘀斑伴血小板减少（可能血液系统疾病）

## 证据等级说明
- **Level A**: 基于临床指南或随机对照试验
- **Level B**: 基于专家共识或病例系列
- **Level C**: LLM 经验性建议
"""


class DermatologySkill(BaseSkill):
    name = "dermatology"
    system_prompt = DERMATOLOGY_SYSTEM_PROMPT

    async def get_knowledge(self, context: dict[str, Any]) -> str:
        symptoms = context.get("symptoms", "").lower()
        knowledge_parts = []

        if any(kw in symptoms for kw in ["rash", "皮疹", "red spot", "红斑", "hives", "荨麻疹",
                                          "itch", "痒", "urticaria", "风团"]):
            knowledge_parts.append(
                "【荨麻疹/风团】\n"
                "- 典型表现: 红色或肤色风团, 剧烈瘙痒, 24h内消退不留痕迹\n"
                "- 急性(<6周) vs 慢性(>6周)\n"
                "- 常见诱因: 食物(海鲜/坚果)、药物、感染、物理因素(冷/热/压力)\n"
                "- 一线治疗: 二代抗组胺药(西替利嗪/氯雷他定), Level A\n"
                "- 警告: 伴呼吸困难/喉头水肿 → 立即就医(过敏性休克可能)"
            )

        if any(kw in symptoms for kw in ["acne", "痤疮", "pimple", "痘痘", "粉刺", "青春痘"]):
            knowledge_parts.append(
                "【痤疮/青春痘】\n"
                "- 分级: 轻度(粉刺) → 中度(炎性丘疹) → 重度(结节/囊肿)\n"
                "- 轻度: 外用维A酸(阿达帕林凝胶), Level A\n"
                "- 中度: 外用+口服抗生素(多西环素/米诺环素), Level A\n"
                "- 重度: 口服异维A酸(需监测血脂/肝功能), Level A\n"
                "- 注意事项: 避免挤压, 注意护肤(温和清洁+保湿)"
            )

        if any(kw in symptoms for kw in ["eczema", "湿疹", "dermatitis", "皮炎", "dry skin", "皮肤干燥"]):
            knowledge_parts.append(
                "【湿疹/特应性皮炎】\n"
                "- 典型表现: 红斑、丘疹、渗出、结痂、苔藓样变, 剧烈瘙痒\n"
                "- 好发部位: 肘窝、腘窝、颈部(屈侧分布)\n"
                "- 基础治疗: 保湿(尿素软膏/凡士林), 避免刺激物, Level A\n"
                "- 急性期: 外用糖皮质激素(氢化可的松→糠酸莫米松, 按严重度递进), Level A\n"
                "- 严重: 环孢素/度普利尤单抗(需专科评估)\n"
                "- 注意事项: 洗澡水温不宜过高, 避免搔抓, 穿纯棉衣物"
            )

        if any(kw in symptoms for kw in ["fungal", "真菌", "tinea", "癣", "athlete's foot",
                                          "足癣", "ringworm", "体癣"]):
            knowledge_parts.append(
                "【真菌感染/体癣足癣】\n"
                "- 典型表现: 环状红斑, 边界清晰, 边缘有丘疹/水疱, 中央消退\n"
                "- 足癣: 趾间浸润/脱屑/水疱, 瘙痒\n"
                "- 诊断: 真菌镜检( KOH 涂片)\n"
                "- 治疗: 外用抗真菌药(特比萘芬/克霉唑), 疗程至少2周, Level A\n"
                "- 严重/广泛: 口服特比萘芬/伊曲康唑\n"
                "- 注意事项: 保持干燥, 避免共用毛巾/拖鞋, 疗程需够"
            )

        if not knowledge_parts:
            knowledge_parts.append(
                "【皮肤科通用知识】\n"
                "- 皮疹的鉴别需要详细的视诊和病史\n"
                "- 注意药物过敏史, 尤其是抗生素和NSAIDs\n"
                "- 外用糖皮质激素强度分级: 弱(氢化可的松) → 中(糠酸莫米松) → 强(氯倍他索)"
            )

        return "\n---\n".join(knowledge_parts)

    async def match_symptoms(self, symptoms: str) -> float:
        s = symptoms.lower()
        high_confidence = ["rash", "皮疹", "itch", "痒", "acne", "痤疮", "痘痘", "pimple",
                          "skin", "皮肤", "hives", "荨麻疹", "eczema", "湿疹", "dermatitis",
                          "皮炎", "fungal", "真菌", "tinea", "癣"]
        score = sum(1 for kw in high_confidence if kw in s) / len(high_confidence)
        return min(score * 3, 0.95)  # Amplify, cap at 0.95
