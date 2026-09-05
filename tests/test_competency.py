#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F-27: COMPETENCY.toml drives routing.

Bite first against
  _delme/predispose_watchdog2_f27_20260831T123800Z/cosmos_watchdog2.py
which never imports cosmos_competency and pick_agent("web research") is G46.

The current consumer must read the live docs/COMPETENCY.toml and pick the
node the file's own algorithm names — an exit code is not the gate.

Run:  py -3.14 tests/test_competency.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "cosmos"))

from cosmos_competency import (  # noqa: E402
    SCHEMA, CompetencyError, DISPATCHABLE, agent_kind, classify_task_type,
    default_path, load, pick,
)
from cosmos_watchdog2 import pick_agent  # noqa: E402

EVIDENCE = REPO / "cosmos" / "_f27_competency.json"
PRE = (REPO / "_delme" / "predispose_watchdog2_f27_20260831T123800Z"
       / "cosmos_watchdog2.py")
LIVE_TOML = REPO / "docs" / "COMPETENCY.toml"

MINI = """schema = "competency/1"

[router]
nodes_order = ["DOM", "G46", "Cursor", "SGH", "GEM", "OA"]
task_types = ["code-build", "web-research", "DOM-automation"]

[nodes.G46]
id = "G46"
family = "xai"
[nodes.SGH]
id = "SGH"
family = "xai"
[nodes.GEM]
id = "GEM"
family = "google"
[nodes.DOM]
id = "DOM"
family = "dom"
[nodes.Cursor]
id = "Cursor"
family = "cursor"

[skills.code-build.G46]
possessed = true
rating = 5
source = "mini"
[skills.code-build.SGH]
possessed = true
rating = 2
source = "mini"
[skills.code-build.GEM]
possessed = true
rating = 4
source = "mini"
[skills.code-build.DOM]
possessed = false
rating = 0
source = "mini"
[skills.code-build.Cursor]
possessed = true
rating = 5
source = "mini"

[skills.web-research.G46]
possessed = true
rating = 4
source = "mini"
[skills.web-research.SGH]
possessed = true
rating = 5
source = "mini"
[skills.web-research.GEM]
possessed = true
rating = 5
source = "mini"

[skills.DOM-automation.G46]
possessed = false
rating = 0
source = "mini"
[skills.DOM-automation.SGH]
possessed = false
rating = 0
source = "mini"
[skills.DOM-automation.Cursor]
possessed = true
rating = 4
source = "mini"
[skills.DOM-automation.DOM]
possessed = true
rating = 5
source = "mini"
"""


def _load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load " + str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def check_prechange() -> list:
    """Old pick_agent does not consult the matrix."""
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    rec("staged_watchdog2_present", PRE.is_file(), str(PRE))
    old_src = PRE.read_text(encoding="utf-8") if PRE.is_file() else ""
    rec("old_source_has_no_cosmos_competency",
        "cosmos_competency" not in old_src,
        "import present" if "cosmos_competency" in old_src else "absent")
    old = _load_mod("old_cosmos_watchdog2_f27", PRE)
    item = {"title": "web research scout", "body": "find new AI products"}
    agent, kind = old.pick_agent(item, {}, False)
    rec("old_web_research_is_G46",
        agent == "G46" and kind == "grok",
        "agent=%s kind=%s" % (agent, kind))
    rec("old_pick_agent_arity_is_three",
        old.pick_agent.__code__.co_argcount == 3,
        "argcount=%s" % old.pick_agent.__code__.co_argcount)
    return out


