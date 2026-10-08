"""Tests for context-reference expansion."""

from __future__ import annotations

import pytest

from context_references import (
    ENTRY_CAP,
    NAME_CAP,
    POLICY_CAP,
    SCHEMA,
    ContextRecord,
    ExpandedContext,
    FetchDescriptor,
    SkippedRef,
    descriptors,
    expand,
    rebuild,
)
from cosmos_hermes import Refuse


def _fetch(items: tuple[FetchDescriptor, ...], index: int) -> FetchDescriptor:
    return items[index]


def test_success_expands_file_folder_diff_and_url() -> None:
    message = "Review @file:note, list @folder:src? @diff @url:https://example.com."
    result = expand(
        message,
        files={"note": "alpha"},
        folders={"src": "tree\nline"},
        diff="patch",
    )
    assert result.schema == SCHEMA
    assert result.cap == POLICY_CAP
    assert result.skipped == ()
    assert result.text == (
        "Review [file:note], list [folder:src]? [diff] [url NEED_FETCH].\n"
        "\n"
        "--- Attached Context ---\n"
        "--- file:note ---\n"
        "alpha\n"
        "--- folder:src ---\n"
        "tree\nline\n"
        "--- diff ---\n"
        "patch\n"
        "--- url NEED_FETCH ---\n"
        "https://example.com"
    )
    assert result.records == (
        ContextRecord("file", "note", "alpha", ""),
        ContextRecord("folder", "src", "tree\nline", ""),
        ContextRecord("diff", "", "patch", ""),
        ContextRecord("url", "", "https://example.com", "NEED_FETCH"),
    )
    assert result.records[3].code == "NEED_FETCH"
    assert descriptors(result) == (FetchDescriptor("https://example.com"),)
    assert "example page" not in result.text
    assert rebuild(result) == result
    again = expand(
        message,
        files={"note": "alpha"},
        folders={"src": "tree\nline"},
        diff="patch",
    )
    assert again == result


def test_plain_message_and_http_url_with_path() -> None:
    plain = expand("nothing to expand")
    assert plain.text == "nothing to expand"
    assert plain.records == ()
    assert plain.cap == POLICY_CAP
    assert rebuild(plain) == plain
    url = "http://example.com:443/a/b?q=1"
    fetched = expand(f"see @url:{url}")
    assert fetched.records[0].text == url
    assert fetched.records[0].code == "NEED_FETCH"
    assert fetched.text.startswith("see [url NEED_FETCH]")
    spaced = "https://example.com/a%20b"
    encoded = expand(f"@url:{spaced}")
    assert _fetch(descriptors(encoded), 0).url == spaced


def test_same_logical_name_is_separate_in_each_catalog() -> None:
    result = expand("@file:item @folder:item", files={"item": "body"}, folders={"item": "list"})
    assert result.records[0].text == "body"
    assert result.records[1].text == "list"


def test_trailing_period_does_not_hide_a_short_name() -> None:
    result = expand("see @file:a.", files={"a": "yes"})
    assert result.records[0].name == "a"
    assert result.text.startswith("see [file:a].")


def test_payload_may_contain_dotdot() -> None:
    body = "keep a..b and %2e%2e in the note"
    result = expand("@file:note", files={"note": body})
    assert result.records[0].text == body


def test_bad_names() -> None:
    samples = (
        "@file:..",
        "@file:a..b",
        "@file:a..",
        "@folder:../x",
        "@file:a/b",
        "@folder:a\\b",
        "@file:C:note",
        "@folder:e:notes",
        "@file:",
        "@folder:",
        "@file:%2e%2e",
        "@folder:%2E%2E",
        "@file:%252e%252e",
        "@file:a%2f%2e%2e",
        "@file:%00note",
        "@folder:a\uff0fb",
        "@file:\uff0e\uff0e",
    )
    for token in samples:
        with pytest.raises(Refuse) as caught:
            expand(token, files={"a": "x"}, folders={"a": "x"})
        assert caught.value.code == "BAD_NAME"


