
import re
import time

class ThreatDetectionAgent:

    def __init__(self):
        self.name = "Threat Detection Agent"

        self.patterns = {
            "urgency": [
                r"\bimmediately\b",
                r"\burgent\b",
                r"\bwithin \d+ (minutes?|hours?)\b",
                r"\baccount (will be )?(blocked|suspended)\b"
            ],
            "financial_lure": [
                r"\bcongratulations\b",
                r"\byou (have )?won\b",
                r"\bclaim your (prize|reward)\b",
                r"\bfree money\b"
            ],
            "sensitive_information": [
                r"\botp\b",
                r"\bbvn\b",
                r"\bpin\b",
                r"\bpassword\b",
                r"\bbank details\b"
            ],
            "suspicious_action": [
                r"\bclick (this |the )?link\b",
                r"\bverify your account\b",
                r"\bsend your details\b"
            ]
        }

    def analyze(self, message):
        start = time.perf_counter()

        if not isinstance(message, str):
            raise TypeError("Message must be a string")

        if not message.strip():
            raise ValueError("Message cannot be empty")

        indicators = []

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    indicators.append(category)
                    break

        urls = re.findall(
            r'https?://[^\s<>"\']+',
            message,
            flags=re.IGNORECASE
        )

        indicators = sorted(set(indicators))

        result = {
            "agent": self.name,
            "indicators": indicators,
            "urls": urls,
            "indicator_count": len(indicators),
            "requires_verification": bool(indicators or urls),
            "execution_seconds": round(
                time.perf_counter() - start, 6
            )
        }

        return result
