"""Route one named model to a catalogued provider.

No network. An unknown provider refuses. A model outside the explicit
allowlist refuses. This module does not substitute another vendor.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from dataclasses import dataclass

from cosmos_hermes import Refuse, bound_int, bound_text, const_eq, secret_shape

SCHEMA = "cosmos-hermes-provider_routing/1"
POLICY_CAP = 32
BUDGET_CAP = 100
FIELD_CAP = 100
NAME_CAP = 64
MODEL_CAP = 128
CRED_CAP = 68
ASK_CAP = 1_000_000
_FENCE_MAX = 1_000_000_000
_AT_MAX = 4_102_444_800
_PREFIX = "openrouter/"

_MODEL_RE = re.compile(r"^[a-z0-9][a-z0-9._:/-]{0,127}$")
_PROVIDER_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
_CRED_RE = re.compile(r"^cred-[a-z0-9][a-z0-9-]{0,62}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_SORTS = frozenset({"price", "throughput", "latency"})
_COLLECTIONS = frozenset({"allow", "deny"})
_CLOSED_SURFACES = frozenset({"portal", "direct"})


def _assign(host: object, name: str, value: object) -> None:
    object.__setattr__(host, name, value)


def _within(length: int, cap: int) -> None:
    if length > cap:
        raise Refuse("OVERSIZE", str(cap))


def _model_key(text: str) -> str:
    body = text[len(_PREFIX) :] if text.startswith(_PREFIX) else text
    parts = body.split("/")
    if len(parts) != 2 or parts[0] == "" or parts[1] == "":
        raise Refuse("BAD_MODEL")
    if ".." in parts[0] or ".." in parts[1]:
        raise Refuse("BAD_MODEL")
    return body.replace(".", "-")


def _model(value: object) -> str:
    text = bound_text(value, MODEL_CAP)
    if text == "":
        raise Refuse("BAD_MODEL")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _MODEL_RE.fullmatch(text) is None:
        raise Refuse("BAD_MODEL")
    _model_key(text)
    return text


def _provider(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if text == "":
        raise Refuse("BAD_PROVIDER")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _PROVIDER_RE.fullmatch(text) is None:
        raise Refuse("BAD_PROVIDER")
    return text


def _cred(value: object) -> str:
    text = bound_text(value, CRED_CAP)
    if text == "":
        raise Refuse("MISSING_CRED")
    if secret_shape(text):
        raise Refuse("SECRET")
    if _CRED_RE.fullmatch(text) is None:
        raise Refuse("BAD_CRED")
    return text


def _surface(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text in _CLOSED_SURFACES:
        raise Refuse("NOT_OPENROUTER")
    if text != "openrouter":
        raise Refuse("BAD_SURFACE")
    return text


def _sort(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _SORTS:
        raise Refuse("BAD_SORT")
    return text


def _collection(value: object) -> str:
    text = bound_text(value, NAME_CAP)
    if secret_shape(text):
        raise Refuse("SECRET")
    if text not in _COLLECTIONS:
        raise Refuse("BAD_COLLECTION")
    return text


def _flag(value: object) -> bool:
    if type(value) is not bool:
        raise Refuse("BAD_FLAG")
    return value


def _as_seq(value: object, code: str) -> Sequence[object]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise Refuse(code)
    return value


def _provider_tuple(value: object, *, empty: str | None, cap: int) -> tuple[str, ...]:
    seq = _as_seq(value, "BAD_LIST")
    _within(len(seq), cap)
    found: list[str] = []
    seen: set[str] = set()
    for item in seq:
        name = _provider(item)
        if name in seen:
            raise Refuse("DUPLICATE")
        seen.add(name)
        found.append(name)
    if empty is not None and not found:
        raise Refuse(empty)
    return tuple(found)


def _require_known(names: tuple[str, ...] | None, catalog: set[str]) -> None:
    if names is None:
        return
    for name in names:
        if name not in catalog:
            raise Refuse("UNKNOWN_PROVIDER")


def _ceiling(value: object, policy: int, lo: int) -> tuple[int, int]:
    asked = bound_int(value, lo, ASK_CAP)
    applied = policy if asked > policy else asked
    return applied, asked


def _fence_pair(fence: object, seen: object) -> int:
    fence_i = bound_int(fence, 1, _FENCE_MAX)
    seen_i = bound_int(seen, 0, _FENCE_MAX)
    if fence_i != seen_i + 1:
        raise Refuse("STALE")
    return fence_i


def _score(sort: str, cost: int, speed: int, latency: int) -> int:
    if sort == "price":
        return FIELD_CAP - cost
    if sort == "throughput":
        return speed
    if sort == "latency":
        return FIELD_CAP - latency
    raise Refuse("BAD_SORT")


def _rank(offer: Offer, sort: str, order_index: dict[str, int]) -> tuple[int, int, str]:
    position = order_index.get(offer.provider, 0) if order_index else 0
    if sort == "price":
        metric = offer.cost
    elif sort == "throughput":
        metric = -offer.speed
    else:
        metric = offer.latency
    return (position, metric, offer.provider)


def _digest(
    schema: str,
    model: str,
    provider: str,
    sort: str,
    score: int,
    cost: int,
    speed: int,
    latency: int,
    data_collection: str,
    require_parameters: bool,
    parameters: bool,
    cred_id: str,
    surface: str,
    at: int,
    fence: int,
    cap: int,
    asked_cap: int,
    policy_cap: int,
    budget: int,
    asked_budget: int,
    budget_cap: int,
    skipped: tuple[str, ...],
) -> str:
    body = "\n".join(
        (
            schema,
            model,
            provider,
            sort,
            str(score),
            str(cost),
            str(speed),
            str(latency),
            data_collection,
            "1" if require_parameters else "0",
            "1" if parameters else "0",
            cred_id,
            surface,
            str(at),
            str(fence),
            str(cap),
            str(asked_cap),
            str(policy_cap),
            str(budget),
            str(asked_budget),
            str(budget_cap),
            ",".join(skipped),
        )
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _check_skipped(skipped: object, provider: str) -> tuple[str, ...]:
    if type(skipped) is not tuple:
        raise Refuse("BAD_RECORD")
    seen: set[str] = set()
    names: list[str] = []
    for item in skipped:
        name = _provider(item)
        if name in seen or name == provider:
            raise Refuse("BAD_RECORD")
        seen.add(name)
        names.append(name)
    return tuple(names)


def _validate(
    schema: object,
    model: object,
    provider: object,
    sort: object,
    score: object,
    cost: object,
    speed: object,
    latency: object,
    data_collection: object,
    require_parameters: object,
    parameters: object,
    cred_id: object,
    surface: object,
    at: object,
    fence: object,
    cap: object,
    asked_cap: object,
    policy_cap: object,
    budget: object,
    asked_budget: object,
    budget_cap: object,
    skipped: object,
    digest: object,
) -> None:
    if type(schema) is not str or schema != SCHEMA:
        raise Refuse("BAD_RECORD")
    model_text = _model(model)
    provider_text = _provider(provider)
    sort_text = _sort(sort)
    collection = _collection(data_collection)
    require = _flag(require_parameters)
    serves = _flag(parameters)
    cred = _cred(cred_id)
    surface_text = _surface(surface)
    cost_i = bound_int(cost, 0, FIELD_CAP)
    speed_i = bound_int(speed, 0, FIELD_CAP)
    latency_i = bound_int(latency, 0, FIELD_CAP)
    at_i = bound_int(at, 0, _AT_MAX)
    fence_i = bound_int(fence, 1, _FENCE_MAX)
    asked_cap_i = bound_int(asked_cap, 1, ASK_CAP)
    asked_budget_i = bound_int(asked_budget, 0, ASK_CAP)
    if type(policy_cap) is not int or type(budget_cap) is not int:
        raise Refuse("NOT_INT")
    if type(cap) is not int or type(budget) is not int or type(score) is not int:
        raise Refuse("NOT_INT")
    if policy_cap != POLICY_CAP or budget_cap != BUDGET_CAP:
        raise Refuse("BAD_CAP")
    expected_cap = POLICY_CAP if asked_cap_i > POLICY_CAP else asked_cap_i
    expected_budget = BUDGET_CAP if asked_budget_i > BUDGET_CAP else asked_budget_i
    if cap != expected_cap or budget != expected_budget:
        raise Refuse("BAD_CAP")
    if score != _score(sort_text, cost_i, speed_i, latency_i):
        raise Refuse("BAD_RECORD")
    names = _check_skipped(skipped, provider_text)
    if type(digest) is not str or _DIGEST_RE.fullmatch(digest) is None:
        raise Refuse("BAD_RECORD")
    expected = _digest(
        SCHEMA,
        model_text,
        provider_text,
        sort_text,
        score,
        cost_i,
        speed_i,
        latency_i,
        collection,
        require,
        serves,
        cred,
        surface_text,
        at_i,
        fence_i,
        cap,
        asked_cap_i,
        POLICY_CAP,
        budget,
        asked_budget_i,
        BUDGET_CAP,
        names,
    )
    if not const_eq(digest, expected):
        raise Refuse("BROKEN")


@dataclass(frozen=True, slots=True)
class Offer:
    """One provider's measured row for one model. Costs are 0..FIELD_CAP."""

    provider: str
    model: str
    cost: int
    speed: int
    latency: int
    parameters: bool

    def __post_init__(self) -> None:
        provider = _provider(self.provider)
        model = _model(self.model)
        cost = bound_int(self.cost, 0, FIELD_CAP)
        speed = bound_int(self.speed, 0, FIELD_CAP)
        latency = bound_int(self.latency, 0, FIELD_CAP)
        parameters = _flag(self.parameters)
        _assign(self, "provider", provider)
        _assign(self, "model", model)
        _assign(self, "cost", cost)
        _assign(self, "speed", speed)
        _assign(self, "latency", latency)
        _assign(self, "parameters", parameters)


