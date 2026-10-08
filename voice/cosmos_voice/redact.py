"""Strip secret-shaped spans before they reach a log or an error detail."""

from __future__ import annotations

import re

# Forms the contract names: bearer tokens, sk-, sk-ant-, xai-, api_key=, token=, AKIA.
# AKIA stays case-sensitive. The other forms do not, so a shifted case still cannot leak.
_SECRET: re.Pattern[str] = re.compile(
    r"(?i:(?<![A-Za-z0-9])bearer\s+\S+"
    r"|(?<![A-Za-z0-9])sk-ant-\S*"
    r"|(?<![A-Za-z0-9])sk-\S*"
    r"|(?<![A-Za-z0-9])xai-\S*"
    r"|(?<![A-Za-z0-9])api_key\s*=\s*\S*"
    r"|(?<![A-Za-z0-9])token\s*=\s*\S*)"
    r"|\bAKIA[0-9A-Z]*\b"
)


def secret_shape(text: str) -> bool:
    """Return True when ``text`` contains a bearer, key, or secret assignment."""
    return _SECRET.search(text) is not None


def redact(text: str) -> str:
    """Replace secret-shaped spans with ``[REDACTED]``. Other text is unchanged."""
    if text == "":
        return ""
    return _SECRET.sub("[REDACTED]", text)
