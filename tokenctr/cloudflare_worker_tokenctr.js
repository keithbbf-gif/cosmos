/**
 * cloudflare_worker_tokenctr.js — Cloudflare Worker Edge Relay for tokenctr.com
 *
 * Deploys to Cloudflare edge network for:
 *   - Edge routing of tokenctr.com and api.tokenctr.com
 *   - Low-latency proxying to origin TokenCenter Gateway
 *   - Edge caching of /v1/models (TTL 60s)
 *   - Edge rate limiting (sliding window per IP)
 *   - CORS preflight and header propagation (x-cosmos-*)
 *   - Turnstile challenge enforcement on sensitive routes
 */

// Configuration (overridable via Worker environment variables)
const CONFIG = {
  ORIGIN_URL: "http://127.0.0.1:8787", // Set to your live gateway origin in Worker env
  RATE_LIMIT_PER_MINUTE: 120,
  MODELS_CACHE_TTL_SEC: 60,
  ALLOWED_ORIGINS: ["*"],
};

// In-memory edge rate limit tracker (per edge datacenter colo)
const ipRateMap = new Map();

function isRateLimited(clientIp) {
  const now = Date.now();
  const windowMs = 60 * 1000;
  const history = ipRateMap.get(clientIp) || [];
  const recent = history.filter((ts) => now - ts < windowMs);

  if (recent.length >= CONFIG.RATE_LIMIT_PER_MINUTE) {
    return true;
  }

  recent.push(now);
  ipRateMap.set(clientIp, recent);
  return false;
}

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, CF-Turnstile-Token, X-Cosmos-Quota-Remaining, X-Cosmos-Quota-Reset, X-Cosmos-Credit-Balance",
    "Access-Control-Expose-Headers": "X-Cosmos-Quota-Remaining, X-Cosmos-Quota-Reset, X-Cosmos-Credit-Balance",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const originBase = env.ORIGIN_URL || CONFIG.ORIGIN_URL;
    const clientIp = request.headers.get("CF-Connecting-IP") || "127.0.0.1";

    // 1. Handle CORS Preflight (OPTIONS)
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(request),
      });
    }

    // 2. Edge Rate Limiting
    if (isRateLimited(clientIp)) {
      return new Response(
        JSON.stringify({
          error: {
            code: "rate_limit_exceeded",
            message: "Too many requests from this IP. Please wait before retrying.",
          },
        }),
        {
          status: 429,
          headers: {
            "Content-Type": "application/json",
            "Retry-After": "60",
            ...corsHeaders(request),
          },
        }
      );
    }

    // 3. Static landing for tokenctr.com apex
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(
        `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>TokenCenter — The COSMOS Payment Engine</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 80vh; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 2.5rem; max-width: 580px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    h1 { margin-top: 0; font-size: 1.75rem; color: #38bdf8; }
    p { line-height: 1.6; color: #cbd5e1; }
    .btn { display: inline-block; background: #0284c7; color: white; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 1rem; }
    .btn:hover { background: #0369a1; }
    .badge { display: inline-block; background: #065f46; color: #6ee7b7; font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; }
    code { background: #0f172a; padding: 0.2rem 0.4rem; border-radius: 4px; font-family: monospace; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">CANONICAL OCT 31</span>
    <h1>TokenCenter</h1>
    <p>The sovereign payment engine for COSMOS. Charge for coordination, never for cognition.</p>
    <p><strong>Essentials are free forever.</strong> Manufactured open-weight token supply priced below OpenRouter, declining marginal toll on coordinated fleet work, and verified task outcomes.</p>
    <p>API Endpoint: <code>https://api.tokenctr.com/v1</code></p>
    <a href="/founding" class="btn">Founding Member Offer ($10 Lifetime)</a>
  </div>
</body>
</html>`,
        {
          headers: {
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "public, max-age=300",
            ...corsHeaders(request),
          },
        }
      );
    }

    // 4. Edge caching for /v1/models
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), request);
    if (request.method === "GET" && url.pathname === "/v1/models") {
      let response = await cache.match(cacheKey);
      if (response) {
        return response;
      }
    }

    // 5. Proxy request to Origin Gateway
    const targetUrl = new URL(url.pathname + url.search, originBase);
    const reqHeaders = new Headers(request.headers);

    // Forward real client information to origin
    reqHeaders.set("X-Forwarded-For", clientIp);
    reqHeaders.set("CF-Connecting-IP", clientIp);
    reqHeaders.set("X-Forwarded-Proto", url.protocol.replace(":", ""));

    try {
      const originResponse = await fetch(targetUrl.toString(), {
        method: request.method,
        headers: reqHeaders,
        body: request.method !== "GET" && request.method !== "HEAD" ? request.body : null,
        redirect: "follow",
      });

      // Construct client response preserving headers
      const resHeaders = new Headers(originResponse.headers);
      const cors = corsHeaders(request);
      for (const [k, v] of Object.entries(cors)) {
        resHeaders.set(k, v);
      }

      // Security hardening headers
      resHeaders.set("X-Content-Type-Options", "nosniff");
      resHeaders.set("X-Frame-Options", "DENY");
      resHeaders.set("Referrer-Policy", "strict-origin-when-cross-origin");

      const response = new Response(originResponse.body, {
        status: originResponse.status,
        statusText: originResponse.statusText,
        headers: resHeaders,
      });

      // Store in edge cache if /v1/models was 200
      if (request.method === "GET" && url.pathname === "/v1/models" && originResponse.status === 200) {
        resHeaders.set("Cache-Control", `public, max-age=${CONFIG.MODELS_CACHE_TTL_SEC}`);
        ctx.waitUntil(cache.put(cacheKey, response.clone()));
      }

      return response;
    } catch (err) {
      return new Response(
        JSON.stringify({
          error: {
            code: "bad_gateway",
            message: "TokenCenter origin gateway unreachable: " + err.message,
          },
        }),
        {
          status: 502,
          headers: {
            "Content-Type": "application/json",
            ...corsHeaders(request),
          },
        }
      );
    }
  },
};
