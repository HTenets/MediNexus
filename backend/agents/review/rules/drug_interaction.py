DRUG_INTERACTIONS = {}


def check_drug_interaction(drug_a: str, drug_b: str) -> str | None:
    return DRUG_INTERACTIONS.get((drug_a, drug_b))