@dataclass(frozen=True, slots=True)
class Pin:
    """Per-model overrides. None inherits the policy field."""

    model: str
    only: tuple[str, ...] | None = None
    ignore: tuple[str, ...] | None = None
    order: tuple[str, ...] | None = None
    sort: str | None = None
    require_parameters: bool | None = None
    data_collection: str | None = None

    def __post_init__(self) -> None:
        model = _model(self.model)
        only = None if self.only is None else _provider_tuple(self.only, empty="EMPTY_ONLY", cap=POLICY_CAP)
        ignore = None if self.ignore is None else _provider_tuple(self.ignore, empty=None, cap=POLICY_CAP)
        order = None if self.order is None else _provider_tuple(self.order, empty=None, cap=POLICY_CAP)
        sort = None if self.sort is None else _sort(self.sort)
        if self.require_parameters is not None:
            _flag(self.require_parameters)
        collection = None if self.data_collection is None else _collection(self.data_collection)
        _assign(self, "model", model)
        _assign(self, "only", only)
        _assign(self, "ignore", ignore)
        _assign(self, "order", order)
        _assign(self, "sort", sort)
        _assign(self, "data_collection", collection)


def _pins(value: object, cap: int) -> tuple[Pin, ...]:
    seq = _as_seq(value, "BAD_PIN")
    _within(len(seq), cap)
    found: list[Pin] = []
    seen: set[str] = set()
    for item in seq:
        if type(item) is not Pin:
            raise Refuse("BAD_PIN")
        key = _model_key(item.model)
        if key in seen:
            raise Refuse("DUPLICATE")
        seen.add(key)
        found.append(item)
    return tuple(found)


