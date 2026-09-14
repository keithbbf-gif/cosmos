// Typed refusals for the session plugin. A kind is the product, not a stack trace.
// Mirrors builds/session-tools/refusals.py so one vocabulary crosses both runtimes.

export type RefusalKind =
  | "NO_SOURCE"
  | "NOT_FOUND"
  | "LEGAL_OMITTED"
  | "LEN_MISMATCH"
  | "HASH_MISMATCH"
  | "SCHEMA_UNKNOWN"
  | "NO_TOKEN"
  | "CORE_UNREACHABLE"
  | "BAD_ARGS"
  | "UNMEASURED"
  | (string & {}); // HTTP_<code> is minted at the call site

export class SessionPluginRefusal extends Error {
  readonly kind: RefusalKind;

  constructor(kind: RefusalKind, detail: string) {
    super(`[${kind}] ${detail}`);
    this.kind = kind;
    this.name = "SessionPluginRefusal";
  }
}

export function refuse(kind: RefusalKind, detail: string): never {
  throw new SessionPluginRefusal(kind, detail);
}

// Bearer material must never reach a result, a log line, or an error string.
export function scrub(text: string, secrets: Array<string | undefined>): string {
  let out = text;
  for (const s of secrets) {
    if (s && s.length >= 4) out = out.split(s).join("<redacted>");
  }
  return out;
}
