"""Provider routing: named model, explicit allowlist, no vendor fallthrough."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

import provider_routing
from cosmos_hermes import Refuse, secret_shape
from provider_routing import (
    ASK_CAP,
    BUDGET_CAP,
    CRED_CAP,
    FIELD_CAP,
    MODEL_CAP,
    NAME_CAP,
    POLICY_CAP,
    SCHEMA,
    Decision,
    Offer,
    Pin,
    Policy,
    RouteRecord,
    rebuild,
    route,
    snapshot,
)

_AT = 1_735_689_600
_CRED = "cred-lamp-note"
_KIMI = "moonshotai/kimi-k2.6"
_CLAUDE = "anthropic/claude-fable-5.1"
_GEMINI = "google/gemini-3"


def _offer(
    provider: str,
    model: str,
    cost: int,
    speed: int,
    latency: int,
    parameters: bool = True,
) -> Offer:
    return Offer(provider, model, cost, speed, latency, parameters)


def _policy(
    *,
    known: tuple[str, ...] = ("moonshotai", "together", "anthropic", "google"),
    only: tuple[str, ...] = ("moonshotai", "together", "anthropic", "google"),
    ignore: tuple[str, ...] = (),
    order: tuple[str, ...] = (),
    sort: str = "price",
    require_parameters: bool = False,
    data_collection: str = "deny",
    pins: tuple[Pin, ...] = (),
) -> Policy:
    return Policy(
        known=known,
        only=only,
        sort=sort,
        require_parameters=require_parameters,
        data_collection=data_collection,
        ignore=ignore,
        order=order,
        pins=pins,
    )


def _offers() -> tuple[Offer, ...]:
    return (
        _offer("together", _KIMI, 10, 95, 40),
        _offer("moonshotai", _KIMI, 25, 55, 20),
        _offer("anthropic", _CLAUDE, 40, 50, 30),
        _offer("google", _GEMINI, 15, 70, 25, parameters=False),
    )


def _go(
    model: object = _KIMI,
    allow: object = (_KIMI, _CLAUDE),
    offers: object | None = None,
    policy: object | None = None,
    *,
    cred_id: object = _CRED,
    surface: object = "openrouter",
    at: object = _AT,
    fence: object = 1,
    seen: object = 0,
    cap: object = POLICY_CAP,
    budget: object = BUDGET_CAP,
    provider: object = None,
) -> Decision:
    return route(
        model,
        allow,
        _offers() if offers is None else offers,
        _policy() if policy is None else policy,
        cred_id=cred_id,
        surface=surface,
        at=at,
        fence=fence,
        seen=seen,
        cap=cap,
        budget=budget,
        provider=provider,
    )


def _head(records: tuple[RouteRecord, ...]) -> RouteRecord:
    if len(records) != 1:
        raise AssertionError("expected one record")
    for item in records:
        return item
    raise AssertionError("empty snapshot")


def _story() -> tuple[Decision, str]:
    policy = _policy(
        known=("moonshotai", "together", "anthropic"),
        only=("moonshotai", "together"),
        order=("together", "moonshotai"),
        sort="throughput",
        require_parameters=True,
        pins=(Pin(_KIMI, only=("moonshotai",), sort="throughput"),),
    )
    offers = (
        _offer("moonshotai", _KIMI, 20, 55, 30),
        _offer("together", _KIMI, 10, 95, 15),
        _offer("anthropic", _CLAUDE, 40, 50, 40),
    )
    allow = (_KIMI, _CLAUDE)
    decision = route(
        "openrouter/moonshotai/kimi-k2.6",
        allow,
        offers,
        policy,
        cred_id=_CRED,
        surface="openrouter",
        at=_AT,
        fence=1,
        seen=0,
        budget=40,
    )
    try:
        route(
            "openai/gpt-6-astra",
            allow,
            offers,
            policy,
            cred_id=_CRED,
            surface="openrouter",
            at=_AT,
            fence=1,
            seen=0,
            budget=40,
        )
    except Refuse as refused:
        code = refused.code
    else:
        raise AssertionError("model outside the list must refuse")
    return decision, code


def test_schema_and_public_surface() -> None:
    assert SCHEMA == "cosmos-hermes-provider_routing/1"
    assert provider_routing.SCHEMA == SCHEMA
    assert provider_routing.__all__ == [
        "ASK_CAP",
        "BUDGET_CAP",
        "CRED_CAP",
        "Decision",
        "FIELD_CAP",
        "MODEL_CAP",
        "NAME_CAP",
        "Offer",
        "POLICY_CAP",
        "Pin",
        "Policy",
        "RouteRecord",
        "SCHEMA",
        "rebuild",
        "route",
        "snapshot",
    ]


def test_example_provider_routing() -> None:
    """A lamp-note session routes Kimi on an explicit card of models.

    The same story twice is equal. A model off that card refuses.
    Together stays unused even though it is faster and listed first.
    """
    first = _story()
    second = _story()
    assert first == second
    decision, code = first
    assert code == "NOT_ALLOWED"
    assert decision.schema == SCHEMA
    assert decision.model == "openrouter/moonshotai/kimi-k2.6"
    assert decision.provider == "moonshotai"
    assert decision.sort == "throughput"
    assert decision.score == 55
    assert decision.cost == 20
    assert decision.speed == 55
    assert decision.data_collection == "deny"
    assert decision.require_parameters is True
    assert decision.parameters is True
    assert decision.cred_id == _CRED
    assert decision.surface == "openrouter"
    assert decision.at == _AT
    assert decision.fence == 1
    assert decision.budget == 40
    assert decision.asked_budget == 40
    assert decision.budget_cap == BUDGET_CAP
    assert decision.cap == POLICY_CAP
    assert decision.policy_cap == POLICY_CAP
    assert decision.skipped == ()
    assert decision.provider != "together"
    assert decision.provider != "anthropic"
    assert rebuild(snapshot(decision)) == decision


def test_sort_ignore_order_and_name_tie() -> None:
    priced = _go()
    assert priced.provider == "together"
    assert priced.score == FIELD_CAP - 10
    assert priced.sort == "price"
    assert priced.skipped == ()
    again = _go()
    assert again == priced
    later = _go(at=_AT + 1)
    assert later != priced
    assert later.at == _AT + 1

    denied = _go(policy=_policy(ignore=("together",)))
    assert denied.provider == "moonshotai"
    assert denied.score == FIELD_CAP - 25

    ordered = _go(
        policy=_policy(order=("moonshotai", "together"), sort="throughput"),
    )
    assert ordered.provider == "moonshotai"
    assert ordered.sort == "throughput"
    assert ordered.score == 55

    tied = _go(
        model="lab/session-note",
        allow=("lab/session-note",),
        offers=(
            _offer("google", "lab/session-note", 10, 20, 99),
            _offer("anthropic", "lab/session-note", 10, 20, 1),
        ),
        policy=_policy(only=("anthropic", "google"), sort="price"),
    )
    assert tied.provider == "anthropic"
    assert tied.score == FIELD_CAP - 10

    slow = _go(
        allow=(_KIMI,),
        offers=(
            _offer("together", _KIMI, 10, 20, 80),
            _offer("moonshotai", _KIMI, 10, 20, 15),
        ),
        policy=_policy(only=("together", "moonshotai"), sort="latency"),
    )
    assert slow.provider == "moonshotai"
    assert slow.score == FIELD_CAP - 15

    plain = _go(
        model=_GEMINI,
        allow=(_GEMINI,),
        offers=(_offer("google", _GEMINI, 15, 70, 25, parameters=False),),
        policy=_policy(only=("google",), require_parameters=False, data_collection="allow"),
    )
    assert plain.provider == "google"
    assert plain.parameters is False
    assert plain.require_parameters is False
    assert plain.data_collection == "allow"


def test_budget_skips_too_large_and_keeps_a_later_offer() -> None:
    offers = (
        _offer("together", _KIMI, 90, 100, 10),
        _offer("moonshotai", _KIMI, 80, 50, 10),
        _offer("google", _KIMI, 5, 10, 10),
        _offer("anthropic", _CLAUDE, 1, 100, 1),
    )
    policy = _policy(sort="throughput")
    routed = _go(offers=offers, policy=policy, budget=20)
    assert routed.provider == "google"
    assert routed.skipped == ("together", "moonshotai")
    assert routed.budget == 20
    assert routed.score == 10
    assert "anthropic" not in routed.skipped

    with pytest.raises(Refuse) as other_model:
        _go(
            offers=(
                _offer("together", _KIMI, 40, 90, 10),
                _offer("moonshotai", _KIMI, 50, 80, 10),
                _offer("google", _GEMINI, 1, 100, 1),
            ),
            policy=_policy(sort="throughput"),
            budget=5,
        )
    assert other_model.value.code == "BUDGET"
    with pytest.raises(Refuse) as named_budget:
        _go(
            provider="together",
            budget=5,
            offers=(
                _offer("together", _KIMI, 40, 90, 10),
                _offer("moonshotai", _KIMI, 1, 10, 10),
            ),
        )
    assert named_budget.value.code == "BUDGET"

    ordered = _go(
        offers=(
            _offer("together", _KIMI, 90, 100, 10),
            _offer("moonshotai", _KIMI, 10, 20, 10),
        ),
        policy=_policy(order=("together", "moonshotai"), sort="throughput"),
        budget=20,
    )
    assert ordered.provider == "moonshotai"
    assert ordered.skipped == ("together",)

    free = _go(
        offers=(_offer("together", _KIMI, 0, 1, 1),),
        policy=_policy(only=("together",)),
        allow=(_KIMI,),
        budget=0,
    )
    assert free.provider == "together"
    assert free.budget == 0


def test_cap_is_recorded_and_not_raised() -> None:
    high = _go(cap=10_000, budget=ASK_CAP)
    assert high.cap == POLICY_CAP
    assert high.asked_cap == 10_000
    assert high.policy_cap == POLICY_CAP
    assert high.budget == BUDGET_CAP
    assert high.asked_budget == ASK_CAP
    assert high.budget_cap == BUDGET_CAP

    edge = _go(cap=ASK_CAP, budget=BUDGET_CAP)
    assert edge.cap == POLICY_CAP
    assert edge.asked_cap == ASK_CAP

    tight = _go(
        allow=(_KIMI,),
        offers=(_offer("together", _KIMI, 10, 10, 10),),
        policy=_policy(known=("together",), only=("together",)),
        cap=2,
        budget=10,
    )
    assert tight.cap == 2
    assert tight.asked_cap == 2
    assert tight.budget == 10

    wide = tuple(f"lab/model-{index}" for index in range(POLICY_CAP + 1))
    with pytest.raises(Refuse) as over_allow:
        _go(allow=wide, cap=10_000)
    assert over_allow.value.code == "OVERSIZE"
    assert over_allow.value.detail == str(POLICY_CAP)

    with pytest.raises(Refuse) as over_known:
        _go(
            policy=_policy(known=("together", "moonshotai", "anthropic", "google")),
            cap=2,
        )
    assert over_known.value.code == "OVERSIZE"
    assert over_known.value.detail == "2"

    with pytest.raises(Refuse) as ask:
        _go(cap=ASK_CAP + 1)
    assert ask.value.code == "OUT_OF_RANGE"
    assert ask.value.detail == f"1..{ASK_CAP}"
    with pytest.raises(Refuse) as flag:
        _go(cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as zero:
        _go(cap=0)
    assert zero.value.code == "OUT_OF_RANGE"


def test_unknown_provider_and_model_outside_do_not_fall_through() -> None:
    with pytest.raises(Refuse) as ghost:
        _policy(known=("anthropic",), only=("anthropic", "google"))
    assert ghost.value.code == "UNKNOWN_PROVIDER"

    with pytest.raises(Refuse) as offer:
        _go(
            offers=(
                _offer("deepinfra", _KIMI, 1, 100, 1),
                _offer("anthropic", _CLAUDE, 40, 50, 30),
            ),
            policy=_policy(known=("anthropic",), only=("anthropic",)),
            allow=(_KIMI, _CLAUDE),
        )
    assert offer.value.code == "UNKNOWN_PROVIDER"

    with pytest.raises(Refuse) as named:
        _go(provider="deepinfra")
    assert named.value.code == "UNKNOWN_PROVIDER"

    with pytest.raises(Refuse) as outside:
        _go(model="openai/gpt-6-astra")
    assert outside.value.code == "NOT_ALLOWED"
    assert outside.value.detail == "model"

    with pytest.raises(Refuse) as vendor:
        _go(
            model=_KIMI,
            provider="anthropic",
            policy=_policy(only=("moonshotai", "together", "anthropic", "google")),
        )
    assert vendor.value.code == "NO_PROVIDER"

    with pytest.raises(Refuse) as off_only:
        _go(
            model=_KIMI,
            policy=_policy(only=("anthropic",)),
        )
    assert off_only.value.code == "NOT_ALLOWED"
    assert off_only.value.detail == "provider"

    with pytest.raises(Refuse) as pinned:
        _go(model=_KIMI, provider="together", policy=_policy(only=("moonshotai",)))
    assert pinned.value.code == "NOT_ALLOWED"
    assert pinned.value.detail == "provider"

    kept = _go(model=_KIMI, provider="moonshotai", policy=_policy(only=("moonshotai",)))
    assert kept.provider == "moonshotai"
    assert kept.provider != "together"


def test_deny_order_params_spelling_and_pins() -> None:
    with pytest.raises(Refuse) as denied:
        _go(policy=_policy(ignore=("together", "moonshotai")))
    assert denied.value.code == "DENIED"
    with pytest.raises(Refuse) as named_deny:
        _go(provider="together", policy=_policy(ignore=("together",)))
    assert named_deny.value.code == "DENIED"

    with pytest.raises(Refuse) as fallback:
        _go(policy=_policy(order=("anthropic",)))
    assert fallback.value.code == "NO_FALLBACK"
    with pytest.raises(Refuse) as named_order:
        _go(provider="together", policy=_policy(order=("anthropic", "google")))
    assert named_order.value.code == "NO_FALLBACK"

    with pytest.raises(Refuse) as missing:
        _go(model=_GEMINI, allow=(_GEMINI, _KIMI), offers=_offers()[:3])
    assert missing.value.code == "NO_PROVIDER"
    with pytest.raises(Refuse) as pair:
        _go(
            model=_KIMI,
            provider="anthropic",
            offers=(_offer("anthropic", _CLAUDE, 10, 10, 10), _offer("together", _KIMI, 10, 10, 10)),
            policy=_policy(only=("anthropic", "together")),
        )
    assert pair.value.code == "NO_PROVIDER"

    with pytest.raises(Refuse) as params:
        _go(
            offers=(_offer("together", _KIMI, 10, 90, 10, parameters=False),),
            policy=_policy(only=("together",), require_parameters=True),
            allow=(_KIMI,),
        )
    assert params.value.code == "PARAMS"
    with pytest.raises(Refuse) as named_params:
        _go(
            offers=(
                _offer("together", _KIMI, 10, 90, 10, parameters=False),
                _offer("moonshotai", _KIMI, 20, 10, 10, parameters=True),
            ),
            policy=_policy(require_parameters=True),
            provider="together",
        )
    assert named_params.value.code == "PARAMS"
    served = _go(
        offers=(
            _offer("together", _KIMI, 10, 90, 10, parameters=False),
            _offer("moonshotai", _KIMI, 20, 10, 10, parameters=True),
        ),
        policy=_policy(sort="throughput", require_parameters=True),
    )
    assert served.provider == "moonshotai"
    assert served.parameters is True

    spelled = _go(
        model="openrouter/anthropic/claude-fable-5-1",
        allow=(_CLAUDE,),
        offers=(_offer("anthropic", _CLAUDE, 40, 50, 30),),
        policy=_policy(only=("anthropic",)),
    )
    assert spelled.provider == "anthropic"
    assert spelled.model == "openrouter/anthropic/claude-fable-5-1"

    pinned = _go(
        policy=_policy(
            sort="price",
            data_collection="deny",
            require_parameters=False,
            pins=(
                Pin(
                    "openrouter/moonshotai/kimi-k2-6",
                    only=("moonshotai",),
                    ignore=(),
                    order=(),
                    sort="latency",
                    require_parameters=True,
                    data_collection="allow",
                ),
            ),
        ),
    )
    assert pinned.provider == "moonshotai"
    assert pinned.sort == "latency"
    assert pinned.score == FIELD_CAP - 20
    assert pinned.data_collection == "allow"
    assert pinned.require_parameters is True


def test_shape_secret_and_empty_refusals() -> None:
    with pytest.raises(Refuse) as portal:
        _go(surface="portal")
    assert portal.value.code == "NOT_OPENROUTER"
    with pytest.raises(Refuse) as direct:
        _go(surface="direct")
    assert direct.value.code == "NOT_OPENROUTER"
    with pytest.raises(Refuse) as surface:
        _go(surface="aggregator")
    assert surface.value.code == "BAD_SURFACE"
    with pytest.raises(Refuse) as blank_surface:
        _go(surface="")
    assert blank_surface.value.code == "BAD_SURFACE"

    with pytest.raises(Refuse) as cred:
        _go(cred_id="")
    assert cred.value.code == "MISSING_CRED"
    with pytest.raises(Refuse) as bad_cred:
        _go(cred_id="cred-")
    assert bad_cred.value.code == "BAD_CRED"
    with pytest.raises(Refuse) as secret_cred:
        _go(cred_id="sk-livekeyvalue")
    assert secret_cred.value.code == "SECRET"
    assert "sk-" not in str(secret_cred.value)

    with pytest.raises(Refuse) as secret_model:
        _go(model="sk-livekeyvalue")
    assert secret_model.value.code == "SECRET"
    with pytest.raises(Refuse) as bearer:
        _go(model="Bearer abcdefghijk")
    assert bearer.value.code == "SECRET"
    with pytest.raises(Refuse) as assigned:
        _go(allow=("api_key=supersecret",))
    assert assigned.value.code == "SECRET"

    with pytest.raises(Refuse) as empty_model:
        _go(model="")
    assert empty_model.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as split:
        _go(model="openai/gpt/extra")
    assert split.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as slash:
        _go(model="openai/")
    assert slash.value.code == "BAD_MODEL"
    with pytest.raises(Refuse) as upper:
        Offer("Anthropic", _CLAUDE, 0, 0, 0, True)
    assert upper.value.code == "BAD_PROVIDER"
    with pytest.raises(Refuse) as empty_provider:
        Offer("", _CLAUDE, 0, 0, 0, True)
    assert empty_provider.value.code == "BAD_PROVIDER"

    with pytest.raises(Refuse) as bad_list:
        _go(allow=_KIMI)
    assert bad_list.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as bad_offers:
        _go(offers=_KIMI)
    assert bad_offers.value.code == "BAD_LIST"
    with pytest.raises(Refuse) as bad_offer:
        _go(offers=("together",))
    assert bad_offer.value.code == "BAD_OFFER"
    with pytest.raises(Refuse) as bad_policy:
        route(
            _KIMI,
            (_KIMI,),
            _offers(),
            None,
            cred_id=_CRED,
            surface="openrouter",
            at=_AT,
            fence=1,
            seen=0,
        )
    assert bad_policy.value.code == "BAD_POLICY"
    with pytest.raises(Refuse) as bad_pin:
        _policy(pins=(_offer("together", _KIMI, 1, 1, 1),))  # type: ignore[arg-type]
    assert bad_pin.value.code == "BAD_PIN"

    with pytest.raises(Refuse) as empty_allow:
        _go(allow=())
    assert empty_allow.value.code == "EMPTY_ALLOW"
    with pytest.raises(Refuse) as empty_only:
        _policy(only=())
    assert empty_only.value.code == "EMPTY_ONLY"
    with pytest.raises(Refuse) as empty_known:
        _policy(known=())
    assert empty_known.value.code == "EMPTY_KNOWN"
    with pytest.raises(Refuse) as pin_only:
        Pin(_KIMI, only=())
    assert pin_only.value.code == "EMPTY_ONLY"

    with pytest.raises(Refuse) as sort:
        _policy(sort="Price")
    assert sort.value.code == "BAD_SORT"
    with pytest.raises(Refuse) as collection:
        _policy(data_collection="null")
    assert collection.value.code == "BAD_COLLECTION"
    with pytest.raises(Refuse) as flag:
        _policy(require_parameters=1)  # type: ignore[arg-type]
    assert flag.value.code == "BAD_FLAG"
    with pytest.raises(Refuse) as offer_flag:
        Offer("together", _KIMI, 0, 0, 0, 1)  # type: ignore[arg-type]
    assert offer_flag.value.code == "BAD_FLAG"

    with pytest.raises(Refuse) as dup_allow:
        _go(allow=(_CLAUDE, "openrouter/anthropic/claude-fable-5-1"))
    assert dup_allow.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as dup_known:
        _policy(known=("anthropic", "anthropic"), only=("anthropic",))
    assert dup_known.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as dup_offer:
        _go(
            offers=(
                _offer("together", _KIMI, 1, 1, 1),
                _offer("together", "openrouter/moonshotai/kimi-k2-6", 2, 2, 2),
            ),
            policy=_policy(only=("together",)),
            allow=(_KIMI,),
        )
    assert dup_offer.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as dup_pin:
        _policy(
            pins=(
                Pin(_CLAUDE),
                Pin("openrouter/anthropic/claude-fable-5-1"),
            )
        )
    assert dup_pin.value.code == "DUPLICATE"

    with pytest.raises(Refuse) as nul:
        _go(model="a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as text:
        _go(model=None)
    assert text.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as over_name:
        Offer("n" * (NAME_CAP + 1), _KIMI, 0, 0, 0, True)
    assert over_name.value.code == "OVERSIZE"
    assert over_name.value.detail == str(NAME_CAP)
    with pytest.raises(Refuse) as over_model:
        Offer("together", "m" * (MODEL_CAP + 1), 0, 0, 0, True)
    assert over_model.value.code == "OVERSIZE"
    assert over_model.value.detail == str(MODEL_CAP)
    with pytest.raises(Refuse) as over_cred:
        _go(cred_id="c" * (CRED_CAP + 1))
    assert over_cred.value.code == "OVERSIZE"
    with pytest.raises(Refuse) as high:
        Offer("together", _KIMI, FIELD_CAP + 1, 0, 0, True)
    assert high.value.code == "OUT_OF_RANGE"
    assert high.value.detail == f"0..{FIELD_CAP}"
    with pytest.raises(Refuse) as low:
        Offer("together", _KIMI, -1, 0, 0, True)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as stale:
        _go(fence=1, seen=1)
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as gap:
        _go(fence=3, seen=1)
    assert gap.value.code == "STALE"
    stepped = _go(fence=2, seen=1)
    assert stepped.fence == 2


def test_rebuild_forged_records_and_repr() -> None:
    decision = _go(budget=30)
    assert rebuild(snapshot(decision)) == decision
    record = _head(snapshot(decision))
    with pytest.raises(Refuse) as empty:
        rebuild(())
    assert empty.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as missing:
        rebuild(None)
    assert missing.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as text:
        snapshot("route")
    assert text.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as row:
        rebuild((decision,))
    assert row.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as duplicate:
        rebuild((record, record))
    assert duplicate.value.code == "DUPLICATE"
    with pytest.raises(Refuse) as score:
        replace(record, score=record.score + 1)
    assert score.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as schema:
        replace(decision, schema="cosmos-hermes-provider_routing/2")
    assert schema.value.code == "BAD_RECORD"
    with pytest.raises(Refuse) as cap:
        replace(decision, cap=decision.cap + 1)
    assert cap.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as budget:
        replace(decision, budget=decision.budget + 1)
    assert budget.value.code == "BAD_CAP"
    with pytest.raises(Refuse) as broken:
        replace(record, digest="ab" * 32)
    assert broken.value.code == "BROKEN"

    text_repr = repr(decision) + repr(record) + repr(_policy())
    assert "sk-" not in text_repr
    assert "Bearer" not in text_repr
    assert "api_key=" not in text_repr
    assert secret_shape(text_repr) is False
    assert not hasattr(decision, "__dict__")
    assert not hasattr(record, "__dict__")
    with pytest.raises(AttributeError):
        setattr(decision, "provider", "google")


def test_module_imports_stay_local() -> None:
    source = Path(provider_routing.__file__ or "").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.add(node.module.split(".")[0])
    assert modules <= {
        "__future__",
        "collections",
        "cosmos_hermes",
        "dataclasses",
        "hashlib",
        "re",
    }
