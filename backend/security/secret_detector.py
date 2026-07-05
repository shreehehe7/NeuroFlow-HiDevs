import re
import logging

logger = logging.getLogger(__name__)

SECRET_PATTERNS = {
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "generic_api_key": r"""['"]?(?:api|secret|token|key|password)['"]?\s*[:=]\s*['"][A-Za-z0-9/+]{20,}['"]""",
    "jwt": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"
}

def detect_and_redact_secrets(text: str) -> str:
    redacted_text = text
    for key, pattern in SECRET_PATTERNS.items():
        matches = re.finditer(pattern, redacted_text)
        for match in matches:
            logger.warning({"event": "secret_redacted", "pattern_type": key})
            redacted_text = redacted_text.replace(match.group(0), "[REDACTED]")
    return redacted_text
