"""Seed clinical knowledge for demo retrieval.

Lightweight, dependency-free knowledge snippets used by the Review Agent
when the full RAG (Qdrant) backend is not seeded. Keeps demo reviews
credible without external infrastructure.
"""

SEED_GUIDELINES: dict[str, list[str]] = {
    "respiratory": [
        "《急性上呼吸道感染诊疗规范》: 以对症支持为主，多饮水休息；体温>38.5°C 可予对乙酰氨基酚或布洛芬退热。",
        "《急性支气管炎专家共识》: 咳嗽咳痰无发热者以祛痰为主，不常规使用抗生素，避免滥用。",
        "《流感诊疗方案》: 突发高热伴全身酸痛者应考虑流感，发病48h内可考虑抗病毒药物。",
    ],
    "ent": [
        "《急性咽炎/扁桃体炎诊治》: 病毒性占多数，细菌性需咽拭子确认；化脓性扁桃体炎可考虑青霉素类。",
        "《过敏性鼻炎诊疗指南》: 以回避过敏原+鼻用糖皮质激素+抗组胺药为核心。",
    ],
    "dermatology": [
        "《荨麻疹诊疗指南》: 首选第二代抗组胺药，避免搔抓与已知诱因；伴呼吸困难/喉头水肿需急诊。",
        "《痤疮治疗共识》: 外用药（维A酸/过氧化苯甲酰）为主，中重度口服抗生素或异维A酸需医师评估。",
    ],
    "mental_health": [
        "《抑郁症诊疗指南》: 持续情绪低落>2周伴兴趣减退应尽早就诊，轻中度可心理治疗，中重度需药物。",
        "《焦虑症诊疗专家共识》: 认知行为治疗一线，药物可选SSRIs；自杀意念属紧急，须立即干预。",
    ],
    "gastro": [
        "《急性胃肠炎诊疗》: 以补液和电解质平衡为主，清淡饮食；持续呕吐/血便/高热需就医。",
    ],
    "general": [
        "《全科医学诊疗原则》: 先鉴别危急征（胸痛/呼吸困难/意识障碍），再按症状系统评估，避免漏诊。",
        "《用药安全共识》: 用药前核对过敏史与合并用药，警惕相互作用与肝肾功能影响。",
    ],
}


def _category_of(symptoms: str) -> list[str]:
    text = (symptoms or "").lower()
    cats: list[str] = []
    if any(k in text for k in ["咳嗽", "咳痰", "发热", "感冒", "流感", "发烧", "咽痛", "cough", "fever", "cold", "flu", "sore throat"]):
        cats.append("respiratory")
    if any(k in text for k in ["皮疹", "痒", "痤疮", "荨麻疹", "皮肤", "rash", "itch", "acne", "eczema"]):
        cats.append("dermatology")
    if any(k in text for k in ["耳", "鼻", "咽喉", "ear", "nasal", "sinus", "throat"]):
        cats.append("ent")
    if any(k in text for k in ["焦虑", "抑郁", "失眠", "anxiety", "depress", "insomnia", "睡眠"]):
        cats.append("mental_health")
    if any(k in text for k in ["腹泻", "腹痛", "胃", "恶心", "abdominal", "diarrhea", "stomach", "nausea"]):
        cats.append("gastro")
    if not cats:
        cats.append("general")
    if "general" not in cats:
        cats.append("general")
    return cats


def search_seed_knowledge(symptoms: str, top_k: int = 3) -> str:
    """Return concatenated guideline snippets relevant to the symptoms."""
    cats = _category_of(symptoms)
    snippets: list[str] = []
    for cat in cats:
        snippets.extend(SEED_GUIDELINES.get(cat, []))
    return "\n".join(snippets[:top_k])