def test_catalog_key_with_a_slash_is_bad_name() -> None:
    with pytest.raises(Refuse) as caught:
        expand("hello", files={"a/b": "no", "ok": "yes"})
    assert caught.value.code == "BAD_NAME"


def test_duplicate_canonical_names_refuse() -> None:
    with pytest.raises(Refuse) as caught:
        expand("plain", files={"note": "a", "\uff4e\uff4f\uff54\uff45": "b"})
    assert caught.value.code == "BAD_CATALOG"
    assert caught.value.detail == "duplicate"


def test_missing_file_folder_and_diff() -> None:
    with pytest.raises(Refuse) as missing_file:
        expand("@file:note", files={}, folders={"note": "only-a-folder"})
    assert missing_file.value.code == "MISSING"
    assert missing_file.value.detail == "note"
    with pytest.raises(Refuse) as missing_folder:
        expand("@folder:src", folders={})
    assert missing_folder.value.code == "MISSING"
    with pytest.raises(Refuse) as missing_diff:
        expand("what changed @diff")
    assert missing_diff.value.code == "MISSING"
    assert missing_diff.value.detail == "diff"
    empty = expand("@diff", diff="")
    assert empty.records[0].text == ""


def test_unknown_at_tokens() -> None:
    for token in ("@staged", "@git:5", "@", "@file", "@folder", "@diff:now", "ping a@b.com"):
        with pytest.raises(Refuse) as caught:
            expand(token, diff="unused")
        assert caught.value.code == "BAD_REF"


def test_bad_urls() -> None:
    for token in (
        "@url:",
        "@url:ftp://example.com",
        "@url:file:///tmp/x",
        "@url:FILE:///tmp/x",
        "@url:https://",
        "@url:https://user:pass@example.com",
        "@url:javascript:alert(1)",
        "@url:https://example.com:99999/a",
        "@url:https://example.com:0/a",
        "@url:https://example.com:00000080/a",
        "@url:https://example.com/../secret",
        "@url:https://example.com/%2e%2e/secret",
        "@url:https://example.com/%252e%252e/secret",
        "@url:https://example.com/%00",
        "@url:https://example.com/%",
        "@url:https://example.com/%zz",
        "@url:https://example.com/..",
    ):
        with pytest.raises(Refuse) as caught:
            expand(token)
        assert caught.value.code == "BAD_REF"


def test_higher_cap_is_ignored_and_policy_cap_is_recorded() -> None:
    result = expand("@file:note", files={"note": "z"}, cap=10**9)
    assert result.cap == POLICY_CAP
    absurd = expand("plain", cap=10**18 + 5)
    assert absurd.cap == POLICY_CAP
    payload = "y" * POLICY_CAP
    exact = expand("@file:note", files={"note": payload}, cap=POLICY_CAP + 50)
    assert exact.cap == POLICY_CAP
    assert exact.records[0].text == payload
    with pytest.raises(Refuse) as over:
        expand("@file:note", files={"note": "y" * (POLICY_CAP + 1)}, cap=POLICY_CAP + 99)
    assert over.value.code == "OVERSIZE"
    assert over.value.detail == str(POLICY_CAP)


def test_budget_skips_an_item_and_keeps_a_later_fit() -> None:
    first = "a" * 20_000
    second = "b" * 50_000
    third = "c" * 10_000
    packed = expand(
        "@file:wide @file:middle @file:tail",
        files={"wide": first, "middle": second, "tail": third},
    )
    assert packed.cap == POLICY_CAP
    assert packed.records == (
        ContextRecord("file", "wide", first, ""),
        ContextRecord("file", "tail", third, ""),
    )
    assert packed.skipped == (SkippedRef("file", "middle", "OVERSIZE"),)
    assert second not in packed.text
    assert third in packed.text
    assert rebuild(packed) == packed
    tight = expand(
        "@file:big @file:mid @file:tail",
        files={"big": "123", "mid": "4567", "tail": "89"},
        cap=5,
    )
    assert tight.cap == 5
    assert tuple(record.name for record in tight.records) == ("big", "tail")
    assert "".join(record.text for record in tight.records) == "12389"
    assert tight.skipped == (SkippedRef("file", "mid", "OVERSIZE"),)
    assert "[file:mid SKIPPED]" in tight.text
    assert "4567" not in tight.text
    assert rebuild(tight) == tight
    both = expand("@file:a @file:b", files={"a": "123", "b": "456"}, cap=6)
    assert tuple(record.text for record in both.records) == ("123", "456")
    assert both.skipped == ()


