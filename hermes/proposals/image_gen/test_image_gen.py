"""image_gen refusals, price, and the prompt cap."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import image_gen
from cosmos_hermes import Refuse, secret_shape
from image_gen import (
    ASPECTS,
    CATALOG,
    DEFAULT_MODEL,
    MAX_CENTS,
    MODELS,
    PROMPT_CAP,
    SCHEMA,
    SOURCE_CAP,
    GenerationJob,
    ImageRequest,
    ModelSpec,
    dispatch,
    native_size,
    rebuild,
    request,
)


def _code(call: Callable[[], object]) -> str:
    with pytest.raises(Refuse) as caught:
        call()
    return caught.value.code


def _no_edit(model: str) -> str:
    return _code(lambda: request(model, "sign", {model: 2}, sources=1))


def _kiln_story() -> tuple[object, ...]:
    prices = {"flux-2-klein": 8}
    order = request(
        "flux-2-klein",
        "frost on a kiln shelf",
        prices,
        aspect="landscape",
        cap=PROMPT_CAP * 5,
    )
    assert order.prompt == "frost on a kiln shelf"
    assert order.prompt_cap == PROMPT_CAP
    assert order.cents == 8
    assert order.priced is True
    assert order.native_size == "landscape_16_9"
    assert "10000" not in repr(order)
    assert "frost on a kiln shelf" not in repr(order)
    job = dispatch(order, "cred-mira-kiln")
    assert job.credential_id == "cred-mira-kiln"
    assert job.prompt == order.prompt
    assert job.priced is True
    assert job.prompt_cap == PROMPT_CAP
    assert "frost on a kiln shelf" not in repr(job)
    assert secret_shape(repr(order)) is False
    assert secret_shape(repr(job)) is False
    restored = rebuild((job,))
    assert restored == (job,)
    secret = _code(lambda: request("flux-2-klein", "api_key=kiln-raw-secret", prices))
    assert secret == "SECRET"
    return (order, job, restored, secret)


def test_schema_allowlist_and_default() -> None:
    assert SCHEMA == "cosmos-hermes-image_gen/1"
    assert DEFAULT_MODEL == "flux-2-klein"
    assert MODELS[0] == DEFAULT_MODEL
    assert MODELS == (
        "flux-2-klein",
        "flux-2-pro",
        "gpt-image-1.5",
        "gpt-image-2",
        "nano-banana-pro",
        "ideogram-v3",
        "recraft-v4",
        "qwen-image",
        "z-image-turbo",
        "krea-v2",
    )
    assert ASPECTS == ("landscape", "square", "portrait")
    assert len(CATALOG) == len(MODELS)
    assert {spec.model_id for spec in CATALOG} == set(MODELS)


def test_priced_request_and_zero_quote() -> None:
    made = request("flux-2-klein", "a serene ridge", {"other": 9, "flux-2-klein": 6})
    assert isinstance(made, ImageRequest)
    assert made.model == "flux-2-klein"
    assert made.cents == 6
    assert made.priced is True
    assert made.prompt == "a serene ridge"
    assert made.prompt_cap == PROMPT_CAP
    assert made.upscale is False
    assert made.upscale_cents == 0
    assert made.aspect == "square"
    assert made.native_size == "square_hd"
    assert made.quality == ""
    again = request("flux-2-klein", "a serene ridge", {"flux-2-klein": 6})
    assert made == again
    assert hash(made) == hash(again)
    free = request("z-image-turbo", "a cat", {"z-image-turbo": 0})
    assert free.cents == 0
    assert free.priced is True
    assert "a serene ridge" not in repr(made)
    assert secret_shape(repr(made)) is False
    assert secret_shape(repr(CATALOG[0])) is False


def test_every_model_and_native_sizes() -> None:
    for spec in CATALOG:
        made = request(spec.model_id, "a red door", {spec.model_id: 10})
        assert made.cents == 10
        assert made.priced is True
        assert made.quality == spec.quality
        assert made.native_size == native_size(spec.model_id)
    assert native_size("flux-2-klein", "landscape") == "landscape_16_9"
    assert native_size("flux-2-pro", "portrait") == "portrait_16_9"
    assert native_size("z-image-turbo", "square") == "square_hd"
    assert native_size("qwen-image", "landscape") == "landscape_16_9"
    assert native_size("recraft-v4", "portrait") == "portrait_16_9"
    assert native_size("ideogram-v3", "square") == "square_hd"
    assert native_size("krea-v2", "landscape") == "landscape_16_9"
    assert native_size("nano-banana-pro", "landscape") == "16:9"
    assert native_size("nano-banana-pro", "square") == "1:1"
    assert native_size("nano-banana-pro", "portrait") == "9:16"
    assert native_size("gpt-image-1.5", "landscape") == "1536x1024"
    assert native_size("gpt-image-1.5", "square") == "1024x1024"
    assert native_size("gpt-image-1.5", "portrait") == "1024x1536"
    assert native_size("gpt-image-2", "landscape") == "landscape_4_3"
    assert native_size("gpt-image-2", "square") == "square_hd"
    assert native_size("gpt-image-2", "portrait") == "portrait_4_3"
    assert request("gpt-image-2", "owl", {"gpt-image-2": 4}).quality == "medium"
    assert request("gpt-image-1.5", "owl", {"gpt-image-1.5": 4}).quality == "medium"


def test_prompt_cap_ignores_caller() -> None:
    prices = {"flux-2-klein": 1}
    body = "b" * PROMPT_CAP
    made = request(DEFAULT_MODEL, body, prices, cap=PROMPT_CAP * 3)
    assert made.prompt == body
    assert made.prompt_cap == PROMPT_CAP
    assert "6000" not in repr(made)
    tight = request(DEFAULT_MODEL, "c" * 50, prices, cap=1)
    assert tight.prompt_cap == PROMPT_CAP
    assert len(tight.prompt) == 50
    assert _code(lambda: request(DEFAULT_MODEL, "d" * (PROMPT_CAP + 1), prices)) == "OVERSIZE"
    assert (
        _code(lambda: request(DEFAULT_MODEL, "e" * (PROMPT_CAP + 1), prices, cap=PROMPT_CAP * 9))
        == "OVERSIZE"
    )


def test_unknown_unpriced_empty_and_secret() -> None:
    prices = {"flux-2-klein": 4}
    assert _code(lambda: request("fal-ai/flux-2-pro", "hello", {"fal-ai/flux-2-pro": 4})) == (
        "UNKNOWN_MODEL"
    )
    assert _code(lambda: request("dalle-3", "hello", {"dalle-3": 4})) == "UNKNOWN_MODEL"
    assert _code(lambda: request("qwen-image", "hello", {})) == "UNPRICED"
    assert _code(lambda: request("qwen-image", "hello", prices)) == "UNPRICED"
    assert _code(lambda: request("flux-2-klein", "", prices)) == "EMPTY"
    assert _code(lambda: request("flux-2-klein", "   \n", prices)) == "EMPTY"
    secret = "sk-abcdefghij"
    assert _code(lambda: request(secret, "hello", {secret: 4})) == "SECRET"
    assert _code(lambda: request("flux-2-klein", secret, prices)) == "SECRET"
    assert _code(lambda: request("flux-2-klein", "hello", {secret: 1, "flux-2-klein": 4})) == (
        "SECRET"
    )
    assert _code(lambda: request("flux-2-klein", "hello", prices, aspect=secret)) == "SECRET"
    plain = request("flux-2-klein", "draw a token on a desk", prices)
    assert plain.priced is True
    assert _code(lambda: native_size(secret)) == "SECRET"


def test_price_table_aspect_flag_and_edit() -> None:
    prices = {"flux-2-klein": 4}
    assert _code(lambda: request("flux-2-klein", "hello", [])) == "BAD_PRICES"  # type: ignore[arg-type]
    assert _code(lambda: request("flux-2-klein", "hello", {1: 2})) == "BAD_PRICES"  # type: ignore[dict-item]
    assert _code(lambda: request("flux-2-klein", "hello", {"flux-2-klein": True})) == "NOT_INT"
    assert _code(lambda: request("flux-2-klein", "hello", {"flux-2-klein": -1})) == "OUT_OF_RANGE"
    assert (
        _code(lambda: request("flux-2-klein", "hello", {"flux-2-klein": MAX_CENTS + 1}))
        == "OUT_OF_RANGE"
    )
    top = request("flux-2-klein", "hello", {"flux-2-klein": MAX_CENTS})
    assert top.cents == MAX_CENTS
    assert _code(lambda: request("flux-2-klein", "hello", prices, aspect="round")) == "BAD_ASPECT"
    assert _code(lambda: request("flux-2-klein", "hello", prices, upscale="yes")) == "BAD_FLAG"  # type: ignore[arg-type]
    assert _code(lambda: request("flux-2-klein", "a\x00b", prices)) == "NULL_BYTE"
    assert _code(lambda: request(None, "hello", prices)) == "NOT_TEXT"  # type: ignore[arg-type]
    assert _code(lambda: request("recraft-v4", "logo", {"recraft-v4": 25}, upscale=True)) == (
        "UNPRICED"
    )
    up = request(
        "recraft-v4",
        "logo",
        {"recraft-v4": 25, "upscale": 3},
        upscale=True,
    )
    assert up.upscale is True
    assert up.cents == 25
    assert up.upscale_cents == 3
    assert up.priced is True
    edited = request("qwen-image", "sign", {"qwen-image": 2}, sources=SOURCE_CAP)
    assert edited.sources == SOURCE_CAP
    assert _code(lambda: request("qwen-image", "sign", {"qwen-image": 2}, sources=SOURCE_CAP + 1)) == (
        "OUT_OF_RANGE"
    )
    for model in ("z-image-turbo", "recraft-v4", "krea-v2"):
        assert _no_edit(model) == "NO_EDIT"
    assert request("ideogram-v3", "sign", {"ideogram-v3": 2}, sources=2).sources == 2
    assert _code(lambda: request("flux-2-klein", "hello", prices, sources=True)) == "NOT_INT"


def test_forged_record_and_catalog() -> None:
    base = request("gpt-image-2", "owl", {"gpt-image-2": 6}, aspect="portrait")
    assert base.native_size == "portrait_4_3"
    params = getattr(ImageRequest, "__dataclass_params__")
    assert params.frozen is True
    assert params.slots is True
    with pytest.raises(FrozenInstanceError):
        setattr(base, "cents", 1)
    assert _code(lambda: replace(base, priced=False)) == "UNPRICED"
    assert _code(lambda: replace(base, prompt_cap=PROMPT_CAP + 5)) == "BAD_CAP"
    assert _code(lambda: replace(base, quality="high")) == "BAD_QUALITY"
    assert _code(lambda: replace(base, native_size="square_hd")) == "BAD_ASPECT"
    assert _code(lambda: replace(base, prompt="sk-abcdefghij")) == "SECRET"
    assert (
        _code(
            lambda: replace(
                base,
                model="z-image-turbo",
                quality="",
                native_size="portrait_16_9",
                sources=1,
            )
        )
        == "NO_EDIT"
    )
    assert (
        _code(
            lambda: ModelSpec(model_id="flux-2-klein", size_family="nope", edit=True, quality="")
        )
        == "BAD_CATALOG"
    )
    assert (
        _code(
            lambda: ModelSpec(
                model_id="flux-2-klein", size_family="preset", edit=True, quality="high"
            )
        )
        == "BAD_QUALITY"
    )


def test_dispatch_credential_and_no_network() -> None:
    order = request("nano-banana-pro", "serene mountain cherry", {"nano-banana-pro": 15})
    job = dispatch(order, "fal-prod")
    assert isinstance(job, GenerationJob)
    assert job.credential_id == "fal-prod"
    assert job.priced is True
    assert job.cents == 15
    assert job.prompt == order.prompt
    assert job.native_size == "1:1"
    assert job.prompt_sha256 == dispatch(order, "fal_prod").prompt_sha256
    same = dispatch(order, "fal-prod")
    assert job == same
    assert "serene mountain cherry" not in repr(job)
    assert secret_shape(repr(job)) is False
    assert _code(lambda: dispatch(order, "")) == "MISSING_CREDENTIAL"
    assert _code(lambda: dispatch(order, "not a token")) == "BAD_CREDENTIAL"
    assert _code(lambda: dispatch(order, "../keys")) == "BAD_CREDENTIAL"
    assert _code(lambda: dispatch(order, "sk-abcdefghij")) == "SECRET"
    assert _code(lambda: dispatch("order", "fal-prod")) == "BAD_ORDER"  # type: ignore[arg-type]
    assert _code(lambda: replace(job, prompt_sha256="abc")) == "BAD_JOB"
    file_name = image_gen.__file__
    assert file_name is not None
    source = Path(file_name).read_text(encoding="utf-8")
    for banned in (
        "urllib",
        "requests",
        "subprocess",
        "socket",
        "http.client",
        "pickle",
        "eval(",
        "exec(",
    ):
        assert banned not in source


def test_example_image_gen() -> None:
    assert _kiln_story() == _kiln_story()


def test_digest_replay_and_malformed() -> None:
    prices = {"flux-2-klein": 4, "upscale": 2}
    order = request("flux-2-klein", "frost on a kiln shelf", prices, upscale=True)
    job = dispatch(order, "cred-mira-kiln")
    assert order.upscale_cents == 2
    assert rebuild((job,)) == (job,)
    assert rebuild(rebuild((job,))) == (job,)
    wrong = "0" * 64
    assert _code(lambda: replace(job, prompt_sha256=wrong)) == "BAD_JOB"
    assert _code(lambda: replace(job, plan_id="f" * 64)) == "BAD_JOB"
    assert _code(lambda: replace(job, prompt="   ")) == "EMPTY"
    assert _code(lambda: replace(job, upscale=False)) == "BAD_FLAG"
    assert _code(lambda: replace(job, sources=SOURCE_CAP + 1)) == "OUT_OF_RANGE"
    assert _code(lambda: replace(job, credential_id=None)) == "NOT_TEXT"  # type: ignore[arg-type]
    assert _code(lambda: replace(job, model=["flux-2-klein"])) == "NOT_TEXT"  # type: ignore[arg-type]
    assert _code(lambda: request(DEFAULT_MODEL, "hello", prices, cap=True)) == "NOT_INT"
    assert _code(lambda: request(DEFAULT_MODEL, "hello", prices, cap=-3)) == "OUT_OF_RANGE"
    assert _code(lambda: request(DEFAULT_MODEL, "frost\ud800", prices)) == "NOT_TEXT"
    secret_price: dict[str, int] = {"flux-2-klein": "api_key=kiln-raw-secret"}  # type: ignore[dict-item]
    assert _code(lambda: request(DEFAULT_MODEL, "hello", secret_price)) == "SECRET"
    assert _code(lambda: request(DEFAULT_MODEL, "hello", "api_key=kiln-raw-secret")) == "SECRET"  # type: ignore[arg-type]
    assert _code(lambda: request(DEFAULT_MODEL, "hello", "flux-2-klein")) == "BAD_PRICES"  # type: ignore[arg-type]
    wide = {f"extra-{index}": 1 for index in range(32)}
    wide["flux-2-klein"] = 4
    assert _code(lambda: request(DEFAULT_MODEL, "hello", wide)) == "BAD_PRICES"
    assert _code(lambda: rebuild((job, job))) == "REPLAY"
    assert _code(lambda: rebuild(())) == "EMPTY"
    assert _code(lambda: rebuild("job")) == "BAD_ORDER"
    assert _code(lambda: rebuild((job, "job"))) == "BAD_ORDER"
    crowd = tuple(dispatch(order, f"cred-{index}") for index in range(65))
    assert _code(lambda: rebuild(crowd)) == "BAD_ORDER"
    bare = request(DEFAULT_MODEL, "hello", prices, cap=PROMPT_CAP * 4)
    assert bare.prompt_cap == PROMPT_CAP
