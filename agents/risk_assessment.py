from agents.recommendations import generate_recommendations

import time

class RiskAssessmentAgent:

    def __init__(self):
        self.name = "Risk Assessment and Response Agent"

    def assess(self, detection_result, verification_result, message=''):
        start = time.perf_counter()

        indicators = detection_result.get("indicators", [])
        findings = verification_result.get("findings", [])

        # Preliminary heuristic score, not a calibrated probability
        weights = {
            "urgency": 20,
            "financial_lure": 20,
            "sensitive_information": 35,
            "suspicious_action": 25
        }

        score = sum(
            weights.get(indicator, 0)
            for indicator in set(indicators)
        )

        warning_count = sum(
            len(finding.get("warnings", []))
            for finding in findings
        )

        score += min(warning_count * 10, 20)
        score = min(score, 100)

        if score >= 60:
            risk_level = "HIGH"
        elif score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        reasons = []

        descriptions = {
            "urgency": "Message uses urgency or pressure",
            "financial_lure": "Message contains a financial lure",
            "sensitive_information":
                "Message mentions sensitive credentials or information",
            "suspicious_action":
                "Message encourages a potentially risky action"
        }

        for indicator in sorted(set(indicators)):
            reasons.append(
                descriptions.get(indicator, indicator)
            )

        for finding in findings:
            reasons.extend(finding.get("warnings", []))


        recommendation_result = generate_recommendations(
            message,
            detection_result,
            verification_result
        )

        recommendations = recommendation_result["recommendations"]

        if risk_level == "HIGH":
            recommendations.append(
                "Treat this message as potentially fraudulent "
                "until independently verified."
            )

        verification_complete = verification_result.get(
            "verification_complete", False
        )

        return {
            "agent": self.name,
            "risk_level": risk_level,
            "heuristic_score": score,
            "score_type": "rule_based_not_probability",
            "reasons": reasons,
            "recommendations": recommendations,
            "threat_categories": recommendation_result["categories"],
            "external_verification_complete": verification_complete,
            "assessment_note": (
                "Preliminary assessment only. "
                "This score is not a probability of fraud. "
                "A low score does not establish safety."
            ),
            "execution_seconds": round(
                time.perf_counter() - start, 6
            )
        }