@dataclass(frozen=True, slots=True)
class Policy:
    """Aggregator rules. `known` is the catalog. `only` is the provider allowlist."""

    known: tuple[str, ...]
    only: tuple[str, ...]
    sort: str
    require_parameters: bool
    data_collection: str
    ignore: tuple[str, ...] = ()
    order: tuple[str, ...] = ()
    pins: tuple[Pin, ...] = ()

    def __post_init__(self) -> None:
        known = _provider_tuple(self.known, empty="EMPTY_KNOWN", cap=POLICY_CAP)
        only = _provider_tuple(self.only, empty="EMPTY_ONLY", cap=POLICY_CAP)
        ignore = _provider_tuple(self.ignore, empty=None, cap=POLICY_CAP)
        order = _provider_tuple(self.order, empty=None, cap=POLICY_CAP)
        sort = _sort(self.sort)
        require_parameters = _flag(self.require_parameters)
        data_collection = _collection(self.data_collection)
        pins = _pins(self.pins, POLICY_CAP)
        catalog = set(known)
        for name in only + ignore + order:
            if name not in catalog:
                raise Refuse("UNKNOWN_PROVIDER")
        for pin in pins:
            _require_known(pin.only, catalog)
            _require_known(pin.ignore, catalog)
            _require_known(pin.order, catalog)
        _assign(self, "known", known)
        _assign(self, "only", only)
        _assign(self, "ignore", ignore)
        _assign(self, "order", order)
        _assign(self, "sort", sort)
        _assign(self, "require_parameters", require_parameters)
        _assign(self, "data_collection", data_collection)
        _assign(self, "pins", pins)


