"""Approved HERO seats. Windows are the numbers written on the DUD cards.

SOL's pin is the one the Codex mouth was asked for (gpt-5.4). Its window is
the OpenAI coder card (272000), not a separate SOL measurement.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Agent:
    id: str
    role: str
    model: str
    native_door: str
    window: int
    what: str
    note: str


AGENTS: dict[str, Agent] = {
    "luna": Agent(
        "luna", "JUDGE", "openai/gpt-5.6-luna:floor", "codex",
        1_100_000, "text", "hero_luna DUD. Native door is Codex, not OpenRouter chat.",
    ),
    "sol": Agent(
        "sol", "CODER", "gpt-5.4", "codex",
        272_000, "python",
        "Native door is Codex. The same agent seats on cosmos-code without codex exec.",
    ),
    "mini": Agent(
        "mini", "CODER", "gpt-5.4-mini", "codex",
        272_000, "python", "CODER 4. hero_coders/4_54mini.",
    ),
    "glm": Agent(
        "glm", "CODER", "glm-5.3-flash", "pi",
        1_000_000, "python", "CODER 1. Native door is pi -p, not the chat rail.",
    ),
    "gf38": Agent(
        "gf38", "CODER", "gemini-3.8-flash", "vertex",
        1_048_576, "python", "CODER 2. Native door is Vertex. No tools array.",
    ),
    "deepseek": Agent(
        "deepseek", "CODER", "deepseek-v4-flash", "dsh",
        1_000_000, "python", "CODER 3. Native door is dsh. A missing key is not a chat call.",
    ),
    "ling": Agent(
        "ling", "CODER", "inclusionai/ling-3.0-flash", "opencode",
        262_144, "python", "CODER 5. Native door is opencode.",
    ),
    "grok": Agent(
        "grok", "CODER", "grok-4.6", "grok",
        2_000_000, "python", "CODER 6. Do not start grok.exe. Cosmos-code is the coding seat.",
    ),
}
