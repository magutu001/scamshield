import re
import ssl
import socket
import whois
from datetime import datetime


def check_ssl(domain: str) -> bool:
    """Check if a domain has a valid SSL certificate."""
    try:
        clean = domain.replace("https://", "").replace("http://", "").split("/")[0]
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=clean) as s:
            s.settimeout(5)
            s.connect((clean, 443))
        return True
    except:
        return False


def check_domain(domain: str) -> dict:
    """Verify domain via SSL check and WHOIS lookup."""
    result = {"ssl_valid": False, "domain_age": -1, "whois_info": "Unavailable"}
    if not domain:
        return result
    try:
        clean = domain.replace("https://", "").replace("http://", "").split("/")[0].lower()

        # SSL check
        result["ssl_valid"] = check_ssl(domain)

        # WHOIS lookup
        try:
            w = whois.whois(clean)
            creation = w.creation_date

            # whois sometimes returns a list — take the earliest
            if isinstance(creation, list):
                creation = sorted([d for d in creation if d is not None])[0]

            if creation:
                # Strip timezone info to allow naive datetime comparison
                if hasattr(creation, "tzinfo") and creation.tzinfo is not None:
                    creation = creation.replace(tzinfo=None)
                age_days = (datetime.now() - creation).days
                result["domain_age"] = max(0, age_days // 365)
                registrar = w.registrar or "Unknown"
                result["whois_info"] = f"Registrar: {registrar} | Created: {str(creation)[:10]}"
            else:
                result["whois_info"] = "WHOIS returned no creation date"

        except Exception as e:
            result["whois_info"] = f"WHOIS lookup failed: {str(e)[:80]}"

    except Exception as e:
        result["whois_info"] = f"Domain check error: {str(e)[:80]}"

    return result


def analyze_text(text: str, rules: list) -> dict:
    """Match text against all active regex rules and accumulate a score."""
    flags, score = [], 0
    for r in rules:
        if r["active_flag"] and re.search(r["pattern"], text):
            flags.append({
                "rule": r["name"],
                "category": r["category"],
                "weight": r["weight"]
            })
            score += r["weight"]
    return {"score": score, "flags": flags}


def calculate_verdict(text_score: int, domain_info: dict) -> dict:
    """Combine text score and domain checks into a final verdict."""
    total        = text_score
    domain_flags = []

    if domain_info.get("domain_age", -1) == 0:
        total += 30
        domain_flags.append({
            "rule": "Newly registered domain (< 1 year)",
            "category": "domain", "weight": 30
        })
    elif domain_info.get("domain_age", -1) == -1:
        total += 15
        domain_flags.append({
            "rule": "Domain age unknown",
            "category": "domain", "weight": 15
        })

    if not domain_info.get("ssl_valid", True):
        total += 20
        domain_flags.append({
            "rule": "No valid SSL certificate",
            "category": "ssl", "weight": 20
        })

    if total >= 60:
        v, c, e, a = (
            "HIGH RISK", "red", "🚨",
            "This job ad shows multiple strong scam indicators. "
            "Do NOT share personal info or send money."
        )
    elif total >= 30:
        v, c, e, a = (
            "NEEDS CAUTION", "orange", "⚠️",
            "Some suspicious characteristics found. "
            "Verify the employer independently before proceeding."
        )
    else:
        v, c, e, a = (
            "LIKELY SAFE", "green", "✅",
            "No major scam indicators detected. "
            "Always verify employers through official channels."
        )

    return {
        "total_score":  total,
        "verdict":      v,
        "color":        c,
        "emoji":        e,
        "advice":       a,
        "domain_flags": domain_flags
    }