def check_current() -> list:
    out = []

    def rec(name, ok, detail=""):
        out.append({"name": name, "ok": bool(ok), "detail": str(detail)[:400]})

    comp_src = (REPO / "cosmos" / "cosmos_competency.py").read_text(
        encoding="utf-8")
    rec("default_path_is_repo_docs_not_a_drive_literal",
        default_path(REPO) == LIVE_TOML
        and default_path().name == "COMPETENCY.toml"
        and "V:\\" not in comp_src and "V:/" not in comp_src,
        str(default_path(REPO)))

    td = Path(tempfile.mkdtemp(prefix="cosmos_comp_"))
    mini_path = td / "COMPETENCY.toml"
    mini_path.write_text(MINI, encoding="utf-8")
    m = load(mini_path)
    rec("mini_schema", m.get("schema") == SCHEMA, m.get("schema"))
    rec("code_build_all_available_is_G46_not_Cursor_tie",
        pick(m, "code-build",
             {"G46", "SGH", "GEM", "DOM", "Cursor"}) == "G46",
        pick(m, "code-build", {"G46", "SGH", "GEM", "DOM", "Cursor"}))
    rec("code_build_without_G46_is_Cursor",
        pick(m, "code-build", {"SGH", "GEM", "Cursor"}) == "Cursor",
        pick(m, "code-build", {"SGH", "GEM", "Cursor"}))
    rec("web_research_SGH_beats_G46_and_ties_GEM_by_nodes_order",
        pick(m, "web-research", {"G46", "SGH", "GEM"}) == "SGH",
        pick(m, "web-research", {"G46", "SGH", "GEM"}))
    rec("dom_automation_prefers_family_dom",
        pick(m, "DOM-automation", {"DOM", "Cursor", "G46"}) == "DOM",
        pick(m, "DOM-automation", {"DOM", "Cursor", "G46"}))
    rec("possessed_false_never_wins",
        pick(m, "code-build", {"DOM", "SGH"}) == "SGH",
        pick(m, "code-build", {"DOM", "SGH"}))

    try:
        pick(m, "no-such-task", {"G46"})
        rec("unknown_task_refuses", False, "did not raise")
    except CompetencyError as e:
        rec("unknown_task_refuses", e.kind == "UNKNOWN_TASK", e.kind)

    try:
        pick(m, "DOM-automation", {"G46", "SGH"})
        rec("no_candidate_refuses", False, "did not raise")
    except CompetencyError as e:
        rec("no_candidate_refuses", e.kind == "NO_CANDIDATE", str(e)[:200])

    missing = td / "nope.toml"
    try:
        load(missing)
        rec("missing_file_unreadable", False, "did not raise")
    except CompetencyError as e:
        rec("missing_file_unreadable", e.kind == "UNREADABLE", e.kind)

    bad = td / "bad.toml"
    bad.write_text("schema = \"nope\"\n", encoding="utf-8")
    try:
        load(bad)
        rec("bad_schema_refuses", False, "did not raise")
    except CompetencyError as e:
        rec("bad_schema_refuses", e.kind == "BAD_SCHEMA", e.kind)

    rec("classify_research",
        classify_task_type("active scout for new AI") == "web-research",
        classify_task_type("active scout for new AI"))
    rec("classify_coding_wins_over_research",
        classify_task_type("research then implement the daemon")
        == "code-build",
        classify_task_type("research then implement the daemon"))
    rec("classify_dom",
        classify_task_type("playwright browser automation") == "DOM-automation",
        classify_task_type("playwright browser automation"))
    rec("classify_vendor_plural",
        classify_task_type("different-family critique of the slice")
        == "vendor-plural-critique",
        classify_task_type("different-family critique of the slice"))
    rec("classify_default_is_code_build",
        classify_task_type("please handle this") == "code-build",
        classify_task_type("please handle this"))

    rec("agent_kind_G46", agent_kind("G46") == ("G46", "grok"),
        str(agent_kind("G46")))
    rec("agent_kind_SGH", agent_kind("SGH") == ("SGH", "grok"),
        str(agent_kind("SGH")))
    try:
        agent_kind("DOM")
        rec("agent_kind_DOM_is_NO_DISPATCH", False, "did not raise")
    except CompetencyError as e:
        rec("agent_kind_DOM_is_NO_DISPATCH", e.kind == "NO_DISPATCH", e.kind)

    rec("DISPATCHABLE_is_grok_nodes_only",
        DISPATCHABLE == frozenset({"G46", "SGH"}),
        str(sorted(DISPATCHABLE)))

    # Live canon file — the value only that file can emit.
    live = load(LIVE_TOML)
    rec("live_schema_competency_1",
        live.get("schema") == SCHEMA, live.get("schema"))
    live_nodes = set((live.get("nodes") or {}).keys())
    required_six = {"G46", "GEM", "OA", "SGH", "Cursor", "DOM"}
    rec("live_six_nodes",
        required_six <= live_nodes,
        str(sorted(live_nodes)))
    live_code = pick(live, "code-build", live_nodes)
    rec("live_code_build_is_G46",
        live_code == "G46", live_code)
    live_web = pick(live, "web-research", live_nodes)
    rec("live_web_research_is_SGH",
        live_web == "SGH", live_web)
    live_dom = pick(live, "DOM-automation", live_nodes)
    rec("live_dom_automation_is_DOM",
        live_dom == "DOM", live_dom)

    # WD2 consumer. Inject the live matrix so the test does not depend on cwd.
    def _pa(item, loads, key, **kw):
        try:
            return pick_agent(item, loads, key, **kw)
        except TypeError as e:
            return ("TYPEERROR", str(e))

    web_item = {"title": "web research scout", "body": "find new AI products"}
    agent, kind = _pa(web_item, {}, False, matrix=live)
    rec("pick_agent_web_research_is_SGH_grok",
        agent == "SGH" and kind == "grok",
        "agent=%s kind=%s" % (agent, kind))
    agent, kind = _pa(web_item, {}, False)
    rec("pick_agent_default_path_loads_live_toml",
        agent == "SGH" and kind == "grok",
        "agent=%s kind=%s" % (agent, kind))
    code_item = {"title": "implement the daemon", "body": "wire the clock"}
    agent, kind = _pa(code_item, {}, False, matrix=live)
    rec("pick_agent_code_build_stays_G46",
        agent == "G46" and kind == "grok",
        "agent=%s kind=%s" % (agent, kind))
    cur_item = {"title": "Cursor key probe", "body": ""}
    agent, kind = _pa(cur_item, {}, True, matrix=live)
    rec("pick_agent_named_cursor_still_wins",
        agent == "Cursor" and kind == "cursor",
        "agent=%s kind=%s" % (agent, kind))
    loads = {"root": {"load": 9}, "lg": {"load": 9}, "pb": {"load": 9}}
    agent, kind = _pa(code_item, loads, True, matrix=live)
    rec("pick_agent_overflow_sheds_G46_to_Cursor",
        agent == "Cursor" and kind == "cursor",
        "agent=%s kind=%s" % (agent, kind))
    agent, kind = _pa(
        {"title": "playwright browser automation", "body": ""},
        {}, False, matrix=live)
    rec("pick_agent_dom_falls_back_when_DOM_not_dispatchable",
        agent == "G46" and kind == "grok",
        "agent=%s kind=%s" % (agent, kind))
    return out


