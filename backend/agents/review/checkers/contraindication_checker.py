"""Contraindication checker — uses rules/contraindication.py."""

from agents.review.checkers import register_checker
from agents.review.rules.contraindication import (
    check_contraindication, check_allergy, check_age_restriction,
)


@register_checker("contraindication")
def check_contraindications(context: dict, diagnosis: dict, prescription: dict) -> list[dict]:
    """Check drug contraindications against patient conditions and allergies."""
    findings: list[dict] = []

    patient = context.get("patient_info", {}) if isinstance(context, dict) else {}
    conditions = patient.get("conditions", []) if isinstance(patient, dict) else []
    allergies = patient.get("allergies", []) if isinstance(patient, dict) else []
    age_group = patient.get("age_group", "adult") if isinstance(patient, dict) else "adult"

    medications = []
    if isinstance(prescription, dict):
        medications = prescription.get("medications", [])
    drug_names = [m.get("name", "") if isinstance(m, dict) else str(m) for m in medications]

    for drug in drug_names:
        # Contraindications
        for condition in conditions:
            result = check_contraindication(drug, condition)
            if result:
                findings.append({
                    "checker": "contraindication",
                    "severity": result.risk,
                    "drug": drug,
                    "condition": condition,
                    "finding": f"{drug} 在 {condition} 情况下禁忌: {result.reason}",
                    "recommendation": result.recommendation,
                })

        # Allergies
        for allergy in allergies:
            result = check_allergy(drug, allergy)
            if result:
                findings.append({
                    "checker": "allergy",
                    "severity": result.risk,
                    "drug": drug,
                    "allergen": allergy,
                    "finding": f"{drug} 与 {allergy} 存在交叉过敏: {result.reason}",
                    "recommendation": result.recommendation,
                })

        # Age restrictions
        result = check_age_restriction(drug, age_group)
        if result:
            findings.append({
                "checker": "age_restriction",
                "severity": result.risk,
                "drug": drug,
                "age_group": age_group,
                "finding": f"{drug} 在 {age_group} 中使用受限: {result.reason}",
                "recommendation": result.recommendation,
            })

    return findings