@dataclass(frozen=True, slots=True)
class RouteRecord:
    """One emitted row. `rebuild` accepts a single record."""

    schema: str
    model: str
    provider: str
    sort: str
    score: int
    cost: int
    speed: int
    latency: int
    data_collection: str
    require_parameters: bool
    parameters: bool
    cred_id: str
    surface: str
    at: int
    fence: int
    cap: int
    asked_cap: int
    policy_cap: int
    budget: int
    asked_budget: int
    budget_cap: int
    skipped: tuple[str, ...]
    digest: str

    def __post_init__(self) -> None:
        _validate(
            self.schema,
            self.model,
            self.provider,
            self.sort,
            self.score,
            self.cost,
            self.speed,
            self.latency,
            self.data_collection,
            self.require_parameters,
            self.parameters,
            self.cred_id,
            self.surface,
            self.at,
            self.fence,
            self.cap,
            self.asked_cap,
            self.policy_cap,
            self.budget,
            self.asked_budget,
            self.budget_cap,
            self.skipped,
            self.digest,
        )


@dataclass(frozen=True, slots=True)
class Decision:
    """The provider a later rail may name. `cap` and `budget` are policy values."""

    schema: str
    model: str
    provider: str
    sort: str
    score: int
    cost: int
    speed: int
    latency: int
    data_collection: str
    require_parameters: bool
    parameters: bool
    cred_id: str
    surface: str
    at: int
    fence: int
    cap: int
    asked_cap: int
    policy_cap: int
    budget: int
    asked_budget: int
    budget_cap: int
    skipped: tuple[str, ...]
    digest: str

    def __post_init__(self) -> None:
        _validate(
            self.schema,
            self.model,
            self.provider,
            self.sort,
            self.score,
            self.cost,
            self.speed,
            self.latency,
            self.data_collection,
            self.require_parameters,
            self.parameters,
            self.cred_id,
            self.surface,
            self.at,
            self.fence,
            self.cap,
            self.asked_cap,
            self.policy_cap,
            self.budget,
            self.asked_budget,
            self.budget_cap,
            self.skipped,
            self.digest,
        )


def _fit(policy: Policy, cap: int) -> None:
    _within(len(policy.known), cap)
    _within(len(policy.only), cap)
    _within(len(policy.ignore), cap)
    _within(len(policy.order), cap)
    _within(len(policy.pins), cap)
    for pin in policy.pins:
        if pin.only is not None:
            _within(len(pin.only), cap)
        if pin.ignore is not None:
            _within(len(pin.ignore), cap)
        if pin.order is not None:
            _within(len(pin.order), cap)


def _allow(value: object, cap: int) -> set[str]:
    seq = _as_seq(value, "BAD_LIST")
    _within(len(seq), cap)
    keys: set[str] = set()
    for item in seq:
        key = _model_key(_model(item))
        if key in keys:
            raise Refuse("DUPLICATE")
        keys.add(key)
    if not keys:
        raise Refuse("EMPTY_ALLOW")
    return keys


def _load_offers(
    value: object,
    cap: int,
    catalog: set[str],
) -> tuple[dict[str, tuple[Offer, ...]], dict[tuple[str, str], Offer]]:
    seq = _as_seq(value, "BAD_LIST")
    _within(len(seq), cap)
    grouped: dict[str, list[Offer]] = {}
    pairs: dict[tuple[str, str], Offer] = {}
    for item in seq:
        if type(item) is not Offer:
            raise Refuse("BAD_OFFER")
        if item.provider not in catalog:
            raise Refuse("UNKNOWN_PROVIDER")
        key = _model_key(item.model)
        pair = (item.provider, key)
        if pair in pairs:
            raise Refuse("DUPLICATE")
        pairs[pair] = item
        bucket = grouped.get(key)
        if bucket is None:
            grouped[key] = [item]
        else:
            bucket.append(item)
    frozen = {key: tuple(items) for key, items in grouped.items()}
    return frozen, pairs


def _merge(
    policy: Policy,
    model_key: str,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], str, bool, str]:
    pin: Pin | None = None
    for item in policy.pins:
        if _model_key(item.model) == model_key:
            pin = item
            break
    if pin is None:
        return (
            policy.only,
            policy.ignore,
            policy.order,
            policy.sort,
            policy.require_parameters,
            policy.data_collection,
        )
    only = policy.only if pin.only is None else pin.only
    ignore = policy.ignore if pin.ignore is None else pin.ignore
    order = policy.order if pin.order is None else pin.order
    sort = policy.sort if pin.sort is None else pin.sort
    require = policy.require_parameters if pin.require_parameters is None else pin.require_parameters
    collection = policy.data_collection if pin.data_collection is None else pin.data_collection
    return (only, ignore, order, sort, require, collection)


