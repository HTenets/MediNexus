"""Drug-drug interaction checker."""

from dataclasses import dataclass
from typing import Literal

Severity = Literal["contraindicated", "major", "moderate", "minor"]

@dataclass
class Interaction:
    severity: Severity
    mechanism: str
    recommendation: str

DRUG_INTERACTIONS = {
    ("aspirin", "ibuprofen"): Interaction("moderate", "Ibuprofen reduces aspirin antiplatelet effect", "Use acetaminophen instead"),
    ("aspirin", "warfarin"): Interaction("major", "Increased bleeding risk", "Monitor INR closely, add PPI"),
    ("warfarin", "ibuprofen"): Interaction("major", "NSAIDs increase warfarin bleeding risk", "Use acetaminophen instead"),
    ("warfarin", "amoxicillin"): Interaction("moderate", "Antibiotics enhance warfarin", "Increase INR monitoring"),
    ("atorvastatin", "clarithromycin"): Interaction("contraindicated", "CYP3A4 inhibition", "Switch to azithromycin"),
    ("nifedipine", "clarithromycin"): Interaction("contraindicated", "Increased nifedipine concentration", "Switch antibiotic"),
    ("metronidazole", "warfarin"): Interaction("major", "Metronidazole inhibits warfarin metabolism", "Monitor INR closely"),
    ("metronidazole", "alcohol"): Interaction("contraindicated", "Disulfiram-like reaction", "No alcohol during treatment"),
    ("sertraline", "ibuprofen"): Interaction("moderate", "SSRIs+NSAIDs increase bleeding risk", "Use with caution"),
    ("sertraline", "warfarin"): Interaction("major", "SSRIs inhibit platelet aggregation", "Monitor INR"),
    ("diazepam", "alcohol"): Interaction("major", "Enhanced CNS depression", "Avoid alcohol"),
    ("metformin", "iodine_contrast"): Interaction("major", "Lactic acidosis risk", "Stop metformin 48h before contrast"),
    ("acetaminophen", "alcohol"): Interaction("moderate", "Hepatotoxicity risk", "Max 2g daily"),
    ("ibuprofen", "alcohol"): Interaction("moderate", "GI irritation", "Reduce alcohol intake"),
}

def check_drug_interaction(drug_a, drug_b):
    key = tuple(sorted([drug_a, drug_b]))
    return DRUG_INTERACTIONS.get(key)

def check_drug_in_context(drug, medications):
    results = []
    for med in medications:
        if med == drug:
            continue
        interaction = check_drug_interaction(drug, med)
        if interaction:
            results.append((med, interaction))
    return results

def get_all_known_drugs():
    drugs = set()
    for a, b in DRUG_INTERACTIONS:
        drugs.add(a)
        drugs.add(b)
    return sorted(drugs)
