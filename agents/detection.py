
import re
import time

class ThreatDetectionAgent:

    def __init__(self):
        self.name = "Threat Detection Agent"
        from pathlib import Path
        import joblib

        model_path = (
            Path(__file__).resolve().parents[1]
            / "ml/models/phishing_hybrid_tfidf_logreg_step9g.joblib"
        )

        self.ml_model = joblib.load(model_path)


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


        # ML provides an additional signal, not a final verdict.
        probabilities = self.ml_model.predict_proba([message])[0]
        classes = list(self.ml_model.classes_)

        class_probabilities = {
            str(label): round(float(probability), 6)
            for label, probability in zip(classes, probabilities)
        }

        ml_prediction = self.ml_model.predict([message])[0]

        ml_confidence = max(float(p) for p in probabilities)

        result = {
            "agent": self.name,
            "ml_prediction": str(ml_prediction),
            "ml_confidence": round(ml_confidence, 6),
            "ml_class_probabilities": class_probabilities,
            "ml_advisory_only": True,
            "indicators": indicators,
            "urls": urls,
            "indicator_count": len(indicators),
            "requires_verification": bool(indicators or urls),
            "execution_seconds": round(
                time.perf_counter() - start, 6
            )
        }

        return result