def main() -> int:
    if not PRE.is_file():
        print("REFUSING: pre-change watchdog2 not staged at %s" % PRE)
        return 1
    if not LIVE_TOML.is_file():
        print("REFUSING: live COMPETENCY.toml missing at %s" % LIVE_TOML)
        return 1
    pre = check_prechange()
    cur = check_current()
    pre_pass = sum(1 for c in pre if c["ok"])
    cur_pass = sum(1 for c in cur if c["ok"])
    evidence = {
        "ok": pre_pass == len(pre) and cur_pass == len(cur),
        "probe": "tests/test_competency.py — F-27 competency consumer",
        "prechange_path": str(PRE),
        "live_toml": str(LIVE_TOML),
        "prechange": {"checks": pre, "tests_run": len(pre),
                      "tests_passed": pre_pass},
        "current": {"checks": cur, "tests_run": len(cur),
                    "tests_passed": cur_pass},
        "emitted": {
            "live_code_build": next(
                (c["detail"] for c in cur
                 if c["name"] == "live_code_build_is_G46"), ""),
            "live_web_research": next(
                (c["detail"] for c in cur
                 if c["name"] == "live_web_research_is_SGH"), ""),
            "pick_agent_web": next(
                (c["detail"] for c in cur
                 if c["name"] == "pick_agent_web_research_is_SGH_grok"), ""),
        },
    }
    EVIDENCE.write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    print("== PRECHANGE (old pick_agent MUST ignore the matrix) ==")
    for c in pre:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("== CURRENT ==")
    for c in cur:
        print("  %s  %s  %s" % (
            "OK  " if c["ok"] else "FAIL", c["name"], c.get("detail") or ""))
    print("EVIDENCE %s" % EVIDENCE)
    print("SELFTEST %s - current %d/%d; prechange-lacks-consumer %d/%d"
          % ("PASS" if evidence["ok"] else "FAIL",
             cur_pass, len(cur), pre_pass, len(pre)))
    return 0 if evidence["ok"] else 1


def test_competency():
    assert main() == 0


if __name__ == "__main__":
    sys.exit(main())
