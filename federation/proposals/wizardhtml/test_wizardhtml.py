"""The day-one wizard page is static and does not keep the model key."""

from __future__ import annotations

import re
from pathlib import Path

from cosmos_federation import ROUTE_CHAT, ROUTE_PAGE, ROUTE_SETUP, secret_shape
from wizardhtml import SCHEMA, page_text

_HERE = Path(__file__).parent
_STATIC = ("wizard.html", "wizard.css", "wizard.js")


def _read(name: str) -> str:
    return (_HERE / name).read_text(encoding="utf-8")


def test_page_text_matches_the_html_file() -> None:
    assert SCHEMA == "cosmos-federation-wizardhtml/1"
    html = _read("wizard.html")
    assert page_text() == html
    assert "wizard.css" in html
    assert "wizard.js" in html
    assert ROUTE_PAGE in html


def test_doors_setup_route_and_no_anthropic() -> None:
    html = _read("wizard.html")
    css = _read("wizard.css")
    js = _read("wizard.js")
    bundled = "\n".join((html, css, js))
    assert 'value="openrouter"' in html
    assert 'value="xai"' in html
    assert f'action="{ROUTE_SETUP}"' in html
    assert 'method="post"' in html
    assert f'"{ROUTE_SETUP}"' in js
    assert f'"{ROUTE_CHAT}"' in js
    assert "anthropic" not in bundled.lower()
    assert "claude" not in bundled.lower()
    assert secret_shape(bundled) is False
    assert "paste-here" in html
    urls = re.findall(r"https://[^\"'\s>]+", bundled)
    assert urls == ["https://openrouter.ai/keys", "https://console.x.ai"]
    order = [
        html.find('id="root"'),
        html.find('id="tree_id"'),
        html.find('id="name"'),
        html.find('id="door"'),
        html.find('id="key"'),
        html.find('id="cap"'),
        html.find('id="bind-loopback"'),
        html.find('id="bind-remote"'),
        html.find('id="tls"'),
    ]
    assert all(item >= 0 for item in order)
    assert order == sorted(order)
    chat_at = html.find('<section id="chat"')
    assert chat_at > order[-1]
    assert "hidden" in html[chat_at:html.find(">", chat_at)]


def test_remote_shows_tls_confirmation() -> None:
    html = _read("wizard.html")
    css = _read("wizard.css")
    assert 'value="loopback"' in html
    assert 'value="remote"' in html
    assert 'name="tls"' in html
    assert 'value="yes"' in html
    assert "#tls-row" in css
    assert "#bind-remote:checked" in css


def test_localstorage_is_not_used_for_the_key_and_js_clears_it() -> None:
    js = _read("wizard.js")
    # The storage names may appear only to say why a copy is refused.
    assert "localStorage" in js
    assert "sessionStorage" in js
    assert "query string" in js
    assert "localStorage.setItem" not in js
    assert "localStorage.getItem" not in js
    assert "localStorage[" not in js
    assert "sessionStorage.setItem" not in js
    assert "sessionStorage.getItem" not in js
    assert "sessionStorage[" not in js
    assert ".setItem(" not in js
    assert ".getItem(" not in js
    assert "location.search" not in js
    assert "URLSearchParams" not in js
    assert "document.cookie" not in js
    assert "credentials.get" not in js
    assert "PasswordCredential" not in js
    assert 'keyInput.value = ""' in js
    for name in _STATIC:
        assert secret_shape(_read(name)) is False
