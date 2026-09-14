# -*- coding: utf-8 -*-
"""Minimal markdown → HTML for WXR content:encoded (no third-party deps)."""
from __future__ import annotations

import html
import re

_BLOCK_CODE = re.compile(r"```(?:\w*\n)?(.*?)```", re.DOTALL)
_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_INLINE_CODE = re.compile(r"`([^`]+)`")


def _inline(md: str) -> str:
    text = html.escape(md)
    text = _INLINE_CODE.sub(r"<code>\1</code>", text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)

    def link_sub(m: re.Match[str]) -> str:
        label = html.escape(m.group(1))
        href = html.escape(m.group(2), quote=True)
        return f'<a href="{href}">{label}</a>'

    text = _LINK.sub(link_sub, text)

    def img_sub(m: re.Match[str]) -> str:
        alt = html.escape(m.group(1))
        src = html.escape(m.group(2), quote=True)
        return f'<img src="{src}" alt="{alt}" />'

    text = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
        lambda m: (
            f'<img src="{html.escape(m.group(2), quote=True)}" '
            f'alt="{html.escape(m.group(1))}" />'
        ),
        text,
    )
    return text


def markdown_to_html(md: str) -> str:
    if not md.strip():
        return ""

    work = md.replace("\r\n", "\n")
    blocks: list[str] = []

    def code_repl(m: re.Match[str]) -> str:
        idx = len(blocks)
        code = html.escape(m.group(1).strip("\n"))
        blocks.append(f"<pre><code>{code}</code></pre>")
        return f"\x00CODE{idx}\x00"

    work = _BLOCK_CODE.sub(code_repl, work)
    work = _HEADING.sub(
        lambda m: f"\x00H{len(m.group(1))}\x00{_inline(m.group(2).strip())}\x00/H\x00",
        work,
    )

    parts: list[str] = []
    para_buf: list[str] = []

    def flush_para() -> None:
        if not para_buf:
            return
        joined = " ".join(s.strip() for s in para_buf if s.strip())
        if joined:
            parts.append(f"<p>{_inline(joined)}</p>")
        para_buf.clear()

    for line in work.split("\n"):
        stripped = line.strip()
        if not stripped:
            flush_para()
            continue
        if stripped.startswith("\x00H") and "\x00/H\x00" in stripped:
            flush_para()
            m = re.match(r"\x00H(\d)\x00(.+)\x00/H\x00", stripped)
            if m:
                level = m.group(1)
                parts.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            items = [re.sub(r"^[-*]\s+", "", stripped)]
            parts.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
            continue
        if "\x00CODE" in stripped:
            flush_para()
            for m in re.finditer(r"\x00CODE(\d+)\x00", stripped):
                parts.append(blocks[int(m.group(1))])
            continue
        para_buf.append(stripped)

    flush_para()
    html_out = "\n".join(parts)
    for i, block in enumerate(blocks):
        html_out = html_out.replace(f"\x00CODE{i}\x00", block)
    return html_out
