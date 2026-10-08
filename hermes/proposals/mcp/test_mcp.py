"""Refusal and success coverage for the MCP client proposal."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

import mcp
from cosmos_hermes import Refuse, secret_shape

_GRANTS: set[str] = {"github", "docs", "local"}


def test_schema_and_source_is_inert() -> None:
    assert mcp.SCHEMA == "cosmos-hermes-mcp/1"
    source = Path(__file__).with_name("mcp.py").read_text(encoding="utf-8")
    for banned in (
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "pickle",
        "Popen",
        "os.system",
        "eval(",
        "exec(",
        "compile(",
        "__import__",
    ):
        assert banned not in source.replace("re.compile(", "")
    assert "const_eq(" in source
    assert "PathJail(" in source
    assert "bound_text(" in source
    assert "bound_bytes(" in source


def test_initialize_list_call_and_frame() -> None:
    init = mcp.initialize(1, "github", _GRANTS)
    assert init.payload() == {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": mcp.PROTOCOL,
            "capabilities": {},
            "clientInfo": {"name": mcp.CLIENT_NAME, "version": mcp.CLIENT_VERSION},
        },
    }
    assert "server_id" not in init.payload()
    listed = mcp.tools_list(2, "github", _GRANTS)
    assert listed.payload()["method"] == "tools/list"
    assert listed.payload()["params"] == {}
    called = mcp.tools_call(3, "github", _GRANTS, "list_issues", {"state": "open", "limit": 2})
    assert called.payload() == {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "list_issues", "arguments": {"limit": 2, "state": "open"}},
    }
    note = mcp.initialized("github", _GRANTS)
    assert note.request_id is None
    assert "id" not in note.payload()
    assert note.payload()["method"] == "notifications/initialized"
    frame = mcp.encode_frame(called)
    assert frame.count("\n") == 1
    parsed = mcp.parse_frame(frame.encode("utf-8"), "github", _GRANTS)
    assert mcp.encode_frame(parsed) == frame
    assert secret_shape(repr(called)) is False


def test_filter_allow_deny_and_glob() -> None:
    names = ["create_issue", "delete_issue", "list_dns_records", "docs_search", "docs", "create_issue"]
    kept = mcp.filter_tools(names, ["create_issue", "*_dns_*", "docs"], ["delete_issue", "create_issue"])
    assert kept == ["list_dns_records", "docs"]
    assert mcp.filter_tools(["docs_search", "docs"], ["docs"], []) == ["docs"]
    assert mcp.filter_tools(["read_file"], ["*"], ["read_file"]) == []
    wide = mcp.filter_tools(["browser_run_code_unsafe"], ["browser_run_code_unsafe"], [])
    assert wide == ["browser_run_code_unsafe"]


def test_empty_allow_and_filter_refusals() -> None:
    with pytest.raises(Refuse) as empty:
        mcp.filter_tools(["read_file"], [], [])
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as missing:
        mcp.filter_tools(["read_file"], None, [])
    assert missing.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as bad_filter:
        mcp.filter_tools(["read_file"], "read_file", [])
    assert bad_filter.value.code == "BAD_FILTER"
    with pytest.raises(Refuse) as bad_names:
        mcp.filter_tools({"read_file"}, ["read_file"], [])
    assert bad_names.value.code == "BAD_NAMES"
    with pytest.raises(Refuse) as bad_name:
        mcp.filter_tools(["ok", 3], ["ok"], [])
    assert bad_name.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as too_many:
        mcp.filter_tools(["tool"] * (mcp.MAX_TOOLS + 1), ["tool"], [])
    assert too_many.value.code == "TOO_MANY"
    with pytest.raises(Refuse) as secret:
        mcp.filter_tools(["sk-livekeyvalue"], ["sk-livekeyvalue"], [])
    assert secret.value.code == "SECRET_SHAPE"
    assert "sk-live" not in str(secret.value)


def test_guarded_call_policy_deny_wins() -> None:
    message = mcp.guarded_tools_call(
        4,
        "github",
        _GRANTS,
        "list_issues",
        {},
        ["list_issues", "delete_issue"],
        ["delete_issue"],
    )
    assert message.payload()["method"] == "tools/call"
    with pytest.raises(Refuse) as denied:
        mcp.guarded_tools_call(
            5,
            "github",
            _GRANTS,
            "browser_run_code_unsafe",
            {},
            ["browser_run_code_unsafe"],
            [],
        )
    assert denied.value.code == "TOOL_DENIED"
    with pytest.raises(Refuse) as both:
        mcp.guarded_tools_call(6, "github", _GRANTS, "list_issues", {}, ["list_issues"], ["list_issues"])
    assert both.value.code == "TOOL_DENIED"
    with pytest.raises(Refuse) as empty:
        mcp.guarded_tools_call(7, "github", _GRANTS, "list_issues", {}, [], [])
    assert empty.value.code == "EMPTY_ALLOW"


def test_sampling_confirm_cap_and_refusals() -> None:
    models = ["openai/gpt-4o"]
    low = mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", 100, 10)
    assert low.code == "SAMPLING_CONFIRM"
    assert low.approved is False
    assert low.max_tokens == 100
    assert low.token_cap == mcp.TOKEN_CAP
    high = mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", 9000, 120)
    assert high.requested_max_tokens == 9000
    assert high.max_tokens == mcp.TOKEN_CAP
    assert high.requested_timeout_s == 120
    assert high.timeout_s == mcp.TIMEOUT_CAP
    assert high.approved is False
    assert high == mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", 9000, 120)
    assert secret_shape(repr(high)) is False
    with pytest.raises(AttributeError):
        high.approved = True  # type: ignore[misc]
    with pytest.raises(Refuse) as yolo:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", 10, 10, "yolo")
    assert yolo.value.code == "UNKNOWN_MODE"
    with pytest.raises(Refuse) as off:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", 10, 10, "off")
    assert off.value.code == "UNKNOWN_MODE"
    with pytest.raises(Refuse) as empty:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", [], "hello", 10, 10)
    assert empty.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as unknown:
        mcp.sampling_request("docs", _GRANTS, "other/model", models, "hello", 10, 10)
    assert unknown.value.code == "UNKNOWN_MODEL"
    with pytest.raises(Refuse) as secret:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "sk-livekeyvalue", 10, 10)
    assert secret.value.code == "SECRET_SHAPE"
    assert "sk-live" not in str(secret.value)
    with pytest.raises(Refuse) as raised:
        mcp.SamplingRequest(
            server_id="docs",
            model="openai/gpt-4o",
            prompt="hello",
            requested_max_tokens=9000,
            max_tokens=9000,
            token_cap=mcp.TOKEN_CAP,
            requested_timeout_s=30,
            timeout_s=30,
            timeout_cap=mcp.TIMEOUT_CAP,
            code="SAMPLING_CONFIRM",
            approved=False,
        )
    assert raised.value.code == "CAP_RAISED"
    with pytest.raises(Refuse) as approved:
        mcp.SamplingRequest(
            server_id="docs",
            model="openai/gpt-4o",
            prompt="hello",
            requested_max_tokens=10,
            max_tokens=10,
            token_cap=mcp.TOKEN_CAP,
            requested_timeout_s=10,
            timeout_s=10,
            timeout_cap=mcp.TIMEOUT_CAP,
            code="SAMPLING_CONFIRM",
            approved=True,
        )
    assert approved.value.code == "SELF_APPROVAL"
    with pytest.raises(Refuse) as bad_cap:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", models, "hello", True, 10)
    assert bad_cap.value.code == "BAD_CAP"


def test_server_grant_and_shell_argv() -> None:
    with pytest.raises(Refuse) as unknown:
        mcp.tools_list(1, "stripe", _GRANTS)
    assert unknown.value.code == "UNKNOWN_SERVER"
    with pytest.raises(Refuse) as empty:
        mcp.initialize(1, "github", set())
    assert empty.value.code == "UNKNOWN_SERVER"
    with pytest.raises(Refuse) as bad_grants:
        mcp.initialize(1, "github", "github")
    assert bad_grants.value.code == "BAD_GRANTS"
    with pytest.raises(Refuse) as bad_server:
        mcp.initialize(1, "bad/server", _GRANTS)
    assert bad_server.value.code == "BAD_SERVER"
    with pytest.raises(Refuse) as shell:
        mcp.unspawned_argv("github", "npx -y @pkg", _GRANTS)
    assert shell.value.code == "SHELL_STRING"
    src = ["npx", "-y", "pkg"]
    got = mcp.unspawned_argv("github", src, _GRANTS)
    assert got == ["npx", "-y", "pkg"]
    assert got is not src
    src.append("mutated")
    assert got == ["npx", "-y", "pkg"]
    assert mcp.unspawned_argv("local", ["echo", "a && b"], _GRANTS) == ["echo", "a && b"]
    with pytest.raises(Refuse) as bad_argv:
        mcp.unspawned_argv("local", ["echo", 1], _GRANTS)
    assert bad_argv.value.code == "BAD_ARGV"
    with pytest.raises(Refuse) as empty_argv:
        mcp.unspawned_argv("local", [], _GRANTS)
    assert empty_argv.value.code == "EMPTY_ARGV"
    with pytest.raises(Refuse) as secret_argv:
        mcp.unspawned_argv("local", ["echo", "sk-livekeyvalue"], _GRANTS)
    assert secret_argv.value.code == "SECRET_SHAPE"


def test_stdio_jail_and_http_credential() -> None:
    root = Path(__file__).resolve().parent
    spec = mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, str(root), [str(root)])
    assert spec.spawned is False
    assert spec.argv == ("echo", "ok")
    assert spec.cwd == str(root)
    assert secret_shape(repr(spec)) is False
    with pytest.raises(Refuse) as outside:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, str(root.parent), [str(root)])
    assert outside.value.code == "OUTSIDE_GRANT"
    with pytest.raises(Refuse) as no_grant:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, str(root), [])
    assert no_grant.value.code == "NO_GRANT"
    with pytest.raises(Refuse) as bad_path:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, 4, [str(root)])
    assert bad_path.value.code == "BAD_PATH"
    with pytest.raises(Refuse) as spawned:
        mcp.StdioSpec(server_id="local", argv=("echo",), cwd=str(root), spawned=True)
    assert spawned.value.code == "SELF_SPAWN"
    target = mcp.http_target("docs", "https://mcp.example.com/mcp", "cred.docs", _GRANTS)
    assert target.connected is False
    assert secret_shape(repr(target)) is False
    with pytest.raises(Refuse) as missing:
        mcp.http_target("docs", "https://mcp.example.com/mcp", "", _GRANTS)
    assert missing.value.code == "MISSING_CREDENTIAL"
    with pytest.raises(Refuse) as shaped:
        mcp.http_target("docs", "https://mcp.example.com/mcp", "sk-livekeyvalue", _GRANTS)
    assert shaped.value.code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as bearer:
        mcp.http_target("docs", "https://mcp.example.com/mcp", "Bearer abcdefghijk", _GRANTS)
    assert bearer.value.code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as bad_url:
        mcp.http_target("docs", "file:///etc/passwd", "cred.docs", _GRANTS)
    assert bad_url.value.code == "BAD_URL"
    with pytest.raises(Refuse) as bad_cred:
        mcp.http_target("docs", "https://mcp.example.com/mcp", "not a cred", _GRANTS)
    assert bad_cred.value.code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as connected:
        mcp.HttpTarget(server_id="docs", url="https://mcp.example.com/mcp", credential_id="cred.docs", connected=True)
    assert connected.value.code == "SELF_CONNECT"


def test_discovery_retry_and_names() -> None:
    unlimited = mcp.discovery_limit(0)
    assert unlimited.requested == 0
    assert unlimited.applied == mcp.DISCOVERY_CAP
    assert mcp.discovery_limit(100).applied == mcp.DISCOVERY_CAP
    assert mcp.discovery_limit(2).applied == 2
    retry = mcp.confirming_retry("TIMEOUT", 0)
    assert retry.failure == "TIMEOUT"
    assert retry.attempt == 1
    with pytest.raises(Refuse) as again:
        mcp.confirming_retry("TIMEOUT", 1)
    assert again.value.code == "RETRY_EXHAUSTED"
    with pytest.raises(Refuse) as other:
        mcp.confirming_retry("BROKE", 0)
    assert other.value.code == "NO_RETRY"
    assert mcp.registered_name("github", "create-issue") == "mcp_github_create_issue"
    assert mcp.registered_name("my-api", "query.data") == "mcp_my_api_query_data"
    assert mcp.registered_name("filesystem", "read_file") == "mcp_filesystem_read_file"
    utils = mcp.utility_tools(
        "github",
        _GRANTS,
        resources=True,
        prompts=False,
        supports_resources=True,
        supports_prompts=True,
    )
    assert utils == ("mcp_github_list_resources", "mcp_github_read_resource")
    quiet = mcp.utility_tools(
        "github",
        _GRANTS,
        resources=True,
        prompts=True,
        supports_resources=False,
        supports_prompts=False,
    )
    assert quiet == ()


def test_sanitize_meta_args_and_elicitation() -> None:
    flag = "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F"
    assert mcp.sanitize_text(flag + "hi\U000E0041!") == flag + "hi!"
    with pytest.raises(Refuse) as not_text:
        mcp.sanitize_text(4)
    assert not_text.value.code == "NOT_TEXT"
    view = mcp.present_tool("github", _GRANTS, "list_issues", "bugs\U000E0041")
    assert view.name == "mcp_github_list_issues"
    assert view.description == "bugs"
    meta = mcp.visible_meta(
        {
            "com.example/handoff": "keep",
            "modelcontextprotocol.io/hidden": "nope",
            "tools.mcp.com/hidden": "nope",
        }
    )
    assert meta == {"com.example/handoff": "keep"}
    with pytest.raises(Refuse) as bad_meta:
        mcp.visible_meta(["nope"])
    assert bad_meta.value.code == "BAD_META"
    with pytest.raises(Refuse) as deep:
        node: object = "x"
        for _ in range(mcp.MAX_DEPTH):
            node = {"k": node}
        mcp.tools_call(1, "github", _GRANTS, "list_issues", node)
    assert deep.value.code == "TOO_DEEP"
    with pytest.raises(Refuse) as args:
        mcp.tools_call(1, "github", _GRANTS, "list_issues", ["nope"])
    assert args.value.code == "BAD_ARGS"
    with pytest.raises(Refuse) as nan:
        mcp.tools_call(1, "github", _GRANTS, "list_issues", {"n": float("nan")})
    assert nan.value.code == "BAD_ARGS"
    form = mcp.elicitation_request("docs", _GRANTS, "form")
    assert form.code == "ELICIT_CONFIRM"
    assert form.approved is False
    with pytest.raises(Refuse) as url_mode:
        mcp.elicitation_request("docs", _GRANTS, "url")
    assert url_mode.value.code == "URL_ELICITATION"
    with pytest.raises(Refuse) as yolo:
        mcp.elicitation_request("docs", _GRANTS, "yolo")
    assert yolo.value.code == "UNKNOWN_MODE"


def test_parse_refusals() -> None:
    with pytest.raises(Refuse) as bad:
        mcp.parse_frame(b"{", "github", _GRANTS)
    assert bad.value.code == "BAD_RPC"
    frame = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "shutdown", "params": {}}).encode("utf-8")
    with pytest.raises(Refuse) as mode:
        mcp.parse_frame(frame, "github", _GRANTS)
    assert mode.value.code == "UNKNOWN_MODE"
    denied = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "browser_run_code_unsafe", "arguments": {}},
        }
    ).encode("utf-8")
    with pytest.raises(Refuse) as tool:
        mcp.parse_frame(denied, "github", _GRANTS)
    assert tool.value.code == "TOOL_DENIED"
    with pytest.raises(Refuse) as unknown:
        mcp.parse_frame(b'{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}', "nope", _GRANTS)
    assert unknown.value.code == "UNKNOWN_SERVER"


@dataclass(frozen=True, slots=True)
class _Studio:
    tools: tuple[str, ...]
    listed: str
    created: str
    denied: str
    empty: str
    disk: str
    offline: str
    connected: bool
    method: str
    card: str
    note: str
    session: str
    rebuilt: tuple[str, ...]
    clean: bool


def _studio_story() -> _Studio:
    grants: set[str] = {"linear"}
    allow = ["list_issues", "create_issue"]
    grant = mcp.admit_tools("linear", grants, allow)
    listed = mcp.resolve_tool(grant, "list_issues")
    created = mcp.resolve_tool(grant, "create_issue")
    denied = ""
    try:
        mcp.resolve_tool(grant, "delete_issue")
    except Refuse as exc:
        denied = exc.code
    empty = ""
    try:
        mcp.admit_tools("linear", grants, [])
    except Refuse as exc:
        empty = exc.code
    disk = ""
    try:
        mcp.load_from_path(r"C:\studio\linear_server.py")
    except Refuse as exc:
        disk = exc.code
    target = mcp.http_target("linear", "https://mcp.linear.app/mcp", "cred.linear", grants)
    offline = ""
    try:
        mcp.connect(target)
    except Refuse as exc:
        offline = exc.code
    call = mcp.guarded_tools_call(
        11,
        "linear",
        grants,
        "create_issue",
        {"session": "studio", "card": "card-441", "note": "north light warm"},
        allow,
        [],
    )
    payload = call.payload()
    params_raw = payload["params"]
    if not isinstance(params_raw, dict):
        raise AssertionError("params")
    arguments_raw = params_raw["arguments"]
    if not isinstance(arguments_raw, dict):
        raise AssertionError("arguments")
    card_raw = arguments_raw["card"]
    note_raw = arguments_raw["note"]
    session_raw = arguments_raw["session"]
    if not isinstance(card_raw, str) or not isinstance(note_raw, str) or not isinstance(session_raw, str):
        raise AssertionError("fields")
    rows = mcp.rebuild(mcp.snapshot([grant]))
    rebuilt: tuple[str, ...] = ()
    for row in rows:
        rebuilt = row.tools
        break
    clean = secret_shape(repr(grant)) is False and secret_shape(repr(call)) is False
    return _Studio(
        tools=grant.tools,
        listed=listed,
        created=created,
        denied=denied,
        empty=empty,
        disk=disk,
        offline=offline,
        connected=target.connected,
        method=call.method,
        card=card_raw,
        note=note_raw,
        session=session_raw,
        rebuilt=rebuilt,
        clean=clean and secret_shape(repr(target)) is False,
    )


def test_example_mcp() -> None:
    first = _studio_story()
    second = _studio_story()
    assert first == second
    assert first.tools == ("list_issues", "create_issue")
    assert first.listed == "list_issues"
    assert first.created == "create_issue"
    assert first.denied == "TOOL_DENIED"
    assert first.empty == "EMPTY_ALLOW"
    assert first.disk == "DISK_IMPORT"
    assert first.offline == "NO_CONNECT"
    assert first.connected is False
    assert first.method == "tools/call"
    assert first.card == "card-441"
    assert first.note == "north light warm"
    assert first.session == "studio"
    assert first.rebuilt == ("list_issues", "create_issue")
    assert first.clean is True


def test_allowlist_replay_window_and_budget() -> None:
    grants: set[str] = {"linear"}
    grant = mcp.admit_tools("linear", grants, ["list_issues", "create_issue"])
    assert mcp.resolve_tool(grant, "create_issue") == "create_issue"
    with pytest.raises(Refuse) as third:
        mcp.resolve_tool(grant, "delete_issue")
    assert third.value.code == "TOOL_DENIED"
    with pytest.raises(Refuse) as dup:
        mcp.admit_tools("linear", grants, ["list_issues", "list_issues"])
    assert dup.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as policy:
        mcp.admit_tools("linear", grants, ["browser_run_code_unsafe"])
    assert policy.value.code == "TOOL_DENIED"
    with pytest.raises(Refuse) as missing_grant:
        mcp.resolve_tool("linear", "list_issues")
    assert missing_grant.value.code == "BAD_GRANT"
    with pytest.raises(Refuse) as empty_record:
        mcp.ToolGrant(server_id="linear", tools=())
    assert empty_record.value.code == "EMPTY_ALLOW"
    again = mcp.rebuild(mcp.snapshot([grant]))
    assert again == mcp.rebuild([grant])
    with pytest.raises(Refuse) as duplicate_server:
        mcp.rebuild([grant, grant])
    assert duplicate_server.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as bad_grant:
        mcp.rebuild([("linear", ("list_issues", 3))])
    assert bad_grant.value.code == "BAD_NAME"
    seen = mcp.note_id(frozenset(), 11)
    assert seen == frozenset({11})
    with pytest.raises(Refuse) as replay:
        mcp.note_id(seen, 11)
    assert replay.value.code == "REPLAY"
    with pytest.raises(Refuse) as bad_seen:
        mcp.note_id(["11"], 11)
    assert bad_seen.value.code == "BAD_RPC"
    fresh = mcp.accept_window(150, 100, 999)
    assert fresh.requested == 999
    assert fresh.applied == mcp.WINDOW_CAP
    assert fresh.cap == mcp.WINDOW_CAP
    assert fresh.age_s == 50
    with pytest.raises(Refuse) as stale:
        mcp.accept_window(200, 100, 50)
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as future:
        mcp.accept_window(100, 130, 50)
    assert future.value.code == "STALE"
    with pytest.raises(Refuse) as bad_window:
        mcp.accept_window(100, 100, True)
    assert bad_window.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as raised_window:
        mcp.Freshness(requested=10, applied=10, cap=10, age_s=1)
    assert raised_window.value.code == "CAP_RAISED"
    root_views = [
        mcp.present_tool("github", _GRANTS, "list_issues", "aa"),
        mcp.present_tool("github", _GRANTS, "create_issue", "bbbb"),
        mcp.present_tool("github", _GRANTS, "update_issue", "c"),
    ]
    pick = mcp.select_views(root_views, 3)
    assert [view.description for view in pick.views] == ["aa", "c"]
    wide = mcp.select_views(root_views[:1], 10_000)
    assert wide.requested == 10_000
    assert wide.applied == mcp.DESC_BUDGET
    assert wide.cap == mcp.DESC_BUDGET
    with pytest.raises(Refuse) as bad_budget:
        mcp.select_views(root_views, 0)
    assert bad_budget.value.code == "BAD_CAP"
    assert mcp.filter_tools(["docs", "docs"], ["docs"], []) == ["docs"]


def test_edge_refusals_and_reserved_meta() -> None:
    with pytest.raises(Refuse) as huge:
        mcp.tools_call(1, "github", _GRANTS, "list_issues", {"n": 10**13})
    assert huge.value.code == "BAD_ARGS"
    with pytest.raises(Refuse) as negative_cap:
        mcp.discovery_limit(-1)
    assert negative_cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as bool_cap:
        mcp.discovery_limit(True)
    assert bool_cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as raised_discovery:
        mcp.DiscoveryLimit(requested=0, applied=0, cap=mcp.DISCOVERY_CAP)
    assert raised_discovery.value.code == "CAP_RAISED"
    with pytest.raises(Refuse) as negative_retry:
        mcp.confirming_retry("TIMEOUT", -1)
    assert negative_retry.value.code == "NO_RETRY"
    with pytest.raises(Refuse) as zero_tokens:
        mcp.sampling_request("docs", _GRANTS, "openai/gpt-4o", ["openai/gpt-4o"], "hello", 0, 10)
    assert zero_tokens.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as secret_server:
        mcp.tools_list(1, "sk-livekeyvalue", {"sk-livekeyvalue"})
    assert secret_server.value.code == "SECRET_SHAPE"
    assert "sk-live" not in str(secret_server.value)
    with pytest.raises(Refuse) as secret_prompt:
        mcp.SamplingRequest(
            server_id="docs",
            model="openai/gpt-4o",
            prompt="sk-livekeyvalue",
            requested_max_tokens=10,
            max_tokens=10,
            token_cap=mcp.TOKEN_CAP,
            requested_timeout_s=10,
            timeout_s=10,
            timeout_cap=mcp.TIMEOUT_CAP,
            code="SAMPLING_CONFIRM",
            approved=False,
        )
    assert secret_prompt.value.code == "SECRET_SHAPE"
    assert "sk-live" not in str(secret_prompt.value)
    with pytest.raises(Refuse) as secret_view:
        mcp.present_tool("github", _GRANTS, "list_issues", "sk-livekeyvalue")
    assert secret_view.value.code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as disk_secret:
        mcp.load_from_path("sk-livekeyvalue")
    assert disk_secret.value.code == "SECRET_SHAPE"
    with pytest.raises(Refuse) as disk_other:
        mcp.load_from_path(None)
    assert disk_other.value.code == "DISK_IMPORT"
    with pytest.raises(Refuse) as not_frame:
        mcp.encode_frame(None)
    assert not_frame.value.code == "BAD_RPC"
    with pytest.raises(Refuse) as not_bytes:
        mcp.parse_frame("nope", "github", _GRANTS)
    assert not_bytes.value.code == "BAD_RPC"
    spaced = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "bad name", "arguments": {}}}
    ).encode("utf-8")
    with pytest.raises(Refuse) as bad_tool:
        mcp.parse_frame(spaced, "github", _GRANTS)
    assert bad_tool.value.code == "BAD_NAME"
    listed = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_issues", "arguments": ["x"]}}
    ).encode("utf-8")
    with pytest.raises(Refuse) as bad_arguments:
        mcp.parse_frame(listed, "github", _GRANTS)
    assert bad_arguments.value.code == "BAD_ARGS"
    meta = mcp.visible_meta(
        {
            "com.example/handoff": "keep",
            "io.modelcontextprotocol/auth": "drop",
            "com.example.mcp/note": "keep-too",
            "mcp.dev/hidden": "drop",
        }
    )
    assert meta == {"com.example/handoff": "keep", "com.example.mcp/note": "keep-too"}
    with pytest.raises(Refuse) as bad_key:
        mcp.visible_meta({"not a key": "x"})
    assert bad_key.value.code == "BAD_META"
    root = Path(__file__).resolve().parent
    with pytest.raises(Refuse) as int_root:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, str(root), [4])
    assert int_root.value.code == "NO_GRANT"
    with pytest.raises(Refuse) as relative:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, "studio", [str(root)])
    assert relative.value.code == "RELATIVE_PATH"
    with pytest.raises(Refuse) as dotdot:
        mcp.stdio_spec("local", ["echo", "ok"], _GRANTS, str(root) + "\\..\\nope", [str(root)])
    assert dotdot.value.code == "DOTDOT"
    with pytest.raises(Refuse) as nul:
        mcp.sanitize_text("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as newline:
        mcp.http_target("docs", "https://mcp.example.com/mcp\n", "cred.docs", _GRANTS)
    assert newline.value.code == "BAD_URL"
    with pytest.raises(Refuse) as userinfo:
        mcp.http_target("docs", "https://user@mcp.example.com/mcp", "cred.docs", _GRANTS)
    assert userinfo.value.code == "BAD_URL"
    with pytest.raises(Refuse) as utility_mode:
        mcp.utility_tools(
            "github",
            _GRANTS,
            resources="yes",
            prompts=False,
            supports_resources=True,
            supports_prompts=False,
        )
    assert utility_mode.value.code == "UNKNOWN_MODE"
