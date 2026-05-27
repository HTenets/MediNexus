"""Emergency signal detection — keyword + semantic."""

EMERGENCY_KEYWORDS = {
    "suicide", "自杀", "kill myself", "chest pain", "胸痛",
    "difficulty breathing", "呼吸困难", "severe bleeding", "大出血",
}


class EmergencyDetector:
    def check(self, text: str) -> tuple[bool, list[str]]:
        detected = [kw for kw in EMERGENCY_KEYWORDS if kw in text.lower()]
        return len(detected) > 0, detected
