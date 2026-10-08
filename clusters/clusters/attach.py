"""Attached images and work-style text on a kanban task.

CodeAgentSwarm's first message carries attached images and work-style text.
The styles on the page are "Normal", "Ask only for blockers", and
"Use best judgment". The last two need a short instruction the operator
can read. This stores that on the task. It does not start work.

Refusals: a missing task is Refuse("TASK", task_id). A work_style outside
those three strings is Refuse("STYLE", work_style). "Normal" with any
style_text, or either other style without one line of 1..240 characters,
is Refuse("STYLE", "text"). A non-list of images, or more than eight, is
Refuse("STYLE", "images"). Each path passes clusters.refuse.guard_path,
and a live path raises LIVE_TREE.

Paths are not read and the files are not opened. The column is not moved
and the harness is not called.
"""

from __future__ import annotations

from clusters.refuse import Refuse, guard_path
from clusters.store import Store

WORK_STYLES = ("Normal", "Ask only for blockers", "Use best judgment")
_WITH_TEXT = WORK_STYLES[1:]
_IMAGE_CAP = 8
_TEXT_CAP = 240


def attach(
    store: Store,
    *,
    task_id: str,
    work_style: str,
    style_text: str = "",
    images: list[str] | None = None,
) -> dict:
    current = store.view("task").get(task_id)
    if current is None:
        raise Refuse("TASK", task_id)
    if not isinstance(work_style, str) or work_style not in WORK_STYLES:
        detail = work_style if isinstance(work_style, str) else "work_style"
        raise Refuse("STYLE", detail)
    text = _instruction(work_style, style_text)
    paths = _image_paths(images)
    body = {key: value for key, value in current.items() if not str(key).startswith("_")}
    body["op"] = "attach"
    body["work_style"] = work_style
    body["style_text"] = text
    body["images"] = paths
    store.append("task", body)
    return dict(store.view("task")[task_id])


def _instruction(work_style: str, style_text: str) -> str:
    if not isinstance(style_text, str):
        raise Refuse("STYLE", "text")
    if work_style == "Normal":
        if style_text != "":
            raise Refuse("STYLE", "text")
        return ""
    if work_style not in _WITH_TEXT:
        raise Refuse("STYLE", "text")
    if "\n" in style_text or "\r" in style_text or not 1 <= len(style_text) <= _TEXT_CAP:
        raise Refuse("STYLE", "text")
    return style_text


def _image_paths(images: list[str] | None) -> list[str]:
    if images is None:
        return []
    if not isinstance(images, list):
        raise Refuse("STYLE", "images")
    # guard_path checks the string only. Do not open the file or read its bytes.
    guarded = [guard_path(path) for path in images]
    if len(guarded) > _IMAGE_CAP:
        raise Refuse("STYLE", "images")
    return guarded
