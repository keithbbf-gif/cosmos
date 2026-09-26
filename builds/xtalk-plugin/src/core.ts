import type { Config } from "./config.ts";
import { refuse, scrub, XTalkPluginRefusal } from "./refusals.ts";

export const XTALK_PATH = "/api/v1/xtalk";
export const XTALK_SCHEMA = "cosmos-xtalk/1";

export type FetchLike = (
  url: string,
  init?: { method?: string; headers?: Record<string, string>; body?: string },
) => Promise<{ status: number; json: () => Promise<unknown> }>;

export type CoreResponse = { status: number; body: Record<string, unknown> };

function headers(cfg: Config): Record<string, string> {
  const h: Record<string, string> = { Accept: "application/json" };
  if (cfg.token) h.Authorization = `Bearer ${cfg.token}`;
  return h;
}

export async function coreCall(
  cfg: Config,
  path: string,
  init: { method?: string; body?: Record<string, unknown> } = {},
  fetchImpl: FetchLike = globalThis.fetch as unknown as FetchLike,
): Promise<CoreResponse> {
  if (!cfg.loopback && !cfg.token) {
    refuse("NO_TOKEN", `${cfg.coreUrl} is not loopback and no COSMOS_API_TOKEN is set`);
  }
  const url = `${cfg.coreUrl}${path}`;
  let res: Awaited<ReturnType<FetchLike>>;
  try {
    res = await fetchImpl(url, {
      method: init.method || "GET",
      headers: {
        ...headers(cfg),
        ...(init.body ? { "Content-Type": "application/json" } : {}),
      },
      body: init.body ? JSON.stringify(init.body) : undefined,
    });
  } catch (e) {
    refuse("CORE_UNREACHABLE", scrub(`${url}: ${(e as Error).message}`, [cfg.token]));
  }
  let body: unknown;
  try {
    body = await res.json();
  } catch {
    body = {};
  }
  const obj = (body && typeof body === "object" ? body : {}) as Record<string, unknown>;
  if (res.status !== 200) {
    const kind = String(obj.error || `HTTP_${res.status}`);
    throw new XTalkPluginRefusal(kind, scrub(String(obj.detail || "no detail"), [cfg.token]));
  }
  return { status: res.status, body: obj };
}
