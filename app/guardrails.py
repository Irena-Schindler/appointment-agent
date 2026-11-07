"""Input/output guardrails: prompt-injection heuristics, PII redaction for logs."""
import re

INJECTION_PATTERNS = [
    r"ignore (all|any|the)? ?(previous|prior|above) (instructions|rules)",
    r"ignoriere (alle|die)? ?(vorherigen|bisherigen) (anweisungen|regeln)",
    r"you are now",
    r"system prompt",
    r"reveal (your|the) (prompt|instructions)",
    r"</?(system|assistant|tool)>",
]
_inj = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)
_phone = re.compile(r"\+?\d[\d ]{5,}\d")
_email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def looks_like_injection(text: str) -> bool:
    return bool(_inj.search(text))


def redact(text: str) -> str:
    """Remove phone numbers and e-mail addresses before anything is logged."""
    return _email.sub("[email]", _phone.sub("[phone]", text))


def sanitize_tool_output(text: str) -> str:
    """Tool output is data, never instructions: neutralise anything that looks like a command."""
    if looks_like_injection(text):
        return "[tool output withheld: possible injected instructions]"
    return text
