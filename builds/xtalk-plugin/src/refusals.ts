export type RefusalKind =
  | "NO_TOKEN"
  | "CORE_UNREACHABLE"
  | "BAD_ARGS"
  | "NOT_COMPOSED"
  | "BAD_ROLE"
  | "BIND_READONLY"
  | "UNMEASURED"
  | (string & {});

export class XTalkPluginRefusal extends Error {
  readonly kind: RefusalKind;
  constructor(kind: RefusalKind, detail: string) {
    super(`[${kind}] ${detail}`);
    this.kind = kind;
    this.name = "XTalkPluginRefusal";
  }
}

export function refuse(kind: RefusalKind, detail: string): never {
  throw new XTalkPluginRefusal(kind, detail);
}

export function scrub(text: string, secrets: Array<string | undefined>): string {
  let out = text;
  for (const s of secrets) {
    if (s && s.length >= 4) out = out.split(s).join("<redacted>");
  }
  return out;
}
