"""Tests for Review Agent rules — drug interactions + contraindications."""

from agents.review.rules.drug_interaction import (
    check_drug_interaction, check_drug_in_context, get_all_known_drugs,
)
from agents.review.rules.contraindication import (
    check_contraindication, check_allergy, check_age_restriction,
    check_all_contraindications,
)


class TestDrugInteraction:
    def test_known_interaction(self):
        r = check_drug_interaction("aspirin", "warfarin")
        assert r is not None and r.severity == "major"

    def test_no_interaction(self):
        assert check_drug_interaction("aspirin", "acetaminophen") is None

    def test_order_independent(self):
        r1 = check_drug_interaction("aspirin", "ibuprofen")
        r2 = check_drug_interaction("ibuprofen", "aspirin")
        assert r1 is not None and r2 is not None
        assert r1.severity == r2.severity

    def test_contraindicated_level(self):
        r = check_drug_interaction("atorvastatin", "clarithromycin")
        assert r is not None and r.severity == "contraindicated"

    def test_check_in_context(self):
        results = check_drug_in_context("warfarin", ["aspirin", "ibuprofen", "acetaminophen"])
        assert len(results) >= 1

    def test_get_all_known_drugs(self):
        drugs = get_all_known_drugs()
        assert "aspirin" in drugs and "warfarin" in drugs and len(drugs) > 5


class TestContraindication:
    def test_buprofen_ulcer(self):
        r = check_contraindication("ibuprofen", "peptic_ulcer")
        assert r is not None

    def test_metformin_kidney(self):
        r = check_contraindication("metformin", "renal_insufficiency")
        assert r is not None and r.risk == "contraindicated"

    def test_no_contraindication(self):
        assert check_contraindication("acetaminophen", "peptic_ulcer") is None


class TestAllergyCheck:
    def test_penicillin_allergy(self):
        r = check_allergy("amoxicillin", "penicillin_allergy")
        assert r is not None and r.risk == "contraindicated"

    def test_no_allergy(self):
        assert check_allergy("acetaminophen", "penicillin_allergy") is None


class TestAgeRestriction:
    def test_aspirin_child(self):
        r = check_age_restriction("aspirin", "children")
        assert r is not None


class TestComprehensiveCheck:
    def test_multiple_findings(self):
        findings = check_all_contraindications("ibuprofen", ["peptic_ulcer"], ["aspirin_allergy"], "adult")
        assert len(findings) >= 2

    def test_empty_findings(self):
        assert check_all_contraindications("acetaminophen", ["hypertension"], [], "") == []
