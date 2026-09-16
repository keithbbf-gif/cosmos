// Host environment is the only configuration source. No credential lives in this
// repo, and nothing here walks a tree looking for a live root (cosmos_paths scar:
// existence is not identity).

import { readFileSync } from "node:fs";
import { refuse } from "./refusals.ts";

export const DEFAULT_CORE_URL = "http://127.0.0.1:8770";

export type Env = Record<string, string | undefined>;

export type Config = {
  coreUrl: string;
  /** Bearer value, resolved at call time. Never written anywhere. */
  token: string | undefined;
  loopback: boolean;
  transcriptDir: string | undefined;
  rolledFeed: string | undefined;
};

const LOOPBACK_HOSTS = new Set(["127.0.0.1", "localhost", "::1", "[::1]"]);

export function isLoopback(url: string): boolean {
  try {
    return LOOPBACK_HOSTS.has(new URL(url).hostname.toLowerCase());
  } catch {
    return false;
  }
}

function readTokenFile(path: string): string {
  let raw: string;
  try {
    raw = readFileSync(path, "utf8");
  } catch (e) {
    refuse("NO_TOKEN", `COSMOS_API_TOKEN_FILE unreadable: ${(e as Error).message}`);
  }
  const token = raw.trim();
  // Core refuses a blank api_token.txt as an open door. So does the client.
  if (!token) refuse("NO_TOKEN", "COSMOS_API_TOKEN_FILE is empty or whitespace");
  return token;
}

export function loadConfig(env: Env): Config {
  const coreUrl = (env.COSMOS_CORE_URL || DEFAULT_CORE_URL).replace(/\/+$/, "");
  const inline = (env.COSMOS_API_TOKEN || "").trim();
  const tokenFile = (env.COSMOS_API_TOKEN_FILE || "").trim();
  const token = inline || (tokenFile ? readTokenFile(tokenFile) : undefined);
  return {
    coreUrl,
    token,
    loopback: isLoopback(coreUrl),
    transcriptDir: (env.COSMOS_TRANSCRIPT_DIR || "").trim() || undefined,
    rolledFeed: (env.COSMOS_ROLLED_FEED || "").trim() || undefined,
  };
}

/** The store path, or a refusal. A missing dir is NO_SOURCE — never a guessed root. */
export function requireTranscriptDir(cfg: Config): string {
  if (!cfg.transcriptDir) {
    refuse("NO_SOURCE", "COSMOS_TRANSCRIPT_DIR is unset - this plugin does not guess a root");
  }
  return cfg.transcriptDir;
}

export function requireRolledFeed(cfg: Config): string {
  if (!cfg.rolledFeed) {
    refuse("NO_SOURCE", "COSMOS_ROLLED_FEED is unset - rolled-event/1 is not emitted here yet");
  }
  return cfg.rolledFeed;
}
