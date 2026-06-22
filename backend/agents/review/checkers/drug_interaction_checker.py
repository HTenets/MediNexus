"""Drug interaction checker — uses rules/drug_interaction.py."""

from agents.review.checkers import register_checker
from agents.review.rules.drug_interaction import check_drug_in_context


@register_checker("drug_interaction")
def check_drug_interactions(context: dict, diagnosis: dict, prescription: dict) -> list[dict]:
    """Check for drug-drug interactions in the prescription."""
    findings: list[dict] = []
    medications = prescription.get("medications", [])
    if not medications:
        return findings

    drug_names = [m.get("name", "") if isinstance(m, dict) else str(m) for m in medications]
    drug_names = [d for d in drug_names if d]

    checked_pairs = set()
    for drug in drug_names:
        interactions = check_drug_in_context(drug, drug_names)
        for other_drug, interaction in interactions:
            pair = tuple(sorted([drug, other_drug]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            findings.append({
                "checker": "drug_interaction",
                "severity": interaction.severity,
                "drug_a": drug,
                "drug_b": other_drug,
                "finding": f"{drug} 与 {other_drug}: {interaction.mechanism}",
                "recommendation": interaction.recommendation,
            })

    return findings
