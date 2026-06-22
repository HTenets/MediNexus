"""Emergency signal detection — keyword + regex + type classification."""

import re
import logging

logger = logging.getLogger(__name__)

# Emergency keywords grouped by type
EMERGENCY_KEYWORDS: dict[str, list[str]] = {
    "SUICIDE": ["suicide", "kill myself", "自杀", "不想活", "不想活了", "轻生"],
    "CARDIAC": ["chest pain", "胸痛", "chest tightness", "胸闷", "心绞痛"],
    "RESPIRATORY": ["difficulty breathing", "呼吸困难", "choking", "窒息"],
    "HEMORRHAGE": ["severe bleeding", "大出血", "出血不止"],
    "STROKE": ["stroke", "中风", "脑卒中", "face droop", "arm weakness"],
    "SHOCK": ["anaphylaxis", "过敏性休克", "shock", "休克"],
}

# Flat keyword set for fast lookup
EMERGENCY_KEYWORDS_FLAT = {kw.lower() for kws in EMERGENCY_KEYWORDS.values() for kw in kws}

# Urgent keywords (lower severity)
URGENT_KEYWORDS: list[str] = [
    "high fever", "高热", "fever 39", "39度", "severe pain", "剧痛",
    "vomiting", "呕吐", "persistent", "持续",
]

# Regex patterns for contextual detection
EMERGENCY_PATTERNS: list[re.Pattern] = [
    re.compile(r"不想活", re.IGNORECASE),
    re.compile(r"胸[口闷痛].*[出汗恶心]", re.IGNORECASE),
    re.compile(r"(heart\s*attack|myocardial|心梗)", re.IGNORECASE),
]


class EmergencyDetector:
    """Detects emergency signals in patient text."""

    async def check(self, text: str) -> tuple[bool, list[str], str]:
        """Check text for emergency signals. Returns (is_emergency, detected_keywords, emergency_type)."""
        text_lower = text.lower()
        detected: list[str] = []
        etype: str = ""

        # Check keywords
        for kw in EMERGENCY_KEYWORDS_FLAT:
            if kw in text_lower:
                detected.append(kw)

        # Check regex patterns
        for pattern in EMERGENCY_PATTERNS:
            if pattern.search(text):
                detected.append(pattern.pattern)

        # Determine emergency type
        if detected:
            for et, kws in EMERGENCY_KEYWORDS.items():
                for kw in kws:
                    if kw in text_lower:
                        etype = et
                        break
                if etype:
                    break
            if not etype:
                etype = "GENERAL_EMERGENCY"

        return len(detected) > 0, detected, etype

    async def check_urgent(self, text: str) -> tuple[bool, list[str]]:
        """Check for urgent (non-emergency but concerning) signals."""
        text_lower = text.lower()
        detected = [kw for kw in URGENT_KEYWORDS if kw in text_lower]
        return len(detected) > 0, detected

    @staticmethod
    def get_emergency_response(detected: list[str], etype: str) -> dict:
        """Generate emergency response info."""
        responses = {
            "SUICIDE": {
                "type": "emergency",
                "emergency_type": "SUICIDE",
                "message": "检测到自杀风险信号。请立即寻求心理危机干预。",
                "actions": [
                    "请立即拨打 24 小时心理援助热线: 010-82951332",
                    "或拨打全国希望 24 热线: 400-161-9995",
                    "保持患者身边有人陪伴",
                    "移除可能的危险物品",
                ],
            },
            "CARDIAC": {
                "type": "emergency",
                "emergency_type": "CARDIAC",
                "message": "检测到心脏急症信号。请立即就医。",
                "actions": [
                    "请立即拨打 120 急救电话",
                    "让患者保持静坐或半卧位",
                    "如有硝酸甘油可舌下含服",
                ],
            },
            "RESPIRATORY": {
                "type": "emergency",
                "emergency_type": "RESPIRATORY",
                "message": "检测到呼吸困难信号。需要紧急医疗干预。",
                "actions": [
                    "请立即拨打 120 急救电话",
                    "协助患者保持呼吸道通畅",
                    "让患者采取舒适的坐位",
                ],
            },
            "HEMORRHAGE": {
                "type": "emergency",
                "emergency_type": "HEMORRHAGE",
                "message": "检测到大出血信号。需要紧急止血处理。",
                "actions": [
                    "请立即拨打 120 急救电话",
                    "用干净纱布直接压迫止血",
                    "抬高出血部位",
                ],
            },
            "STROKE": {
                "type": "emergency",
                "emergency_type": "STROKE",
                "message": "检测到脑卒中信号。黄金抢救时间 4.5 小时。",
                "actions": [
                    "请立即拨打 120 急救电话",
                    "让患者平躺，头部稍微抬高",
                    "记录症状开始时间",
                ],
            },
        }

        response = responses.get(etype, {
            "type": "emergency",
            "emergency_type": etype or "GENERAL_EMERGENCY",
            "message": "检测到紧急情况信号。请立即就医。",
            "actions": ["请立即拨打 120 急救电话"],
        })
        response["detected"] = detected
        return response
