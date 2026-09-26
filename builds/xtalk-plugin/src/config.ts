import { readFileSync } from "node:fs";
import { refuse } from "./refusals.ts";

export const DEFAULT_CORE_URL = "http://127.0.0.1:8770";
export type Env = Record<string, string | undefined>;
export type Config = {
  coreUrl: string;
  token: string | undefined;
  loopback: boolean;
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
  if (!token) refuse("NO_TOKEN", "COSMOS_API_TOKEN_FILE is empty or whitespace");
  return token;
}

export function loadConfig(env: Env): Config {
  const coreUrl = (env.COSMOS_CORE_URL || DEFAULT_CORE_URL).replace(/\/+$/, "");
  const inline = (env.COSMOS_API_TOKEN || "").trim();
  const tokenFile = (env.COSMOS_API_TOKEN_FILE || "").trim();
  const token = inline || (tokenFile ? readTokenFile(tokenFile) : undefined);
  return { coreUrl, token, loopback: isLoopback(coreUrl) };
}