def test_reference_and_name_caps() -> None:
    files = {f"f{index}": "x" for index in range(ENTRY_CAP + 1)}
    with pytest.raises(Refuse) as catalog:
        expand("plain", files=files)
    assert catalog.value.code == "BAD_CATALOG"
    assert catalog.value.detail == "files"
    token = "@url:https://e.test/a"
    message = " ".join([token] * (ENTRY_CAP + 1))
    with pytest.raises(Refuse) as count:
        expand(message)
    assert count.value.code == "BAD_REF"
    assert count.value.detail == "count"
    with pytest.raises(Refuse) as name:
        expand("plain", files={"n" * (NAME_CAP + 1): "x"})
    assert name.value.code == "OVERSIZE"
    assert name.value.detail == str(NAME_CAP)


def _expect_secret(message: object, **kwargs: object) -> None:
    with pytest.raises(Refuse) as caught:
        expand(
            message,
            files=kwargs.get("files"),
            folders=kwargs.get("folders"),
            diff=kwargs.get("diff"),
        )
    assert caught.value.code == "SECRET"


def test_secret_shapes_refuse() -> None:
    secret = "sk-liveSecretKey"
    _expect_secret(f"look {secret}")
    _expect_secret("@file:note", files={"note": secret})
    _expect_secret("@folder:src", folders={"src": "Bearer abcdefghijk"})
    _expect_secret("@diff", diff="api_key=supersecret")
    _expect_secret(f"@url:https://example.com/{secret}")
    _expect_secret("plain", diff=secret)
    _expect_secret("plain", files={"note": secret})
    with pytest.raises(Refuse) as built:
        ContextRecord("file", "note", secret, "")
    assert built.value.code == "SECRET"


def test_repr_omits_payload() -> None:
    result = expand("@file:note @url:https://example.com", files={"note": "super-secret-body"})
    blob = repr(result) + repr(result.records[0]) + repr(result.records[1])
    blob += repr(_fetch(descriptors(result), 0))
    assert "super-secret-body" not in blob
    assert "sk-" not in blob
    assert "Bearer" not in blob
    assert "api_key=" not in blob


def test_not_text_null_and_catalog_type() -> None:
    with pytest.raises(Refuse) as message:
        expand(12)
    assert message.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as nul:
        expand("a\x00b")
    assert nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as file_type:
        expand("@file:note", files={"note": 5})
    assert file_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as unused:
        expand("plain", files={"note": 5})
    assert unused.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as file_nul:
        expand("@file:note", files={"note": "a\x00b"})
    assert file_nul.value.code == "NULL_BYTE"
    with pytest.raises(Refuse) as diff_type:
        expand("plain", diff=b"patch")
    assert diff_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as key_type:
        expand("plain", files={1: "x"})
    assert key_type.value.code == "NOT_TEXT"
    with pytest.raises(Refuse) as files_type:
        expand("plain", files=["note"])
    assert files_type.value.code == "BAD_CATALOG"
    assert files_type.value.detail == "files"
    with pytest.raises(Refuse) as folders_type:
        expand("plain", folders=("src",))
    assert folders_type.value.code == "BAD_CATALOG"
    assert folders_type.value.detail == "folders"


def test_cap_argument_type_and_range() -> None:
    with pytest.raises(Refuse) as flag:
        expand("plain", cap=True)
    assert flag.value.code == "NOT_INT"
    with pytest.raises(Refuse) as text:
        expand("plain", cap="10")
    assert text.value.code == "NOT_INT"
    with pytest.raises(Refuse) as low:
        expand("plain", cap=0)
    assert low.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as negative:
        expand("plain", cap=-3)
    assert negative.value.code == "OUT_OF_RANGE"


