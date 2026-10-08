"""Exact routes read from Core, plus the three day-one paths Core does not have.

Source is ``cosmos/cosmos_service.py`` ``do_GET`` / ``do_POST`` (and the
allowlists those methods look up). A row is ``EXISTS`` only when that exact
path string is in the file. Concatenated cDeck and XTalk file keys are not
listed: ``/cdeck/`` + name and ``/xtalk/`` + name are not exact path strings.

The chat window and the wizard need this route and Core does not have it yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from cosmos_federation.bounds import bound_text
from cosmos_federation.errors import Refuse
from cosmos_federation.product import ROUTE_CHAT, ROUTE_PAGE, ROUTE_SETUP
from cosmos_federation.redact import secret_shape

SCHEMA = "cosmos-federation-routes/1"

# The chat window and the wizard need this route and Core does not have it yet.
_DAY_ONE_WHY = (
    "the chat window and the wizard need this route and Core does not have it yet"
)

_DAY_ONE_PATHS = frozenset({ROUTE_PAGE, ROUTE_SETUP, ROUTE_CHAT})

_Method = Literal["GET", "POST"]
_Phase = Literal["EXISTS", "DAY_ONE"]


@dataclass(frozen=True, slots=True)
class Route:
    """One method plus path. ``phase`` is ``EXISTS`` or ``DAY_ONE``."""

    method: _Method
    path: str
    phase: _Phase
    why: str

    def __post_init__(self) -> None:
        method = bound_text(self.method, limit=8, name="method")
        path = bound_text(self.path, limit=80, name="path")
        phase = bound_text(self.phase, limit=16, name="phase")
        why = bound_text(self.why, limit=200, name="why")
        if secret_shape(method) or secret_shape(path) or secret_shape(why):
            raise Refuse("SECRET", "rejected")
        if method not in ("GET", "POST"):
            raise Refuse("METHOD", "rejected")
        if phase not in ("EXISTS", "DAY_ONE"):
            raise Refuse("PHASE", "rejected")
        if (
            not path.startswith("/")
            or path.startswith("//")
            or ".." in path
            or "?" in path
            or "#" in path
            or "\\" in path
            or " " in path
        ):
            raise Refuse("PATH", "rejected")
        if phase == "EXISTS" and path in _DAY_ONE_PATHS:
            raise Refuse("ROUTE", "core does not have this route yet")
        if phase == "DAY_ONE" and path not in _DAY_ONE_PATHS:
            raise Refuse("ROUTE", "unknown day-one path")
        if phase == "DAY_ONE" and why != _DAY_ONE_WHY:
            raise Refuse("ROUTE", "day-one why")


def _row(method: _Method, path: str, why: str) -> Route:
    return Route(method, path, "EXISTS", why)


def _gap(method: _Method, path: str) -> Route:
    # The chat window and the wizard need this route and Core does not have it yet.
    return Route(method, path, "DAY_ONE", _DAY_ONE_WHY)


_UNMEASURED = (
    "do_GET and do_POST return 501 from _ORC_UNMEASURED. GET never mkdir."
)

# Read order from the service: static allowlist, GET branches, POST branches.
# Both methods are separate rows when both handlers name the path.
_TABLE: tuple[Route, ...] = (
    _row("GET", "/", "Bearer-free shell. _STATIC_ROUTES serves mobile.html."),
    _row("GET", "/m", "Bearer-free alias of the mobile shell."),
    _row("GET", "/mobile", "Bearer-free alias of the mobile shell."),
    _row("GET", "/dash", "Bearer-free kdash index.html. Telemetry, not a wizard."),
    _row("GET", "/kdash_manifest.webmanifest", "Bearer-free PWA manifest allowlist entry."),
    _row("GET", "/kdash_sw.js", "Bearer-free service worker served at the root scope."),
    _row("GET", "/cosmos-voice.apk", "Bearer-free Android package on the service port."),
    _row("GET", "/cdeck", "GET redirects to /cdeck/ so relative cDeck hrefs stay under that prefix."),
    _row("GET", "/xtalk", "GET redirects to /xtalk/."),
    _row("GET", "/cdeck/", "Exact allowlist root for cDeck index.html."),
    _row("GET", "/xtalk/", "Exact allowlist root for the standalone XTalk page."),
    _row("GET", "/kill", "Bearer-free GET off switch. An optional kill token still gates it."),
    _row("GET", "/api/v1/control", "Bearer GET of control state for one client id."),
    _row("GET", "/api/v1/status", "Bearer GET of ready, root, tree id, and ledger head."),
    _row("GET", "/api/v1/audit", "Bearer GET of kernel.audit()."),
    _row("GET", "/api/v1/jobs", "Bearer GET of scheduler job states."),
    _row("GET", "/api/v1/health", "Bearer GET of HealthBoard.run()."),
    _row("GET", "/api/v1/spend", "Bearer GET of the spend audit. It changes no cap."),
    _row("GET", "/api/v1/tools", "Bearer GET of the ToolContracts registry report."),
    _row("GET", "/api/v1/tools_kit", "Bearer GET of the tools-kit snapshot."),
    _row("GET", "/api/v1/voice_loop", "Bearer GET of the voice-loop snapshot."),
    _row("GET", "/api/v1/events", "Bearer GET. Prefix match for the ledger tail since since_seq."),
    _row("GET", "/api/v1/rails", "Bearer GET of the registry matrix. Same branch as /api/v1/nodes."),
    _row("GET", "/api/v1/nodes", "Bearer GET of the registry matrix. Same branch as /api/v1/rails."),
    _row("GET", "/api/v1/surfaces", "Bearer GET of the surfaces report."),
    _row("GET", "/api/v1/surfaces_kit", "Bearer GET of the surfaces-kit snapshot."),
    _row("GET", "/api/v1/fleet", "Bearer GET. cDeck fleet panel handle_get."),
    _row("GET", "/api/v1/nodemap", "Bearer GET. cDeck nodemap panel, then a kernel overlay on 200."),
    _row("GET", "/api/v1/jukebox", "Bearer GET. cDeck jukebox panel."),
    _row("GET", "/api/v1/recents", "Bearer GET. cDeck recents panel. The query is passed through."),
    _row("GET", "/api/v1/makers", "Bearer GET. Exact path after a prefix check. find() does not mkdir."),
    _row("GET", "/api/v1/gitur", "Bearer GET of the gitur snapshot."),
    _row("GET", "/api/v1/crew", "Bearer GET of the crew roster snapshot."),
    _row("GET", "/api/v1/cred", "Bearer GET of the cred-kit snapshot. This row stores no secret."),
    _row("GET", "/api/v1/agents", "Bearer GET of agents_snapshot plus the tree id."),
    _row("GET", "/api/v1/mcp", "Bearer GET of named MCP servers."),
    _row("GET", "/api/v1/research_call", "Bearer GET of the research-call snapshot."),
    _row("GET", "/api/v1/studio", "Bearer GET of the studio snapshot."),
    _row("GET", "/api/v1/profiles", "Bearer GET of one profiles snapshot."),
    _row("GET", "/api/v1/backup", "Bearer GET of the backup fold snapshot."),
    _row("GET", "/api/v1/session_kit", "Bearer GET of the session-kit snapshot."),
    _row("GET", "/api/v1/session_tools", "Bearer GET of the session-tools snapshot."),
    _row("GET", "/api/v1/orc", "Bearer GET of the orc boot inspection."),
    _row("GET", "/api/v1/pilot", "Bearer GET of the pilot snapshot."),
    _row("GET", "/api/v1/xtalk", "Bearer GET of the xtalk snapshot."),
    _row("GET", "/api/v1/runs_ops", "Bearer GET of the runs-ops snapshot."),
    _row("GET", "/api/v1/review", "Bearer GET of the review snapshot."),
    _row("GET", "/api/v1/work_orders", "Bearer GET folding work orders."),
    _row("GET", "/api/v1/ccr/duty", "Bearer GET of the ccr duty report."),
    _row("GET", "/api/v1/stations", "Bearer GET of the stations snapshot."),
    _row("GET", "/api/v1/head", "Bearer GET of load_head."),
    _row("GET", "/api/v1/openrouter/routing", "Bearer GET of the OpenRouter routing record."),
    _row("GET", "/api/v1/model_rater/roles", "Bearer GET of the model-rater role scan."),
    _row("GET", "/api/v1/model_rater", "Bearer GET of the model-rater catalog snapshot."),
    _row("GET", "/api/v1/porosity", "Bearer GET of the porosity snapshot."),
    _row("GET", "/api/v1/womb/seat", "Bearer GET of one womb seat."),
    _row("GET", "/api/v1/womb/board", "Bearer GET of the womb board snapshot."),
    _row("GET", "/api/v1/usage", "Bearer GET of the OpenRouter usage snapshot."),
    _row("GET", "/api/v1/cvm/pull", "Bearer GET of the cvm pull projection. client_id is required."),
    _row("GET", "/api/v1/seats", _UNMEASURED),
    _row("GET", "/api/v1/approvals/pending", _UNMEASURED),
    _row("GET", "/api/v1/approvals/grant", _UNMEASURED),
    _row("GET", "/api/v1/approvals/deny", _UNMEASURED),
    _row("GET", "/api/v1/chamber", _UNMEASURED),
    _row("GET", "/api/v1/skills", _UNMEASURED),
    _row("GET", "/api/v1/temporal", _UNMEASURED),
    _row("GET", "/api/v1/sandbox", _UNMEASURED),
    _row("GET", "/api/v1/delegate", _UNMEASURED),
    _row("GET", "/api/v1/recall", _UNMEASURED),
    _row("POST", "/api/v1/kill", "POST off switch with no bearer. The body may carry a client id and a token."),
    _row("POST", "/api/v1/control/resume", "Bearer POST. Clears kill and pause. Does not reset the day spend cap."),
    _row("POST", "/api/v1/spend", "Bearer POST. Sets a rail cap or breaker thresholds. Not a second wallet."),
    _row("POST", "/api/v1/voice", "Bearer POST. Voice transcript seam. Control and spend run before any model."),
    _row("POST", "/api/v1/command", "Bearer POST. Text in, Commander.handle out."),
    _row("POST", "/api/v1/crucible", "Bearer POST. Queues a round only when critics are composed. Otherwise 501."),
    _row("POST", "/api/v1/research_call", "Bearer POST. Runs one research call."),
    _row("POST", "/api/v1/studio", "Bearer POST. Saves a studio pack."),
    _row("POST", "/api/v1/usage", "Bearer POST. Fetches one OpenRouter generation and may record usage."),
    _row("POST", "/api/v1/porosity", "Bearer POST. pair, trial, recommend, or coverage."),
    _row("POST", "/api/v1/profiles/bg", "Bearer POST. Forge background start or facilitate."),
    _row("POST", "/api/v1/profiles", "Bearer POST. Saves a profile engine."),
    _row("POST", "/api/v1/orc", "Bearer POST. Boots orc for one stream."),
    _row("POST", "/api/v1/xtalk", "Bearer POST. xtalk send. NOT_COMPOSED is 501."),
    _row("POST", "/api/v1/surfaces", "Bearer POST. Saves one surface."),
    _row("POST", "/api/v1/backup", "Bearer POST. Runs one backup action."),
    _row("POST", "/api/v1/session_tools", "Bearer POST. Runs one session-tools action."),
    _row("POST", "/api/v1/voice_loop", "Bearer POST. Saves a voice SOP."),
    _row("POST", "/api/v1/session_kit", "Bearer POST. Saves a session kit."),
    _row("POST", "/api/v1/work_orders/picked", "Bearer POST. Records a picked work order."),
    _row("POST", "/api/v1/jobs", "Bearer POST. Submits one scheduler command."),
    _row("POST", "/api/v1/makers", "Bearer POST. Adds one maker. 503 when the map is not composed."),
    _row("POST", "/api/v1/cvm/snapshot", "Bearer POST. Stores a phone snapshot. Does not append the ledger."),
    _row("POST", "/api/v1/cvm/push", "Bearer POST. Stores a push and stamps pull audio_owner. No ledger write."),
    _row("POST", "/api/v1/stations", "Bearer POST. Station, wish, board, floor, or rotation actions."),
    _row("POST", "/api/v1/openrouter/routing", "Bearer POST. Sets the OpenRouter routing priority."),
    _row("POST", "/api/v1/head", "Bearer POST. Sets the head record."),
    _row("POST", "/api/v1/model_rater/refresh", "Bearer POST. Refreshes the model-rater catalog."),
    _row("POST", "/api/v1/model_rater/seat", "Bearer POST. Assigns, adds, or removes a model-rater seat."),
    _row("POST", "/api/v1/model_rater/cap", "Bearer POST. Sets one model cap in the rater."),
    _row("POST", "/api/v1/model_rater/porosity", "Bearer POST. Records one porosity sample."),
    _row("POST", "/api/v1/model_rater/policy", "Bearer POST. Sets favored and banned model policy."),
    _row("POST", "/api/v1/model_rater/estimate", "Bearer POST. Estimates one model cost."),
    _row("POST", "/api/v1/model_rater/job_estimate", "Bearer POST. Saves or resets the job estimate."),
    _row("POST", "/api/v1/cred", "Bearer POST. set, delete, grab, custom, or a fold. This row stores no secret."),
    _row("POST", "/api/v1/seats", _UNMEASURED),
    _row("POST", "/api/v1/approvals/pending", _UNMEASURED),
    _row("POST", "/api/v1/approvals/grant", _UNMEASURED),
    _row("POST", "/api/v1/approvals/deny", _UNMEASURED),
    _row("POST", "/api/v1/chamber", _UNMEASURED),
    _row("POST", "/api/v1/skills", _UNMEASURED),
    _row("POST", "/api/v1/temporal", _UNMEASURED),
    _row("POST", "/api/v1/sandbox", _UNMEASURED),
    _row("POST", "/api/v1/delegate", _UNMEASURED),
    _row("POST", "/api/v1/recall", _UNMEASURED),
    _row("POST", "/api/v1/pilot", "Bearer POST. Captain seat turn. The handler forces role to captain."),
    _gap("GET", ROUTE_PAGE),
    _gap("POST", ROUTE_SETUP),
    _gap("POST", ROUTE_CHAT),
)


def table() -> tuple[Route, ...]:
    """Return the route table. Duplicates and a missing day-one row refuse."""
    seen: set[tuple[str, str]] = set()
    for route in _TABLE:
        key: tuple[str, str] = (route.method, route.path)
        if key in seen:
            raise Refuse("ROUTE", "duplicate")
        seen.add(key)
    required: tuple[tuple[str, str], ...] = (
        ("GET", ROUTE_PAGE),
        ("POST", ROUTE_SETUP),
        ("POST", ROUTE_CHAT),
    )
    for needed in required:
        if needed not in seen:
            raise Refuse("ROUTE", "missing day-one")
    return _TABLE


__all__ = ["SCHEMA", "Route", "table"]