def _pick(
    pool: Sequence[Offer],
    sort: str,
    order_index: dict[str, int],
    budget: int,
) -> tuple[Offer, tuple[str, ...]]:
    def _key(offer: Offer) -> tuple[int, int, str]:
        return _rank(offer, sort, order_index)

    skipped: list[str] = []
    for offer in sorted(pool, key=_key):
        if offer.cost > budget:
            skipped.append(offer.provider)
            continue
        return offer, tuple(skipped)
    raise Refuse("BUDGET")


def _seal(
    model: str,
    offer: Offer,
    sort: str,
    collection: str,
    require: bool,
    cred_id: str,
    surface: str,
    at: int,
    fence: int,
    cap: int,
    asked_cap: int,
    budget: int,
    asked_budget: int,
    skipped: tuple[str, ...],
) -> Decision:
    score = _score(sort, offer.cost, offer.speed, offer.latency)
    digest = _digest(
        SCHEMA,
        model,
        offer.provider,
        sort,
        score,
        offer.cost,
        offer.speed,
        offer.latency,
        collection,
        require,
        offer.parameters,
        cred_id,
        surface,
        at,
        fence,
        cap,
        asked_cap,
        POLICY_CAP,
        budget,
        asked_budget,
        BUDGET_CAP,
        skipped,
    )
    return Decision(
        schema=SCHEMA,
        model=model,
        provider=offer.provider,
        sort=sort,
        score=score,
        cost=offer.cost,
        speed=offer.speed,
        latency=offer.latency,
        data_collection=collection,
        require_parameters=require,
        parameters=offer.parameters,
        cred_id=cred_id,
        surface=surface,
        at=at,
        fence=fence,
        cap=cap,
        asked_cap=asked_cap,
        policy_cap=POLICY_CAP,
        budget=budget,
        asked_budget=asked_budget,
        budget_cap=BUDGET_CAP,
        skipped=skipped,
        digest=digest,
    )


def _automatic(
    matched: Sequence[Offer],
    only_set: set[str],
    ignore_set: set[str],
    order: tuple[str, ...],
    order_index: dict[str, int],
    sort: str,
    require: bool,
    budget: int,
) -> tuple[Offer, tuple[str, ...]]:
    if not matched:
        raise Refuse("NO_PROVIDER")
    on_only = tuple(item for item in matched if item.provider in only_set)
    if not on_only:
        raise Refuse("NOT_ALLOWED", "provider")
    visible = tuple(item for item in on_only if item.provider not in ignore_set)
    if not visible:
        raise Refuse("DENIED")
    if order:
        ordered = tuple(item for item in visible if item.provider in order_index)
        if not ordered:
            raise Refuse("NO_FALLBACK")
    else:
        ordered = visible
    if require:
        supported = tuple(item for item in ordered if item.parameters)
        if not supported:
            raise Refuse("PARAMS")
    else:
        supported = ordered
    return _pick(supported, sort, order_index if order else {}, budget)


def _named(
    named: str,
    model_key: str,
    pairs: dict[tuple[str, str], Offer],
    only_set: set[str],
    ignore_set: set[str],
    order: tuple[str, ...],
    order_index: dict[str, int],
    require: bool,
    budget: int,
) -> Offer:
    if named not in only_set:
        raise Refuse("NOT_ALLOWED", "provider")
    if named in ignore_set:
        raise Refuse("DENIED")
    if order and named not in order_index:
        raise Refuse("NO_FALLBACK")
    chosen = pairs.get((named, model_key))
    if chosen is None:
        raise Refuse("NO_PROVIDER")
    if require and not chosen.parameters:
        raise Refuse("PARAMS")
    if chosen.cost > budget:
        raise Refuse("BUDGET")
    return chosen


