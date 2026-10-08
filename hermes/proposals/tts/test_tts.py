"""TTS rail refusals, the success path, and the policy cap."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from cosmos_hermes import Refuse, redact, secret_shape
from tts import PROVIDERS, SCHEMA, TEXT_CAP, AudioRequest, Tts
from tts import __all__ as tts_all

_FORMATS = {
    "edge": "mp3",
    "elevenlabs": "opus",
    "openai": "opus",
    "minimax": "mp3",
    "mistral": "opus",
    "gemini": "pcm",
    "xai": "mp3",
    "neutts": "wav",
    "kitten": "wav",
    "piper": "wav",
    "command": "mp3",
}
_LOCAL = frozenset({"edge", "neutts", "kitten", "piper"})
_CLOUD = ("elevenlabs", "openai", "minimax", "mistral", "gemini", "xai")
_STATUS = "Session bay-session: porch light on card north-card matches note porch-note."
_BANNED = ("socket", "subprocess", "urllib", "requests", "pickle")


def _edge_record(
    *,
    provider: str = "edge",
    text: str = "hello",
    credential_id: str = "",
    cap: int = TEXT_CAP,
    region: str = "",
    audio_format: str = "mp3",
    local: bool = True,
    voice: str = "en-US-AriaNeural",
    speed_milli: int = 1000,
    command: str = "",
) -> AudioRequest:
    return AudioRequest(
        provider=provider,
        text=text,
        credential_id=credential_id,
        cap=cap,
        region=region,
        audio_format=audio_format,
        local=local,
        voice=voice,
        speed_milli=speed_milli,
        command=command,
    )


def _story() -> AudioRequest:
    rail = Tts()
    rail.select("openai", credential_id="cred-voice", voice="alloy", cap=9000)
    spoken = rail.synthesize(_STATUS, max_text_length=8000)
    with pytest.raises(Refuse) as caught:
        rail.synthesize("Session bay-session note porch-note Bearer abcdefghijk")
    assert caught.value.code == "SECRET"
    assert caught.value.detail == ""
    assert "abcdefghijk" not in str(caught.value)
    again = rail.synthesize(_STATUS)
    assert again == spoken
    return spoken


def test_schema_and_allowlist() -> None:
    assert SCHEMA == "cosmos-hermes-tts/1"
    assert TEXT_CAP == 4000
    assert PROVIDERS == (
        "edge",
        "elevenlabs",
        "openai",
        "minimax",
        "mistral",
        "gemini",
        "xai",
        "neutts",
        "kitten",
        "piper",
        "command",
    )
    assert set(tts_all) == {"SCHEMA", "TEXT_CAP", "PROVIDERS", "AudioRequest", "Tts"}


def test_example_tts() -> None:
    first = _story()
    second = _story()
    assert first == second
    assert first.provider == "openai"
    assert first.credential_id == "cred-voice"
    assert first.cap == TEXT_CAP
    assert first.command == ""
    assert first.local is False
    assert first.audio_format == "opus"
    assert first.voice == "alloy"
    assert first.speed_milli == 1000
    assert "north-card" in first.text
    assert "porch-note" in first.text
    assert secret_shape(repr(first)) is False


def test_no_provider_before_select() -> None:
    rail = Tts()
    with pytest.raises(Refuse) as caught:
        rail.synthesize("hello")
    assert caught.value.code == "NO_PROVIDER"
    with pytest.raises(Refuse) as unknown:
        rail.select("deepinfra")
    assert unknown.value.code == "UNKNOWN_PROVIDER"
    with pytest.raises(Refuse) as still:
        rail.synthesize("hello")
    assert still.value.code == "NO_PROVIDER"


def test_malformed_text_before_select() -> None:
    rail = Tts()
    with pytest.raises(Refuse) as kind:
        rail.synthesize(12)
    assert kind.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as empty:
        rail.synthesize(" \n\t")
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as nul:
        rail.synthesize("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as over:
        rail.synthesize("b" * (TEXT_CAP + 1))
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == "4000"
    with pytest.raises(Refuse) as secret_field:
        rail.synthesize("b" * (TEXT_CAP + 1), note="sk-livekeyvalue")
    assert secret_field.value.code == "SECRET"
    with pytest.raises(Refuse) as still:
        rail.synthesize("hello")
    assert still.value.code == "NO_PROVIDER"


@pytest.mark.parametrize("name", ["deepinfra", "kittentts", "nous", "Edge", ""])
def test_unknown_provider(name: str) -> None:
    with pytest.raises(Refuse) as caught:
        Tts().select(name)
    assert caught.value.code == "UNKNOWN_PROVIDER"


def test_rails_are_independent() -> None:
    selected = Tts()
    idle = Tts()
    assert selected.select("edge") == "edge"
    with pytest.raises(Refuse) as caught:
        idle.synthesize("hello")
    assert caught.value.code == "NO_PROVIDER"
    assert selected.synthesize("hello").provider == "edge"


@pytest.mark.parametrize("name", ["edge", "neutts", "kitten", "piper", "command"])
def test_local_and_command_success(name: str) -> None:
    rail = Tts()
    assert rail.select(name) == name
    first = rail.synthesize("hello")
    second = rail.synthesize("hello")
    assert first == second
    assert first.provider == name
    assert first.text == redact("hello")
    assert first.credential_id == ""
    assert first.cap == TEXT_CAP
    assert first.region == ""
    assert first.audio_format == _FORMATS[name]
    assert first.local is (name in _LOCAL)
    assert first.speed_milli == 1000
    assert first.command == ""
    assert secret_shape(repr(first)) is False
    if name in ("neutts", "command"):
        assert first.voice == ""
    else:
        assert first.voice != ""


@pytest.mark.parametrize("name", _CLOUD)
def test_cloud_requires_credential_id(name: str) -> None:
    rail = Tts()
    with pytest.raises(Refuse) as missing:
        rail.select(name)
    assert missing.value.code == "MISSING_CREDENTIAL"
    assert rail.select(name, credential_id=f"cred-{name}") == name
    request = rail.synthesize("hello")
    assert request.provider == name
    assert request.credential_id == f"cred-{name}"
    assert request.local is False
    assert request.audio_format == _FORMATS[name]
    assert request.cap == TEXT_CAP
    assert request.command == ""
    if name == "minimax":
        assert request.region == "global"
    else:
        assert request.region == ""


def test_cap_is_policy() -> None:
    rail = Tts()
    rail.select("edge", max_text_length=9000, cap=9000)
    request = rail.synthesize("a" * TEXT_CAP, max_text_length=8000, cap=10**9)
    assert request.cap == TEXT_CAP
    assert request.text == "a" * TEXT_CAP
    assert len(request.text) == 4000
    with pytest.raises(Refuse) as over:
        rail.synthesize("b" * (TEXT_CAP + 1), max_text_length=8000)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == "4000"
    short_ask = Tts()
    short_ask.select("edge", max_text_length=10)
    kept = short_ask.synthesize("hello world")
    assert kept.cap == TEXT_CAP
    assert kept.text == "hello world"
    flagged = Tts()
    flagged.select("edge", cap=True, max_text_length=1.5)
    ignored = flagged.synthesize("hello", cap=False, max_text_length=-1)
    assert ignored.cap == TEXT_CAP
    assert ignored.text == "hello"


@pytest.mark.parametrize(
    "sample",
    ["sk-livekeyvalue", "Authorization: Bearer abcdefghijk", "token=supersecret"],
)
def test_secret_text_raises(sample: str) -> None:
    rail = Tts()
    rail.select("edge")
    with pytest.raises(Refuse) as caught:
        rail.synthesize(sample)
    assert caught.value.code == "SECRET"
    assert sample not in str(caught.value)
    assert caught.value.detail == ""


def test_secret_before_select_and_api_key_field() -> None:
    rail = Tts()
    with pytest.raises(Refuse) as early:
        rail.synthesize("sk-livekeyvalue")
    assert early.value.code == "SECRET"
    with pytest.raises(Refuse) as named:
        rail.select("edge", api_key="")
    assert named.value.code == "SECRET"
    with pytest.raises(Refuse) as folded:
        rail.select("edge", Api_Key="x")
    assert folded.value.code == "SECRET"
    with pytest.raises(Refuse) as nested:
        rail.synthesize("hello", options=[{"voice": "Aria", "api_key": "x"}])
    assert nested.value.code == "SECRET"
    with pytest.raises(Refuse) as shaped:
        rail.select("edge", note="api_key=raw-material")
    assert shaped.value.code == "SECRET"
    with pytest.raises(Refuse) as key_id:
        rail.select("openai", credential_id="sk-12345678")
    assert key_id.value.code == "SECRET"


def test_empty_null_and_type() -> None:
    rail = Tts()
    with pytest.raises(Refuse) as blank_name:
        rail.select(None)
    assert blank_name.value.code == "NOT_TEXT"
    rail.select("edge")
    with pytest.raises(Refuse) as empty:
        rail.synthesize("")
    assert empty.value.code == "EMPTY"
    with pytest.raises(Refuse) as spaces:
        rail.synthesize(" \n\t")
    assert spaces.value.code == "EMPTY"
    with pytest.raises(Refuse) as nul:
        rail.synthesize("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as kind:
        rail.synthesize(12)
    assert kind.value.code == "NOT_TEXT"


def test_bad_credential_region_voice_and_speed() -> None:
    cloud = Tts()
    with pytest.raises(Refuse) as bad_id:
        cloud.select("openai", credential_id="not a token")
    assert bad_id.value.code == "BAD_CREDENTIAL"
    with pytest.raises(Refuse) as kind:
        cloud.select("openai", credential_id=12)
    assert kind.value.code == "BAD_CREDENTIAL"
    minimax = Tts()
    assert minimax.select("minimax", credential_id="mm-cn", region="cn") == "minimax"
    assert minimax.synthesize("hello").region == "cn"
    with pytest.raises(Refuse) as region:
        minimax.select("minimax", credential_id="mm-cn", region="eu")
    assert region.value.code == "BAD_REGION"
    assert minimax.synthesize("hello").region == "cn"
    with pytest.raises(Refuse) as synth_region:
        minimax.synthesize("hello", region="eu")
    assert synth_region.value.code == "BAD_REGION"
    assert minimax.synthesize("hello").region == "cn"
    with pytest.raises(Refuse) as edge_region:
        Tts().select("edge", region="global")
    assert edge_region.value.code == "BAD_REGION"
    voiced = Tts()
    voiced.select("openai", credential_id="oa-1", voice="nova")
    assert voiced.synthesize("hello").voice == "nova"
    with pytest.raises(Refuse) as path:
        voiced.synthesize("hello", voice="../voices/a.onnx")
    assert path.value.code == "BAD_VOICE"
    assert voiced.synthesize("hello").voice == "nova"
    with pytest.raises(Refuse) as drive:
        Tts().select("piper", voice=r"C:\voices\a.onnx")
    assert drive.value.code == "BAD_VOICE"
    fast = Tts()
    fast.select("xai", credential_id="xai-main", speed=1.5)
    assert fast.synthesize("hello").speed_milli == 1500
    fast.select("xai", credential_id="xai-main", speed=0.7)
    assert fast.synthesize("hello").speed_milli == 700
    assert fast.synthesize("hello", speed=1.0).speed_milli == 1000
    assert fast.synthesize("hello").speed_milli == 700
    with pytest.raises(Refuse) as too_fast:
        fast.select("xai", credential_id="xai-main", speed=1.6)
    assert too_fast.value.code == "BAD_SPEED"
    assert fast.synthesize("hello").speed_milli == 700
    with pytest.raises(Refuse) as flag:
        Tts().select("edge", speed=True)
    assert flag.value.code == "BAD_SPEED"
    with pytest.raises(Refuse) as nan:
        Tts().select("edge", speed=float("nan"))
    assert nan.value.code == "BAD_SPEED"
    Tts().select("openai", credential_id="oa-1", speed=0.25)
    Tts().select("openai", credential_id="oa-1", speed=4)
    Tts().select("kitten", speed=0.5)
    Tts().select("kitten", speed=2)
    held = Tts()
    held.select("minimax", credential_id="mm-1", speed=1)
    assert held.synthesize("hello").speed_milli == 1000
    with pytest.raises(Refuse) as edge_speed:
        Tts().select("edge", speed=3)
    assert edge_speed.value.code == "BAD_SPEED"


def test_credential_on_synthesize_must_match() -> None:
    rail = Tts()
    rail.select("openai", credential_id="oa-1")
    assert rail.synthesize("hello", credential_id="oa-1").credential_id == "oa-1"
    with pytest.raises(Refuse) as caught:
        rail.synthesize("hello", credential_id="oa-2")
    assert caught.value.code == "BAD_CREDENTIAL"
    rail.select("edge")
    assert rail.synthesize("hello").credential_id == ""
    rail.select("piper", credential_id="piper-local")
    assert rail.synthesize("hello").credential_id == "piper-local"
    assert rail.synthesize("hello").local is True


def test_command_and_url_fields_refuse() -> None:
    rail = Tts()
    rail.select("edge")
    with pytest.raises(Refuse) as command:
        rail.select("command", command="piper --out out.wav")
    assert command.value.code == "BAD_FIELD"
    assert rail.synthesize("hello").provider == "edge"
    with pytest.raises(Refuse) as url:
        Tts().select("xai", credential_id="cred-voice", base_url="https://api.x.ai/v1")
    assert url.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as nested:
        Tts().select("edge", meta={"Base_URL": "https://example.invalid/tts"})
    assert nested.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as persona:
        Tts().select("gemini", credential_id="gem-1", persona_prompt_file="butler.md")
    assert persona.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as shaped:
        Tts().select("edge", command="api_key=raw-material")
    assert shaped.value.code == "SECRET"
    spoken = Tts()
    assert spoken.select("command", command="") == "command"
    request = spoken.synthesize("hello")
    assert request.command == ""
    assert request.provider == "command"
    assert request.local is False


def test_bad_field_depth_and_width() -> None:
    with pytest.raises(Refuse) as field:
        Tts().select("edge", note=object())
    assert field.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as raw:
        Tts().select("edge", meta=[b"raw"])
    assert raw.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as key:
        Tts().select("edge", meta=[{1: "x"}])
    assert key.value.code == "BAD_FIELD"
    node: object = {"leaf": "ok"}
    for _ in range(8):
        node = {"wrap": node}
    with pytest.raises(Refuse) as deep:
        Tts().select("edge", nest=node)
    assert deep.value.code == "TOO_DEEP"
    wide = {f"k{index}": "v" for index in range(65)}
    with pytest.raises(Refuse) as width:
        Tts().select("edge", **wide)
    assert width.value.code == "TOO_WIDE"
    Tts().select("edge", meta={"note": "calm"})


def test_record_invariants_and_frozen() -> None:
    with pytest.raises(Refuse) as limit:
        _edge_record(cap=TEXT_CAP + 1)
    assert limit.value.code == "BAD_LIMIT"
    with pytest.raises(Refuse) as fmt:
        _edge_record(audio_format="exe")
    assert fmt.value.code == "BAD_FORMAT"
    with pytest.raises(Refuse) as secret:
        _edge_record(text="sk-livekeyvalue")
    assert secret.value.code == "SECRET"
    with pytest.raises(Refuse) as local:
        _edge_record(local=False)
    assert local.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as command:
        _edge_record(command="ffmpeg -i in.mp3 out.ogg")
    assert command.value.code == "BAD_FIELD"
    with pytest.raises(Refuse) as speed:
        _edge_record(speed_milli=3000)
    assert speed.value.code == "BAD_SPEED"
    with pytest.raises(Refuse) as unknown:
        _edge_record(provider="deepinfra")
    assert unknown.value.code == "UNKNOWN_PROVIDER"
    request = Tts().select("edge")
    assert request == "edge"
    spoken = Tts()
    spoken.select("edge")
    record = spoken.synthesize("hello")
    with pytest.raises(AttributeError):
        setattr(record, "text", "other")
    assert record.voice == "en-US-AriaNeural"
    assert record.command == ""


def test_imports_stay_local() -> None:
    source = Path(__file__).with_name("tts.py").read_text(encoding="utf-8")
    for banned in _BANNED:
        assert banned not in source
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            found.add(node.module.split(".")[0])
    assert found == {
        "__future__",
        "math",
        "re",
        "collections",
        "dataclasses",
        "typing",
        "cosmos_hermes",
    }
