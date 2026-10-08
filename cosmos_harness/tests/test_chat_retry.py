"""ChatSample shape retries. No network."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"V:\streams\cosmos_code\attempts\cheap-seat")))

from run_cheap import ChatSample  # noqa: E402


class Scripted(ChatSample):
    def __init__(self, dest: Path, replies: list[tuple[int, dict[str, object]]]) -> None:
        super().__init__("sk-testsecret", "pin/under-test", dest)
        self.replies = list(replies)
        self.bodies: list[dict[str, object]] = []

    def _post(self, body: dict[str, object]) -> tuple[int, dict[str, object]]:
        self.bodies.append(json.loads(json.dumps(body)))
        return self.replies.pop(0)


def test_tool_404_then_multiturn_collapses_to_one_user_message(tmp_path: Path) -> None:
    sample = Scripted(tmp_path, [
        (404, {"error": {"message": "No endpoints found that support tool use", "code": 404}}),
        (400, {"error": {"message": "Multi-turn conversations are not supported", "code": 400}}),
        (200, {
            "model": "relace/relace-apply-3",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "DROP\nThe file should return 2."},
            }],
            "usage": {"cost": 0},
        }),
    ])
    out = sample.sample(("role = JUDGE", "Grade bug.py. Do not call a tool."))
    assert out.text.startswith("DROP")
    assert len(sample.bodies) == 3
    last = sample.bodies[-1]
    messages = last["messages"]
    assert isinstance(messages, list)
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "tools" not in last
    assert "tool_choice" not in last
    assert sample.http == [200]


def test_empty_length_retries_once_without_reasoning(tmp_path: Path) -> None:
    sample = Scripted(tmp_path, [
        (200, {
            "model": "qwen/qwen3.5-35b-a3b",
            "choices": [{
                "finish_reason": "length",
                "message": {"role": "assistant", "content": None, "reasoning": "Thinking about DROP"},
            }],
            "usage": {"cost": 0.001},
        }),
        (200, {
            "model": "qwen/qwen3.5-35b-a3b",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "DROP\nThe file should return 2."},
            }],
            "usage": {"cost": 0.0001},
        }),
    ])
    out = sample.sample(("role = JUDGE", "Grade bug.py. Do not call a tool."))
    assert out.text.startswith("DROP")
    assert len(sample.bodies) == 2
    assert "reasoning" not in sample.bodies[1]
    assert sample.bodies[1]["max_tokens"] == 400
    assert sample.http == [200]
    assert (tmp_path / "turn-1-length.json").is_file()
    assert sum(float(row["cost"]) for row in sample.usage) == 0.0011


def test_function_calling_400_drops_tools(tmp_path: Path) -> None:
    sample = Scripted(tmp_path, [
        (400, {
            "error": {
                "message": "Provider returned error",
                "code": 400,
                "metadata": {"raw": "model features function calling not support"},
            },
        }),
        (200, {
            "model": "sao10k/l3.1-euryale-70b",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "DROP\nThe file should return 2."},
            }],
        }),
    ])
    out = sample.sample(("role = JUDGE", "Grade bug.py. Do not call a tool."))
    assert out.text.startswith("DROP")
    assert len(sample.bodies) == 2
    assert "tools" not in sample.bodies[1]
    assert "tool_choice" not in sample.bodies[1]
    assert sample.http == [200]


def test_a_normal_verdict_is_not_retried(tmp_path: Path) -> None:
    sample = Scripted(tmp_path, [
        (200, {
            "model": "pin/under-test",
            "choices": [{
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "DROP\nThe file should return 2."},
            }],
        }),
    ])
    out = sample.sample(("role = JUDGE", "Grade bug.py. Do not call a tool."))
    assert out.text.startswith("DROP")
    assert len(sample.bodies) == 1
    assert sample.bodies[0]["max_tokens"] == 2000
