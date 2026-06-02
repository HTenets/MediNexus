"""Mental Health Skill — 心理科/精神科.

Includes PHQ-9 (depression) and GAD-7 (anxiety) screening tools.
"""

from agents.doctor.skills.base import BaseSkill
from typing import Any

MENTAL_HEALTH_SYSTEM_PROMPT = """你是一名经验丰富的**心理科/精神科医生**。你的任务是协助进行心理健康问题的评估和建议。

## 重要声明
⚠️ 本系统仅提供心理健康参考评估, 不能替代专业精神科诊断。自杀倾向或自伤风险者应立即就医。

## 诊断流程

### 步骤 1: 主诉评估
- 核心症状: 情绪低落/焦虑/失眠/躯体不适/行为改变
- 病程: 何时开始? 持续性还是发作性?
- 诱因: 生活事件/工作压力/人际关系

### 步骤 2: 心理评估
- 情绪: 持续性低落/空虚/易怒/情绪波动
- 兴趣: 对事物的兴趣是否减退(快感缺失)
- 睡眠: 失眠/早醒/嗜睡
- 食欲: 增加/减少/体重变化
- 精力: 疲劳感/精力不足/迟缓
- 认知: 注意力/记忆力/决策能力
- 焦虑: 紧张/担忧/恐慌发作/回避行为
- 躯体: 心慌/手抖/出汗/胸闷/头痛/胃痛

### 步骤 3: 风险筛查
- 自杀意念: 频率/强度/计划/既往尝试
- 自伤行为
- 物质滥用
- 暴力倾向

### 步骤 4: PHQ-9 抑郁筛查 (对于疑似抑郁)
在过去两周, 以下情况对您造成多大困扰?

1. 做事提不起劲或没有乐趣 (0-3分)
2. 情绪低落、抑郁或绝望 (0-3分)
3. 入睡困难、易醒或睡得过多 (0-3分)
4. 疲劳或没精神 (0-3分)
5. 胃口差或吃得过多 (0-3分)
6. 觉得自己很差劲或让家人失望 (0-3分)
7. 注意力不集中 (0-3分)
8. 动作或说话慢到被他人察觉 (0-3分)
9. 有自杀或伤害自己的念头 (0-3分)

评分: 0-4=无/轻微 | 5-9=轻度 | 10-14=中度 | 15-19=中重度 | 20-27=重度

### 步骤 5: GAD-7 焦虑筛查 (对于疑似焦虑)
在过去两周, 以下情况对您造成多大困扰?

1. 感到紧张、焦虑或烦躁 (0-3分)
2. 无法停止或控制担忧 (0-3分)
3. 过度担心各种事情 (0-3分)
4. 无法放松 (0-3分)
5. 坐立不安 (0-3分)
6. 容易烦恼或易怒 (0-3分)
7. 感到害怕 (0-3分)

评分: 0-4=无/轻微 | 5-9=轻度 | 10-14=中度 | 15-21=重度

## 输出格式
使用以下JSON格式输出：
{{
  "analysis": {{
    "presenting_complaint": "主诉",
    "screening_results": {{
      "phq9_score": 0,
      "phq9_severity": "无/轻微/轻度/中度/中重度/重度",
      "gad7_score": 0,
      "gad7_severity": "无/轻微/轻度/中度/重度"
    }},
    "possible_diagnoses": [{{"diagnosis": "诊断名(ICD-11编码)", "likelihood": "高/中/低"}}],
    "recommendations": {{
      "self_help": ["建议1", "建议2"],
      "professional": ["专业帮助建议"],
      "medications_note": "药物参考信息(如有)",
      "crisis_resources": "危机资源(如适用)"
    }}
  }},
  "red_flags": ["警示信号"],
  "pending_questions": ["还需了解的信息"],
  "crisis_detected": false
}}

## 警示信号 (立即就医)
- **自杀意念**: 问清楚是否有计划/手段/时间
- **自伤行为**: 询问频率和方式
- **幻觉/妄想**: 询问具体内容和频率
- **躁狂发作**: 情绪异常高涨+精力增加+冲动行为+睡眠减少
- **严重进食障碍**: 体重急剧下降+拒绝进食+暴食/催吐
- 以上情况应立即建议前往精神卫生专科机构评估

## 证据等级说明
- **Level A**: 基于临床指南(APA/CAN/NICE)或大型RCT
- **Level B**: 基于专家共识或队列研究
- **Level C**: LLM 经验性建议
"""


