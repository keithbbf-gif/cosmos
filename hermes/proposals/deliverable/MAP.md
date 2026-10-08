# deliverable

Hermes deliverable mode attaches files the agent already wrote. In a messaging gateway the agent mentions an absolute or home-relative path in plain reply text. The gateway ignores paths inside fenced blocks and inline code, drops source extensions such as `.py` and `.log`, and classifies the rest by extension. Images and video embed inline, audio goes out as a voice attachment, and documents, data, geospatial files, presentations, archives, and web pages go out as file attachments. A kanban completion can name artifact paths. The notifier uploads the ones that still exist and skips a missing path. Native upload is the platform file API. This proposal does not upload and does not read the host disk.

The live COSMOS tree has no deliverable module. This proposal is a new seam. The assigned slice is a hash check of one relative name against a caller-supplied snapshot.

`expect(name, media, sha256_hex, snapshot)` returns a frozen `Deliverable` when `snapshot[name]` is non-empty, its sha256 equals `sha256_hex`, and the extension's category equals `media`. The name is an exact snapshot key, not a host path. A `.` segment is kept and is not normalized. An absolute name, a `..` segment, an empty or slash-only path, or a backslash is `BAD_NAME`. Percent-encoding is not a key: an encoded NUL is `NULL_BYTE`, a decoded secret is `SECRET`, and any other `%` form is `BAD_NAME`. A missing key is `INCOMPLETE`. The digest is hashed once from the bounded bytes and compared with `const_eq`. A mismatch is `HASH` and is not retried. One flipped byte refuses. `upload()` raises `NO_UPLOAD`. The policy byte cap is 1_048_576. A higher request is ignored, and the recorded cap stays 1_048_576. A lower positive cap is kept and recorded. A value of the wrong type raises `Refuse`, not `ValueError`, `KeyError`, or `UnicodeDecodeError`.

Authority sits in the attempt workspace. The caller supplies the snapshot bytes. The record is a descriptor (`inline`, `voice`, or `file`) for a later gateway. There is no ledger write and no retry.

Refusal codes: `BAD_DIGEST`, `BAD_LIMIT`, `BAD_MEDIA`, `BAD_NAME`, `BAD_SCHEMA`, `EMPTY`, `HASH`, `INCOMPLETE`, `NOT_BYTES`, `NOT_INT`, `NOT_MAP`, `NOT_TEXT`, `NO_UPLOAD`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `SOURCE`.

CCr would land this later by calling `expect` on bytes already in the attempt workspace before a human attaches a file to chat. The frozen record names the category and the disposition. `upload` stays refused inside the turn. A gateway outside this process performs the platform upload only after that human confirms the record.

## Ship

- operations: `NAME_CAP`, `POLICY_CAP`, `SCHEMA`, `Deliverable`, `expect`, `upload`
- refusal codes: `BAD_DIGEST`, `BAD_LIMIT`, `BAD_MEDIA`, `BAD_NAME`, `BAD_SCHEMA`, `EMPTY`, `HASH`, `INCOMPLETE`, `NOT_BYTES`, `NOT_INT`, `NOT_MAP`, `NOT_TEXT`, `NO_UPLOAD`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `SOURCE`
- what this module still refuses to execute: native chat upload, host-path resolution, disk reads and writes, archive unpack, media transcode, gateway send, and a second hash after `HASH`
- hot-path shape: one snapshot lookup, one latin-1 secret scan, one sha256; a mismatch refuses with no retry
