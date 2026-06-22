"""Contraindication and allergy checking rules."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ContraindicationResult:
    risk: Literal["contraindicated", "major", "moderate", "minor"]
    reason: str
    recommendation: str = ""


CONTRAINDICATIONS: dict[str, dict[str, ContraindicationResult]] = {
    "ibuprofen": {
        "peptic_ulcer": ContraindicationResult(
            risk="contraindicated",
            reason="NSAIDs exacerbate peptic ulcer and increase bleeding risk",
            recommendation="Use acetaminophen instead",
        ),
        "renal_insufficiency": ContraindicationResult(
            risk="major",
            reason="NSAIDs reduce renal blood flow",
            recommendation="Monitor renal function, avoid prolonged use",
        ),
    },
    "metformin": {
        "renal_insufficiency": ContraindicationResult(
            risk="contraindicated",
            reason="Lactic acidosis risk in renal impairment",
            recommendation="Switch to alternative antidiabetic agent",
        ),
        "liver_disease": ContraindicationResult(
            risk="major",
            reason="Impaired lactate clearance",
            recommendation="Monitor liver function",
        ),
    },
    "aspirin": {
        "peptic_ulcer": ContraindicationResult(
            risk="contraindicated",
            reason="Aspirin increases GI bleeding risk",
            recommendation="Add PPI or use clopidogrel",
        ),
        "g6pd_deficiency": ContraindicationResult(
            risk="contraindicated",
            reason="Risk of hemolytic anemia",
            recommendation="Avoid aspirin use",
        ),
    },
    "acetaminophen": {
        "liver_disease": ContraindicationResult(
            risk="major",
            reason="Hepatotoxicity risk in liver disease",
            recommendation="Max 2g daily, monitor liver function",
        ),
    },
}


ALLERGIES: dict[str, dict[str, ContraindicationResult]] = {
    "amoxicillin": {
        "penicillin_allergy": ContraindicationResult(
            risk="contraindicated",
            reason="Cross-reactivity with penicillin allergy",
            recommendation="Use macrolide or quinolone instead",
        ),
    },
    "penicillin": {
        "penicillin_allergy": ContraindicationResult(
            risk="contraindicated",
            reason="Known penicillin allergy",
            recommendation="Use macrolide or quinolone instead",
        ),
    },
    "sulfonamides": {
        "sulfa_allergy": ContraindicationResult(
            risk="contraindicated",
            reason="Known sulfa allergy",
            recommendation="Use alternative antibiotic class",
        ),
    },
    "ibuprofen": {
        "aspirin_allergy": ContraindicationResult(
            risk="major",
            reason="Cross-reactivity risk in patients with aspirin allergy",
            recommendation="Use acetaminophen instead",
        ),
    },
}


AGE_RESTRICTIONS: dict[str, dict[str, ContraindicationResult]] = {
    "aspirin": {
        "children": ContraindicationResult(
            risk="contraindicated",
            reason="Reye syndrome risk in children with viral illness",
            recommendation="Use acetaminophen or ibuprofen instead",
        ),
        "elderly": ContraindicationResult(
            risk="major",
            reason="Increased bleeding risk in elderly",
            recommendation="Use with PPI, monitor renal function",
        ),
    },
    "ibuprofen": {
        "children_under_3m": ContraindicationResult(
            risk="contraindicated",
            reason="Not approved for infants under 3 months",
            recommendation="Consult pediatrician",
        ),
    },
}


def check_contraindication(drug: str, condition: str) -> ContraindicationResult | None:
    """Check if a drug is contraindicated for a given condition."""
    drug_contraindications = CONTRAINDICATIONS.get(drug.lower())
    if drug_contraindications:
        return drug_contraindications.get(condition.lower())
    return None


def check_allergy(drug: str, allergy: str) -> ContraindicationResult | None:
    """Check if a drug has a known allergy cross-reaction."""
    drug_allergies = ALLERGIES.get(drug.lower())
    if drug_allergies:
        return drug_allergies.get(allergy.lower())
    return None


def check_age_restriction(drug: str, age_group: str) -> ContraindicationResult | None:
    """Check if a drug has age-based restrictions."""
    restrictions = AGE_RESTRICTIONS.get(drug.lower())
    if restrictions:
        return restrictions.get(age_group.lower())
    return None


def check_all_contraindications(
    drug: str,
    conditions: list[str],
    allergies: list[str],
    age_group: str,
) -> list[dict]:
    """Comprehensive check: conditions + allergies + age restrictions."""
    findings: list[dict] = []

    for condition in conditions:
        result = check_contraindication(drug, condition)
        if result:
            findings.append({
                "type": "contraindication",
                "drug": drug,
                "condition": condition,
                "risk": result.risk,
                "reason": result.reason,
                "recommendation": result.recommendation,
            })

    for allergy in allergies:
        result = check_allergy(drug, allergy)
        if result:
            findings.append({
                "type": "allergy",
                "drug": drug,
                "allergen": allergy,
                "risk": result.risk,
                "reason": result.reason,
                "recommendation": result.recommendation,
            })

    if age_group:
        result = check_age_restriction(drug, age_group)
        if result:
            findings.append({
                "type": "age_restriction",
                "drug": drug,
                "age_group": age_group,
                "risk": result.risk,
                "reason": result.reason,
                "recommendation": result.recommendation,
            })

    return findings
