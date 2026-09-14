#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pin semantic/SEO contracts for cosmos/sites Eleventy shells.

Runs a production build when Node is available, then asserts landmarks,
Open Graph tags, ProfessionalService JSON-LD, and absence of PHI-style forms.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITES = REPO / "cosmos" / "sites"
SITE_OUT = (
    ("slpwow", SITES / "slpwow" / "_site" / "index.html"),
    ("therapy", SITES / "therapy" / "_site" / "index.html"),
)
ARTICLE_OUT = SITES / "slpwow" / "_site" / "articles" / "early-language-milestones" / "index.html"

REQUIRED_LANDMARKS = (
    'id="main"',
    'role="banner"',
    'aria-label="Primary"',
    'role="contentinfo"',
    "Skip to main content",
)
REQUIRED_META = (
    'property="og:title"',
    'property="og:description"',
    'property="og:url"',
    'rel="canonical"',
)
REQUIRED_SCHEMA = '"@type": "ProfessionalService"'
FORBIDDEN_FORM = re.compile(
    r"<form\b[^>]*>(?:(?!</form>).)*(?:health|diagnos|ssn|dob|patient|phi)",
    re.I | re.S,
)


def _run_build() -> tuple[bool, str]:
    if not (SITES / "package.json").is_file():
        return False, "missing cosmos/sites/package.json"
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run(
            [npm, "install"],
            cwd=SITES,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )
        subprocess.run(
            [npm, "run", "build"],
            cwd=SITES,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        return False, "npm not found — layout source checks only"
    except subprocess.CalledProcessError as exc:
        return False, (exc.stderr or exc.stdout or str(exc))[:2000]
    return True, "built"


def _check_html(path: Path, label: str) -> list[str]:
    fails: list[str] = []
    if not path.is_file():
        return [f"{label}: missing output {path.relative_to(REPO)}"]
    html = path.read_text(encoding="utf-8")
    for needle in REQUIRED_LANDMARKS + REQUIRED_META:
        if needle not in html:
            fails.append(f"{label}: missing {needle!r}")
    if REQUIRED_SCHEMA not in html.replace(" ", ""):
        if REQUIRED_SCHEMA not in html:
            fails.append(f"{label}: missing ProfessionalService JSON-LD")
    if re.search(r"<form\b", html, re.I):
        fails.append(f"{label}: unexpected <form> (PHI/intake forms disallowed)")
    if FORBIDDEN_FORM.search(html):
        fails.append(f"{label}: form appears to collect sensitive health fields")
    if 'itemtype="https://schema.org/BlogPosting"' not in html:
        pass  # home pages only here
    return fails


def _check_layout_sources() -> list[str]:
    fails: list[str] = []
    includes = SITES / "shared" / "_includes"
    for rel in (
        "layouts/base.njk",
        "layouts/article.njk",
        "partials/head-meta.njk",
        "partials/jsonld-professional-service.njk",
        "partials/jsonld-article.njk",
    ):
        if not (includes / rel).is_file():
            fails.append(f"missing shared include {rel}")
    base = (includes / "layouts" / "base.njk").read_text(encoding="utf-8")
    if "{{ content" not in base:
        fails.append("base layout must expose main content region")
    head = (includes / "partials" / "head-meta.njk").read_text(encoding="utf-8")
    for needle in ('property="og:title"', 'rel="canonical"', "twitter:card"):
        if needle not in head:
            fails.append(f"head-meta missing {needle}")
    schema = (includes / "partials" / "jsonld-professional-service.njk").read_text(
        encoding="utf-8"
    )
    if "ProfessionalService" not in schema:
        fails.append("ProfessionalService schema partial missing")
    header = (includes / "partials" / "site-header.njk").read_text(encoding="utf-8")
    if 'role="banner"' not in header or "Skip to main content" not in header:
        fails.append("site header landmarks incomplete")
    footer = (includes / "partials" / "site-footer.njk").read_text(encoding="utf-8")
    if 'role="contentinfo"' not in footer:
        fails.append("site footer landmark missing")
    article = (includes / "layouts" / "article.njk").read_text(encoding="utf-8")
    if "BlogPosting" not in article:
        fails.append("article layout missing BlogPosting microdata")
    return fails


def main() -> int:
    fails = _check_layout_sources()
    built, note = _run_build()
    if built:
        for name, out in SITE_OUT:
            fails.extend(_check_html(out, name))
        fails.extend(_check_html(ARTICLE_OUT, "slpwow-article"))
        article_html = ARTICLE_OUT.read_text(encoding="utf-8") if ARTICLE_OUT.is_file() else ""
        if article_html and '"@type": "BlogPosting"' not in article_html:
            fails.append("slpwow-article: missing BlogPosting JSON-LD")
        if article_html and "<article" not in article_html:
            fails.append("slpwow-article: missing article landmark element")
    elif "npm not found" not in note:
        fails.append(f"build failed: {note}")

    rec = {"ok": not fails, "built": built, "note": note, "failures": fails}
    print(json.dumps(rec, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
