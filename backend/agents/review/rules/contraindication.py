CONTRAINDICATIONS: dict[str, list[str]] = {}


def check_contraindication(drug: str, condition: str) -> bool:
    return condition in CONTRAINDICATIONS.get(drug, []) # 禁忌症检查规则
