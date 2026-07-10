"""
target_security.py

Regex/keyword-based prompt injection detection. Exposes
PromptSecurity.detect_injection(text) -> bool, compatible with
redteam_cli's LocalFunctionAdapter.

_StubLogger and SecurityValidator below are minimal substitutes for the
original application's logging and PII-detection dependencies, included
so this module runs standalone for security testing.
"""

import re


class _StubLogger:
    def warning(self, msg, **kwargs):
        pass


class SecurityValidator:
    def detect_pii(self, text: str) -> dict:
        return {}


logger = _StubLogger()


class PromptSecurity:
    """
    Security utilities for AI prompt processing and injection detection.
    """

    # Patterns that might indicate prompt injection attempts
    INJECTION_PATTERNS = [
        re.compile(r'ignore\s+(?:previous\s+)?instructions?', re.IGNORECASE),
        re.compile(r'forget\s+everything', re.IGNORECASE),
        re.compile(r'act\s+as\s+(?:a\s+)?different', re.IGNORECASE),
        re.compile(r'pretend\s+(?:to\s+be|you\s+are)', re.IGNORECASE),
        re.compile(r'system\s*:', re.IGNORECASE),
        re.compile(r'<\s*script\s*>', re.IGNORECASE),
        re.compile(r'javascript\s*:', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'exec\s*\(', re.IGNORECASE),
    ]

    @staticmethod
    def detect_injection(text: str) -> bool:
        """
        Detect potential prompt injection attempts.

        Args:
            text: Input text to analyze

        Returns:
            True if potential injection detected
        """
        if not text:
            return False

        text_lower = text.lower()

        # Check for injection patterns
        for pattern in PromptSecurity.INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning("Potential prompt injection detected", pattern=pattern.pattern)
                return True

        # Check for suspicious character sequences
        if len(text) > 10000:  # Unusually long input
            logger.warning("Suspicious long input detected", length=len(text))
            return True

        # Check for excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            logger.warning("High special character ratio", ratio=special_char_ratio)
            return True

        return False