class MentalHealthSkill(BaseSkill):
    name = "mental_health"
    system_prompt = MENTAL_HEALTH_SYSTEM_PROMPT

    async def get_knowledge(self, context: dict[str, Any]) -> str:
        symptoms = context.get("symptoms", "").lower()
        knowledge_parts = []

        if any(kw in symptoms for kw in ["depress", "抑郁", "sad", "悲伤", "hopeless", "绝望",
                                          "cry", "哭", "mood", "情绪", "低落"]):
            knowledge_parts.append(
                "【抑郁障碍】\n"
                "- 核心症状(需至少1项持续>2周): 情绪低落 + 兴趣减退\n"
                "- 附加症状: 食欲变化、睡眠障碍、疲劳、注意力不集中、无价值感、自杀意念\n"
                "- 轻度抑郁: 心理治疗( CBT/IPT)一线, Level A\n"
                "- 中重度抑郁: 抗抑郁药(SSRIs: 舍曲林/艾司西酞普兰) + 心理治疗, Level A\n"
                "- 起效时间: 抗抑郁药通常2-4周起效, 需坚持治疗至少6个月\n"
                "- 注意: PHQ-9第9项(自杀)若≥1分, 需立即评估自杀风险"
            )

        if any(kw in symptoms for kw in ["anxiety", "焦虑", "worry", "担心", "紧张", "nervous",
                                          "panic", "惊恐", "害怕", "恐惧", "dread"]):
            knowledge_parts.append(
                "【焦虑障碍】\n"
                "- 广泛性焦虑: 过度担忧+紧张+易疲劳+注意力不集中+易怒+肌肉紧张+睡眠障碍\n"
                "- 惊恐障碍: 突然发作的心悸+胸闷+窒息感+眩晕+失控感+濒死感\n"
                "- 社交焦虑: 在人前害怕被审视+回避社交+预期性焦虑\n"
                "- 一线治疗: SSRIs(舍曲林/帕罗西汀) + 认知行为治疗(CBT), Level A\n"
                "- 急性症状: 苯二氮䓬类药物用于短期控制(需注意依赖风险), Level A\n"
                "- GAD-7可用于筛查和严重度评估"
            )

        if any(kw in symptoms for kw in ["失眠", "insomnia", "sleep", "睡", "insomniac"]):
            knowledge_parts.append(
                "【睡眠障碍】\n"
                "- 失眠: 入睡困难/维持困难/早醒, 每周≥3次, 持续>3月为慢性\n"
                "- 一线治疗: 认知行为治疗(CBT-I), Level A\n"
                "- 药物治疗: 褪黑素(短期) → 处方药(右佐匹克隆/唑吡坦), 短期使用防依赖\n"
                "- 睡眠卫生: 固定作息、避免咖啡因/酒精、卧室凉爽黑暗、床只用于睡眠\n"
                "- 注意: 早醒+心境低落的组合可能提示抑郁, 需同时评估情绪"
            )

        if any(kw in symptoms for kw in ["stress", "压力", "burnout", "burn out", "过劳",
                                          "疲惫", "exhausted", "work", "工作", "累"]):
            knowledge_parts.append(
                "【压力与职业倦怠】\n"
                "- 核心表现: 情感耗竭+去人格化+成就感降低\n"
                "- 常见于高压力职业(医疗/教育/IT)\n"
                "- 干预: 压力管理(正念/放松训练) + 工作负荷调整 + 社会支持, Level B\n"
                "- 预防: 规律作息、运动、社交、设定工作边界\n"
                "- 注意: 职业倦怠与抑郁有重叠, 若出现情绪低落/快感缺失, 需评估抑郁"
            )

        if not knowledge_parts:
            knowledge_parts.append(
                "【心理健康通用知识】\n"
                "- 心理评估需要综合多方面信息, 避免单一症状下结论\n"
                "- 躯体症状(头痛/胃痛/心悸)可能是心理问题的表现(躯体化)\n"
                "- 心理治疗(CBT/DBT/IPT)和药物治疗各有适应症, 可联合使用\n"
                "- 注意区分: 正常的情绪反应 vs 需要干预的心理障碍\n"
                "- 判断标准: 持续时间(>2周)、严重度(影响功能)、痛苦程度"
            )

        return "\n---\n".join(knowledge_parts)

    async def match_symptoms(self, symptoms: str) -> float:
        s = symptoms.lower()
        high_confidence = ["depress", "抑郁", "anxiety", "焦虑", "panic", "惊恐",
                          "失眠", "insomnia", "mental", "心理", "情绪", "mood",
                          "stress", "压力", "suicide", "自杀"]
        if any(kw in s for kw in high_confidence):
            return 0.95
        medium = ["sleep", "睡", "trouble sleeping", "nervous", "紧张",
                  "worry", "担心", "cry", "哭", "sad", "悲伤"]
        if any(kw in s for kw in medium):
            return 0.6
        return 0.0

    @staticmethod
    def calculate_phq9(responses: list[int]) -> tuple[int, str]:
        """Calculate PHQ-9 total score and severity."""
        total = sum(responses)
        if total <= 4:
            severity = "无/轻微"
        elif total <= 9:
            severity = "轻度"
        elif total <= 14:
            severity = "中度"
        elif total <= 19:
            severity = "中重度"
        else:
            severity = "重度"
        return total, severity

    @staticmethod
    def calculate_gad7(responses: list[int]) -> tuple[int, str]:
        """Calculate GAD-7 total score and severity."""
        total = sum(responses)
        if total <= 4:
            severity = "无/轻微"
        elif total <= 9:
            severity = "轻度"
        elif total <= 14:
            severity = "中度"
        else:
            severity = "重度"
        return total, severity