def test_direct_records_refuse_a_raised_cap_and_a_bad_code() -> None:
    with pytest.raises(Refuse) as kind:
        ContextRecord("git", "", "x", "")
    assert kind.value.code == "BAD_REF"
    with pytest.raises(Refuse) as code:
        ContextRecord("url", "", "https://example.com", "FETCHED")
    assert code.value.code == "BAD_REF"
    with pytest.raises(Refuse) as fetched:
        FetchDescriptor("file:///tmp/x")
    assert fetched.value.code == "BAD_REF"
    with pytest.raises(Refuse) as descriptor_code:
        FetchDescriptor("https://example.com", "FETCHED")
    assert descriptor_code.value.code == "BAD_REF"
    with pytest.raises(Refuse) as schema:
        ExpandedContext("other", "hi", (), POLICY_CAP)
    assert schema.value.code == "BAD_REF"
    with pytest.raises(Refuse) as raised:
        ExpandedContext(SCHEMA, "hi", (), POLICY_CAP + 1)
    assert raised.value.code == "OUT_OF_RANGE"
    with pytest.raises(Refuse) as stale:
        rebuild(ExpandedContext(SCHEMA, "tampered", (ContextRecord("file", "note", "alpha", ""),), POLICY_CAP))
    assert stale.value.code == "STALE"
    with pytest.raises(Refuse) as foreign:
        rebuild("not-a-context")
    assert foreign.value.code == "BAD_REF"
    held = ContextRecord("url", "", "https://example.com", "NEED_FETCH")
    assert held.code == "NEED_FETCH"
    assert "https://example.com" in repr(held)


def test_left_to_right_stops_on_the_first_refusal() -> None:
    with pytest.raises(Refuse) as caught:
        expand("@file:note @staged", files={"note": "ok"})
    assert caught.value.code == "BAD_REF"


def test_example_context_references() -> None:
    """Session aurora attaches three https notes. A file: URL and a dotdot ref refuse."""
    message = (
        "Session aurora reviews the porch card @url:https://notes.example/cards/porch, "
        "the lamp note @url:https://notes.example/notes/lamp, "
        "and the hall light @url:https://lights.example/hall."
    )
    first = expand(message)
    second = expand(message)
    assert first == second
    fetched = descriptors(first)
    assert fetched == descriptors(second)
    assert len(fetched) == 3
    assert _fetch(fetched, 0).url == "https://notes.example/cards/porch"
    assert _fetch(fetched, 1).url == "https://notes.example/notes/lamp"
    assert _fetch(fetched, 2).url == "https://lights.example/hall"
    assert _fetch(fetched, 0).code == "NEED_FETCH"
    assert _fetch(fetched, 1).code == "NEED_FETCH"
    assert _fetch(fetched, 2).code == "NEED_FETCH"
    head, fence, tail = first.text.partition("\n\n--- Attached Context ---\n")
    assert fence == "\n\n--- Attached Context ---\n"
    assert head == (
        "Session aurora reviews the porch card [url NEED_FETCH], "
        "the lamp note [url NEED_FETCH], "
        "and the hall light [url NEED_FETCH]."
    )
    assert tail == (
        "--- url NEED_FETCH ---\n"
        "https://notes.example/cards/porch\n"
        "--- url NEED_FETCH ---\n"
        "https://notes.example/notes/lamp\n"
        "--- url NEED_FETCH ---\n"
        "https://lights.example/hall"
    )
    assert "porch card" not in _fetch(fetched, 0).url
    assert rebuild(first) == second
    with pytest.raises(Refuse) as file_url:
        expand("Session aurora reads @url:file:///sessions/aurora.env")
    assert file_url.value.code == "BAD_REF"
    with pytest.raises(Refuse) as dotdot:
        expand("Session aurora reads @file:../card", files={"../card": "no"})
    assert dotdot.value.code == "BAD_NAME"
    with pytest.raises(Refuse) as encoded:
        expand("Session aurora reads @url:https://notes.example/%2e%2e/card")
    assert encoded.value.code == "BAD_REF"
