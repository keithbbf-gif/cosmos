"""Utility skill: insert a payload at a 1-based line in source without touching git.

Not a general AST rewrite. Line splice only. Caller verifies syntax (compile / parser).
"""
from __future__ import annotations


def apply_ast_patch(source_code: str, target_line: int, patch_payload: str) -> str:
    if not source_code or patch_payload is None:
        raise ValueError("Invalid AST patch arguments")
    if target_line < 1:
        raise ValueError("target_line is 1-based")
    lines = source_code.split("\n")
    idx = min(target_line - 1, len(lines))
    lines[idx:idx] = patch_payload.split("\n")
    return "\n".join(lines)


if __name__ == "__main__":
    import pathlib
    import sys

    if len(sys.argv) != 4:
        sys.stderr.write("usage: apply_ast_patch.py FILE LINE PAYLOAD_FILE\n")
        raise SystemExit(2)
    src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    line = int(sys.argv[2])
    payload = pathlib.Path(sys.argv[3]).read_text(encoding="utf-8")
    sys.stdout.write(apply_ast_patch(src, line, payload))
