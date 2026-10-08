"""Chooser pins: scrape refuses, day one is api, a profile is not a key."""

from __future__ import annotations

from cosmos_federation import Refuse
from domdefer import SCHEMA, Choice, choose, later


def test_schema_name() -> None:
    assert SCHEMA == "cosmos-federation-domdefer/1"


def test_scrape_refuses_before_any_other_choice() -> None:
    for has_key_id in (True, False):
        for has_browser_profile in (True, False):
            try:
                choose(has_key_id, has_browser_profile, True)
            except Refuse as exc:
                assert exc.code == "SCRAPE"
            else:
                raise AssertionError((has_key_id, has_browser_profile))


def test_day_one_api_ignores_the_profile_flag() -> None:
    assert choose(True, False, False) == Choice(via="api", phase="DAY_ONE")
    assert choose(True, True, False) == Choice(via="api", phase="DAY_ONE")


def test_need_key_despite_a_profile() -> None:
    for has_browser_profile in (True, False):
        got = choose(False, has_browser_profile, False)
        assert got == Choice(via="none", phase="NEED_KEY")
        assert got.via != "dom"


def test_later_names_dom_only_with_a_profile() -> None:
    assert later(True) == Choice(via="dom", phase="LATER")
    try:
        later(False)
    except Refuse as exc:
        assert exc.code == "NO_PROFILE"
    else:
        raise AssertionError("later without a profile")


def test_choose_never_returns_dom() -> None:
    for has_key_id in (True, False):
        for has_browser_profile in (True, False):
            got = choose(has_key_id, has_browser_profile, False)
            assert got.via != "dom"
