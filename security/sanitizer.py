"""
PII & Secret Sanitizer.
Scrubs sensitive tokens, passwords, and API keys from logs and payloads.
"""

import re
from typing import Any, Dict, List, Union

class Sanitizer:
    """Sanitizes text and nested dictionaries to prevent accidental credential leakage."""

    BEARER_PATTERN = re.compile(r"Bearer\s+([a-zA-Z0-9_\-\.]{15,})", re.IGNORECASE)
    API_KEY_PATTERN = re.compile(r"(key=|api_key=|secret=)([a-zA-Z0-9_\-]{15,})", re.IGNORECASE)
    SENSITIVE_KEYS = {"password", "secret", "token", "access_token", "refresh_token", "client_secret", "api_key"}

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        if not isinstance(text, str):
            return text
        sanitized = cls.BEARER_PATTERN.sub("Bearer [REDACTED_TOKEN]", text)
        sanitized = cls.API_KEY_PATTERN.sub(r"\1[REDACTED_SECRET]", sanitized)
        return sanitized

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return data
        clean_dict = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(sens in k_lower for sens in cls.SENSITIVE_KEYS):
                clean_dict[k] = "[REDACTED]"
            elif isinstance(v, dict):
                clean_dict[k] = cls.sanitize_dict(v)
            elif isinstance(v, list):
                clean_dict[k] = [cls.sanitize_dict(item) if isinstance(item, dict) else cls.sanitize_text(str(item)) for item in v]
            elif isinstance(v, str):
                clean_dict[k] = cls.sanitize_text(v)
            else:
                clean_dict[k] = v
        return clean_dict
