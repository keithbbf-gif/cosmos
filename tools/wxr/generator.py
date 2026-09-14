# -*- coding: utf-8 -*-
"""Build WordPress WXR 1.2 exports with draft posts only (no live publish)."""
from __future__ import annotations

import re
import xml.sax.saxutils as saxutils
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

from .figures import collect_figure_paths, media_notes_html_comment, media_notes_json
from .frontmatter import ParsedPost, meta_string, parse_markdown
from .manifest import Manifest, ManifestPack, get_pack, load_manifest
from .markdown_html import markdown_to_html

GENERATOR = "COSMOS WXR draft-import generator/1.0"
WXR_VERSION = "1.2"


def _slugify(title: str, fallback: str) -> str:
    base = title.lower().strip()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or fallback


def _parse_date(meta: dict[str, Any], path: Path) -> datetime:
    for key in ("date", "published", "pub_date", "created"):
        raw = meta.get(key)
        if not raw:
            continue
        if isinstance(raw, datetime):
            return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
        s = str(raw).strip()
        for fmt in (
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(s.replace("Z", ""), fmt.replace("Z", ""))
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def _wp_datetime(dt: datetime) -> str:
    utc = dt.astimezone(timezone.utc)
    return utc.strftime("%Y-%m-%d %H:%M:%S")


def _cdata(text: str) -> str:
    safe = text.replace("]]>", "]]]]><![CDATA[>")
    return f"<![CDATA[{safe}]]>"


def _elem(tag: str, inner: str, indent: int = 2) -> str:
    pad = " " * indent
    if inner.startswith("<![CDATA["):
        return f"{pad}<{tag}>{inner}</{tag}>"
    escaped = saxutils.escape(inner) if inner else ""
    return f"{pad}<{tag}>{escaped}</{tag}>"


@dataclass
class PostExport:
    source_path: Path
    post_id: int
    title: str
    slug: str
    html: str
    excerpt: str
    author: str
    pub_dt: datetime
    figure_paths: list[str]
    stripped_keys: list[str]


def _resolve_glob(root: Path, pattern: str) -> list[Path]:
    return sorted(p for p in root.glob(pattern) if p.is_file())


def load_posts_for_pack(
    manifest: Manifest,
    pack: ManifestPack,
    *,
    use_samples: bool = False,
) -> list[tuple[Path, ParsedPost]]:
    if use_samples and pack.sample_posts_glob:
        pattern = pack.sample_posts_glob
    else:
        pattern = pack.posts_glob
    paths = _resolve_glob(manifest.repo_root, pattern)
    loaded: list[tuple[Path, ParsedPost]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        loaded.append((path, parse_markdown(text)))
    return loaded


def build_post_exports(
    manifest: Manifest,
    pack: ManifestPack,
    *,
    use_samples: bool = False,
    start_id: int = 900001,
) -> list[PostExport]:
    rows = load_posts_for_pack(manifest, pack, use_samples=use_samples)
    exports: list[PostExport] = []
    for i, (path, parsed) in enumerate(rows):
        post_id = start_id + i
        title = meta_string(parsed.meta, "title") or path.stem.replace("-", " ").title()
        slug = meta_string(parsed.meta, "slug") or _slugify(title, path.stem)
        author = meta_string(parsed.meta, "author", pack.default_author)
        excerpt = meta_string(parsed.meta, "excerpt") or meta_string(parsed.meta, "description")
        pub_dt = _parse_date(parsed.meta, path)
        figure_paths = collect_figure_paths(parsed.meta, parsed.body_md)
        body_html = markdown_to_html(parsed.body_md)
        note_block = media_notes_html_comment(figure_paths)
        if note_block:
            body_html = f"{note_block}\n{body_html}"
        exports.append(
            PostExport(
                source_path=path,
                post_id=post_id,
                title=title,
                slug=slug,
                html=body_html,
                excerpt=excerpt,
                author=author,
                pub_dt=pub_dt,
                figure_paths=figure_paths,
                stripped_keys=list(parsed.stripped_keys),
            )
        )
    return exports


def render_wxr(pack: ManifestPack, posts: list[PostExport]) -> str:
    now = datetime.now(timezone.utc)
    channel_pub = format_datetime(now, usegmt=True)
    base = pack.site_url.rstrip("/")

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        '<rss version="2.0"',
        '  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"',
        '  xmlns:content="http://purl.org/rss/1.0/modules/content/"',
        '  xmlns:wfw="http://wellformedweb.org/CommentAPI/1.1/"',
        '  xmlns:dc="http://purl.org/dc/elements/1.1/"',
        '  xmlns:wp="http://wordpress.org/export/1.2/">',
        "<channel>",
        _elem("title", pack.site_title, 2),
        _elem("link", base, 2),
        _elem("description", pack.site_description, 2),
        _elem("pubDate", channel_pub, 2),
        _elem("language", pack.language, 2),
        _elem("wp:wxr_version", WXR_VERSION, 2),
        _elem("wp:base_site_url", base, 2),
        _elem("wp:base_blog_url", base, 2),
        _elem("generator", GENERATOR, 2),
    ]

    for post in posts:
        link = f"{base}/?p={post.post_id}"
        pub_rfc = format_datetime(post.pub_dt, usegmt=True)
        wp_date = _wp_datetime(post.pub_dt)
        lines.extend(
            [
                "  <item>",
                _elem("title", post.title, 4),
                _elem("link", link, 4),
                _elem("pubDate", pub_rfc, 4),
                f'    <dc:creator>{_cdata(post.author)}</dc:creator>',
                f'    <guid isPermaLink="false">{link}</guid>',
                _elem("description", "", 4),
                f"    <content:encoded>{_cdata(post.html)}</content:encoded>",
                f"    <excerpt:encoded>{_cdata(post.excerpt)}</excerpt:encoded>",
                _elem("wp:post_id", str(post.post_id), 4),
                _elem("wp:post_date", wp_date, 4),
                _elem("wp:post_date_gmt", wp_date, 4),
                _elem("wp:post_modified", wp_date, 4),
                _elem("wp:post_modified_gmt", wp_date, 4),
                _elem("wp:comment_status", "closed", 4),
                _elem("wp:ping_status", "closed", 4),
                _elem("wp:post_name", post.slug, 4),
                _elem("wp:status", "draft", 4),
                _elem("wp:post_parent", "0", 4),
                _elem("wp:menu_order", "0", 4),
                _elem("wp:post_type", "post", 4),
                _elem("wp:post_password", "", 4),
                _elem("wp:is_sticky", "0", 4),
            ]
        )
        if post.figure_paths:
            notes = media_notes_json(post.figure_paths)
            lines.extend(
                [
                    "    <wp:postmeta>",
                    f"      <wp:meta_key>{_cdata('_cosmos_media_notes')}</wp:meta_key>",
                    f"      <wp:meta_value>{_cdata(notes)}</wp:meta_value>",
                    "    </wp:postmeta>",
                ]
            )
        lines.append("  </item>")

    lines.extend(["</channel>", "</rss>", ""])
    return "\n".join(lines)


@dataclass
class GenerateResult:
    pack_id: str
    post_count: int
    wxr_bytes: int
    output_path: Path | None
    dry_run: bool
    posts: list[PostExport]


class WxrGenerator:
    def __init__(self, manifest: Manifest):
        self.manifest = manifest

    def generate(
        self,
        pack_id: str,
        *,
        output: Path | None = None,
        dry_run: bool = False,
        use_samples: bool = False,
    ) -> GenerateResult:
        pack = get_pack(self.manifest, pack_id)
        posts = build_post_exports(self.manifest, pack, use_samples=use_samples)
        xml = render_wxr(pack, posts)
        out_path: Path | None = None
        if dry_run:
            out_path = None
        else:
            if output is None:
                out_dir = self.manifest.repo_root / "content/_ops/wxr/out"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"{pack_id}-draft.wxr.xml"
            else:
                out_path = output
                out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(xml, encoding="utf-8")
        return GenerateResult(
            pack_id=pack_id,
            post_count=len(posts),
            wxr_bytes=len(xml.encode("utf-8")),
            output_path=out_path,
            dry_run=dry_run,
            posts=posts,
        )


def generate_wxr(
    pack_id: str,
    *,
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
    output: Path | None = None,
    dry_run: bool = False,
    use_samples: bool = False,
) -> GenerateResult:
    manifest = load_manifest(manifest_path, repo_root)
    gen = WxrGenerator(manifest)
    return gen.generate(
        pack_id,
        output=output,
        dry_run=dry_run,
        use_samples=use_samples,
    )
