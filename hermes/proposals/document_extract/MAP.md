# document_extract

Hermes `read_file` turns a document into text the agent can page through. Jupyter notebooks, Word, Excel, and SQLite convert with the standard library. SQLite is a read-only schema preview (create statements, row counts, a short sample, indexes, views, triggers), and a file whose magic is not SQLite is refused with the real reason. PDF, legacy Office, OpenDocument, RTF, and ePub need the optional `firecrawl-anydoc` converter, installed on first use only when lazy installs are permitted; without it those bytes stay behind the binary-file guard. Output is Markdown inside the caller's offset and limit. A file over 50 MB is refused. Notebook outputs longer than 20,000 characters are truncated. A scanned PDF with no text layer is not OCR'd in the reader: when more than 20% of pages or at least 10 pages yield no text, the result carries a coverage warning that names the empty ranges. Bytes fetched from a remote terminal backend convert on the host. East Asian phonetic guides annotate a cell or run and are not part of the extracted value. Balanced git conflict markers in the returned range are counted; a lone marker is not.

The live COSMOS tree has no document module. This proposal is a new seam. The assigned slice is in-process `txt` and `md` only.

`extract(kind, data, cap=None)` returns an `Extract` record for `txt` and `md`. `Extract.text` is strict UTF-8. `Extract.cap` is the cap that was applied. `pdf` and `docx` raise `NEED_EXTRACTOR` and are not parsed. `zip` raises `ARCHIVE` and is not unpacked. Any other kind raises `BAD_KIND`. The kind string is the only format signal. Magic bytes do not select a parser. A direct `Extract` uses that same kind check, so a record cannot claim a pdf, docx, or zip result. `extract` ignores a cap above 256_000. A record whose stored cap is already above 256_000 raises `BAD_LIMIT`.

Authority lives in the attempt workspace. The caller supplies bytes already taken from that workspace. This module opens no path, starts no install, and writes nothing. The policy cap is 256_000 bytes on the input and the same number of characters on the decoded text. A higher request is ignored, and the recorded cap stays 256_000. A lower positive cap is kept and recorded.

Refusal codes: `BAD_KIND`, `BAD_LIMIT`, `DECODE`, `NEED_EXTRACTOR`, `ARCHIVE`, `NULL_BYTE`, `NOT_TEXT`, `NOT_BYTES`, `OVERSIZE`, `OUT_OF_RANGE`.

CCr lands this later as a pure helper on the attempt-workspace read path. `txt` and `md` stay in-process under the recorded cap. `pdf` and `docx` stay `NEED_EXTRACTOR` until a separate extractor is approved. `zip` stays `ARCHIVE`, so an archive is never unpacked inside the turn. The helper grows no network install and no lazy package fetch.

## Ship

- operations: `POLICY_CAP`, `SCHEMA`, `Extract`, `extract`
- refusal codes: `ARCHIVE`, `BAD_KIND`, `BAD_LIMIT`, `DECODE`, `NEED_EXTRACTOR`, `NOT_BYTES`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`
- still refuses to execute: PDF parse and OCR, docx and other Office conversion, zip unpack, notebook or xlsx or SQLite conversion, lazy install, network fetch, and any path read
- hot-path shape: one pass — set-membership on the kind, refuse pdf, docx, and zip before the payload is read, bound the bytes once, decode utf-8 once, bound the text once
