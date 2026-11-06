
import re
import time


from urllib.parse import urlsplit

def detect_risky_instruction(message):
    action_patterns = [
        r"\b(?:visit|open|go to)\s+(?:\[)?https?://",
        r"\b(?:enter|submit|provide|share|send)\s+your\s+"
        r"(?:password|pin|otp)\b"
    ]

    negation_pattern = re.compile(
        r"\b(?:never|do not|don't|must not|should not|"
        r"avoid|refrain from)\s+"
        r"(?:(?:\w+)\s+){0,3}?",
        flags=re.IGNORECASE
    )

    for pattern in action_patterns:
        for match in re.finditer(
            pattern, message, flags=re.IGNORECASE
        ):
            prefix = message[
                max(0, match.start() - 65):match.start()
            ]
            prefix = re.split(r"[.!?\n;]", prefix)[-1]

            negations = list(
                negation_pattern.finditer(prefix)
            )

            if negations:
                last = negations[-1]
                intervening = prefix[last.end():]

                if len(intervening.split()) <= 3:
                    continue

            return True

    return False


def extract_clean_urls(message):
    normalized = re.sub(
        r"\[[^\]]+\]\((https?://[^)\s]+)\)",
        r"\1",
        message,
        flags=re.IGNORECASE
    )

    raw_urls = re.findall(
        r"""https?://[^\s<>'"\])]+""",
        normalized,
        flags=re.IGNORECASE
    )

    urls = []

    for url in raw_urls:
        url = url.rstrip(".,;!?")
        parsed = urlsplit(url)

        if (
            parsed.scheme.lower() in ("http", "https")
            and parsed.hostname
            and url not in urls
        ):
            urls.append(url)

    return urls



def detect_sensitive_context(message):
    credential_pattern = re.compile(
        r"\b(?:password|passwords|otp|otps|pin|pins|"
        r"bvn|bank details|verification code|"
        r"verification codes)\b",
        re.IGNORECASE
    )

    safety_advice_pattern = re.compile(
        r"\b(?:never|do not|don't|must not|should not|"
        r"avoid|refrain from)\s+"
        r"(?:\w+\s+){0,3}?"
        r"(?:enter|share|send|submit|provide|disclose)\b",
        re.IGNORECASE
    )

    if not isinstance(message, str):
        return False

    if not credential_pattern.search(message):
        return False

    sentences = re.split(r"[.!?\n;]+", message)

    for sentence in sentences:
        if not credential_pattern.search(sentence):
            continue

        if detect_risky_instruction(sentence):
            return True

        if safety_advice_pattern.search(sentence):
            continue

        return True

    return False


def refined_detection_context_v2(message):

    credential_terms = re.compile(
        r"\b(?:passwords?|otps?|pins?|bvn|"
        r"bank details|verification codes?)\b",
        re.I
    )

    credential_request = re.compile(
        r"\b(?:enter|submit|provide|share|send|disclose)"
        r"\s+(?:your|the|my)?\s*"
        r"(?:password|otp|pin|bvn|bank details|"
        r"verification code)\b",
        re.I
    )

    safety_negation = re.compile(
        r"\b(?:never|do not|don't|must not|should not|"
        r"avoid|refrain from)\s+"
        r"(?:\w+\s+){0,3}"
        r"(?:enter|submit|provide|share|send|disclose)\b",
        re.I
    )

    education_intro = re.compile(
        r"\b(?:phishing message says|"
        r"phishing example|example of phishing|"
        r"scam message says|security awareness|"
        r"common phishing message says)\b",
        re.I
    )

    if not isinstance(message, str):
        return {
            "sensitive_information": False,
            "suspicious_action": False
        }

    # Remove quoted examples only when explicitly
    # introduced as educational material.
    working = message

    if education_intro.search(message):
        working = re.sub(
            r"""['"][^'"]+['"]""",
            " ",
            working
        )

    # Preserve URLs while splitting on sentence
    # punctuation followed by whitespace.
    sentences = re.split(
        r"(?<=[.!?])\s+|\n+|;",
        working
    )

    sensitive = False
    suspicious = False

    for sentence in sentences:
        if not credential_terms.search(sentence):
            continue

        # A direct credential request takes priority
        # unless it is explicitly negated.
        request_matches = list(
            credential_request.finditer(sentence)
        )

        for match in request_matches:
            prefix = sentence[
                max(0, match.start() - 45):match.start()
            ]

            negated = bool(
                re.search(
                    r"\b(?:never|do not|don't|"
                    r"must not|should not|avoid)"
                    r"\s*$",
                    prefix,
                    re.I
                )
            )

            if not negated:
                sensitive = True
                suspicious = True

        if suspicious:
            continue

        # Explicit safety instructions are benign
        # unless another request is detected.
        if safety_negation.search(sentence):
            continue

        # Conditional password reset information
        # without credential submission is not
        # automatically suspicious.
        if re.search(
            r"\bif you requested a password reset\b",
            sentence,
            re.I
        ):
            continue

        sensitive = True

    return {
        "sensitive_information": sensitive,
        "suspicious_action": suspicious
    }



def detect_contextual_urgency(message):
    if not isinstance(message, str):
        return False

    urgency_patterns = [
        r"\bimmediately\b",
        r"\burgent\b",
        r"\bwithin \d+ (minutes?|hours?)\b",
        r"\baccount (will be )?(blocked|suspended)\b"
    ]

    educational_intro = re.compile(
        r"\b(?:"
        r"(?:common )?phishing message says|"
        r"phishing example|example of phishing|"
        r"scam message says|security awareness"
        r")\b",
        re.I
    )

    working = message

    if educational_intro.search(message):
        working = re.sub(
            r"""['"][^'"]+['"]""",
            " ",
            working
        )

    return any(
        re.search(pattern, working, re.I)
        for pattern in urgency_patterns
    )


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
                    if (category != "sensitive_information" or refined_detection_context_v2(message)["sensitive_information"]) and (category != "urgency" or detect_contextual_urgency(message)):
                        indicators.append(category)
                    break

        urls = extract_clean_urls(message)

        if refined_detection_context_v2(message)["suspicious_action"]:
            indicators.append("suspicious_action")

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
