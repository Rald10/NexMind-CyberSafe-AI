
import time
import ipaddress
from urllib.parse import urlsplit

class EvidenceVerificationAgent:

    def __init__(self):
        self.name = "Evidence Verification Agent"

    def verify(self, detection_result):
        start = time.perf_counter()

        urls = detection_result.get("urls", [])
        findings = []

        for url in urls:
            warnings = []
            parsed = urlsplit(url)

            hostname = parsed.hostname or ""

            if parsed.scheme.lower() != "https":
                warnings.append("URL does not use HTTPS")

            if "@" in parsed.netloc:
                warnings.append(
                    "URL contains userinfo, which may hide the destination"
                )

            if not hostname:
                warnings.append("Missing or invalid hostname")

            try:
                address = ipaddress.ip_address(hostname)
                warnings.append("URL uses an IP address")
                if not address.is_global:
                    warnings.append(
                        "IP address is not globally routable"
                    )
            except ValueError:
                pass

            if hostname.startswith("xn--") or ".xn--" in hostname:
                warnings.append(
                    "Internationalized domain requires review"
                )

            findings.append({
                "url": url,
                "hostname": hostname,
                "warnings": warnings,
                "verification_status": "offline_checks_only",
                "reputation_checked": False
            })

        return {
            "agent": self.name,
            "findings": findings,
            "urls_checked": len(findings),
            "verification_complete": False,
            "execution_seconds": round(
                time.perf_counter() - start, 6
            )
        }
