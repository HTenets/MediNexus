"""Dynamic skill loader."""


def load_skills() -> dict[str, type]:
    from agents.doctor.skills.builtin.internal_medicine.skill import InternalMedicineSkill
    from agents.doctor.skills.builtin.dermatology.skill import DermatologySkill
    from agents.doctor.skills.builtin.ent.skill import ENTSkill
    from agents.doctor.skills.builtin.mental_health.skill import MentalHealthSkill

    skills = {}
    for cls in [InternalMedicineSkill, DermatologySkill, ENTSkill, MentalHealthSkill]:
        instance = cls()
        skills[instance.name] = instance
    return skills