def route(
    model: object,
    allow: object,
    offers: object,
    policy: object,
    *,
    cred_id: object,
    surface: object,
    at: object,
    fence: object,
    seen: object,
    cap: object = POLICY_CAP,
    budget: object = BUDGET_CAP,
    provider: object = None,
) -> Decision:
    """Choose one provider for `model` or refuse.

    `allow` is the model allowlist. A model absent from it is `NOT_ALLOWED`.
    A provider absent from `Policy.known` is `UNKNOWN_PROVIDER`. The result
    never names a vendor that does not offer that model.
    """
    surface_text = _surface(surface)
    cred = _cred(cred_id)
    at_i = bound_int(at, 0, _AT_MAX)
    fence_i = _fence_pair(fence, seen)
    applied_cap, asked_cap = _ceiling(cap, POLICY_CAP, 1)
    applied_budget, asked_budget = _ceiling(budget, BUDGET_CAP, 0)
    model_text = _model(model)
    model_key = _model_key(model_text)
    if type(policy) is not Policy:
        raise Refuse("BAD_POLICY")
    _fit(policy, applied_cap)
    allow_keys = _allow(allow, applied_cap)
    catalog = set(policy.known)
    grouped, pairs = _load_offers(offers, applied_cap, catalog)
    named: str | None
    if provider is not None:
        named = _provider(provider)
        if named not in catalog:
            raise Refuse("UNKNOWN_PROVIDER")
    else:
        named = None
    if model_key not in allow_keys:
        raise Refuse("NOT_ALLOWED", "model")
    only, ignore, order, sort, require, collection = _merge(policy, model_key)
    only_set = set(only)
    ignore_set = set(ignore)
    order_index = {name: index for index, name in enumerate(order)}
    if named is None:
        chosen, skipped = _automatic(
            grouped.get(model_key, ()),
            only_set,
            ignore_set,
            order,
            order_index,
            sort,
            require,
            applied_budget,
        )
    else:
        chosen = _named(
            named,
            model_key,
            pairs,
            only_set,
            ignore_set,
            order,
            order_index,
            require,
            applied_budget,
        )
        skipped = ()
    if chosen.provider not in only_set or _model_key(chosen.model) != model_key:
        raise Refuse("NOT_ALLOWED", "provider")
    return _seal(
        model_text,
        chosen,
        sort,
        collection,
        require,
        cred,
        surface_text,
        at_i,
        fence_i,
        applied_cap,
        asked_cap,
        applied_budget,
        asked_budget,
        skipped,
    )


def snapshot(decision: object) -> tuple[RouteRecord, ...]:
    """Return the one record that reproduces `decision`."""
    if type(decision) is not Decision:
        raise Refuse("BAD_RECORD")
    return (
        RouteRecord(
            schema=decision.schema,
            model=decision.model,
            provider=decision.provider,
            sort=decision.sort,
            score=decision.score,
            cost=decision.cost,
            speed=decision.speed,
            latency=decision.latency,
            data_collection=decision.data_collection,
            require_parameters=decision.require_parameters,
            parameters=decision.parameters,
            cred_id=decision.cred_id,
            surface=decision.surface,
            at=decision.at,
            fence=decision.fence,
            cap=decision.cap,
            asked_cap=decision.asked_cap,
            policy_cap=decision.policy_cap,
            budget=decision.budget,
            asked_budget=decision.asked_budget,
            budget_cap=decision.budget_cap,
            skipped=decision.skipped,
            digest=decision.digest,
        ),
    )


def _head(records: Sequence[object]) -> object:
    if len(records) != 1:
        raise Refuse("DUPLICATE")
    for item in records:
        return item
    raise Refuse("BAD_RECORD")


def rebuild(records: object) -> Decision:
    """Reproduce the public decision from the record `snapshot` emitted."""
    seq = _as_seq(records, "BAD_RECORD")
    if len(seq) == 0:
        raise Refuse("BAD_RECORD")
    row = _head(seq)
    if type(row) is not RouteRecord:
        raise Refuse("BAD_RECORD")
    return Decision(
        schema=row.schema,
        model=row.model,
        provider=row.provider,
        sort=row.sort,
        score=row.score,
        cost=row.cost,
        speed=row.speed,
        latency=row.latency,
        data_collection=row.data_collection,
        require_parameters=row.require_parameters,
        parameters=row.parameters,
        cred_id=row.cred_id,
        surface=row.surface,
        at=row.at,
        fence=row.fence,
        cap=row.cap,
        asked_cap=row.asked_cap,
        policy_cap=row.policy_cap,
        budget=row.budget,
        asked_budget=row.asked_budget,
        budget_cap=row.budget_cap,
        skipped=row.skipped,
        digest=row.digest,
    )


__all__ = [
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
