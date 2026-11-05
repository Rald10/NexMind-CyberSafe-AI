
import re


THREAT_PATTERNS = {
    "bank_fraud": [
        r"\bbvn\b",
        r"\bbank account\b",
        r"\baccount (blocked|suspended|restricted)\b",
        r"\bdebit card\b",
        r"\batm card\b",
    ],
    "credential_theft": [
        r"\botp\b",
        r"\bone.time (password|code)\b",
        r"\bverification code\b",
        r"\bpassword\b",
        r"\bpin\b",
        r"\blogin details\b",
    ],
    "fake_job": [
        r"\bjob offer\b",
        r"\brecruitment fee\b",
        r"\bprocessing fee\b",
        r"\bemployment letter\b",
        r"\bjob vacancy\b",
    ],
    "investment_scam": [
        r"\binvestment\b",
        r"\bdouble your money\b",
        r"\bguaranteed returns?\b",
        r"\bcrypto\b",
        r"\bforex\b",
    ],
    "grant_scam": [
        r"\bgovernment grant\b",
        r"\bgrant application\b",
        r"\bfree grant\b",
        r"\bclaim your prize\b",
        r"\byou (have )?won\b",
    ],
    "account_takeover": [
        r"\baccount hacked\b",
        r"\bunauthorized login\b",
        r"\bsuspicious login\b",
        r"\breset your password\b",
    ],
}


THREAT_ADVICE = {
    "bank_fraud": [
        "Do not send money or banking details in response to this message.",
        "Open your bank's official app or contact its verified customer support independently.",
    ],
    "credential_theft": [
        "Never share OTPs, PINs, passwords, or verification codes.",
        "If you already shared a credential, change it through the official service and contact the provider immediately.",
    ],
    "fake_job": [
        "Do not pay recruitment or processing fees based only on this message.",
        "Check the vacancy on the employer's official careers page and verify the recruiter's identity.",
    ],
    "investment_scam": [
        "Do not transfer money based on promises of guaranteed profits.",
        "Independently verify the investment provider and relevant regulatory registration before proceeding.",
    ],
    "grant_scam": [
        "Do not pay a fee to release an unexpected prize or grant.",
        "Verify the programme using an independently located official government or organization website.",
    ],
    "account_takeover": [
        "Open the official service directly and review recent account activity.",
        "Change affected passwords, enable two-factor authentication, and revoke unfamiliar sessions.",
    ],
}


def generate_recommendations(message, detection_result, verification_result):
    """
    Produce context-specific safety recommendations.

    Pattern matches are warning signals, not proof of fraud.
    This function does not access external websites.
    """

    if not isinstance(message, str):
        message = ""

    indicators = set(detection_result.get("indicators", []))
    findings = verification_result.get("findings", [])

    categories = []

    for category, patterns in THREAT_PATTERNS.items():
        if any(
            re.search(pattern, message, flags=re.IGNORECASE)
            for pattern in patterns
        ):
            categories.append(category)

    recommendations = []

    for category in categories:
        recommendations.extend(THREAT_ADVICE[category])

    if findings:
        recommendations.append(
            "Do not open unfamiliar links. Navigate to the organization's official website manually."
        )

    if "urgency" in indicators:
        recommendations.append(
            "Do not act under pressure. Independently verify deadlines or threats before responding."
        )

    if "financial_lure" in indicators and not categories:
        recommendations.append(
            "Verify unexpected rewards or offers before sharing information or making payments."
        )

    if "suspicious_action" in indicators and not findings:
        recommendations.append(
            "Do not follow unexpected instructions until the sender and request are independently verified."
        )

    if not recommendations:
        recommendations = [
            "No matching high-risk patterns were identified by the current rules.",
            "This does not establish that the message is safe. Verify unexpected requests independently.",
        ]

    # Remove duplicates while preserving order.
    recommendations = list(dict.fromkeys(recommendations))

    return {
        "categories": categories,
        "recommendations": recommendations[:6],
        "external_verification_complete": False,
    }
