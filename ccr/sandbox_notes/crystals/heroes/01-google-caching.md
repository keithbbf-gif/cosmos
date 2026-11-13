# 01-google-caching

Role: GOOGLE-DOCS

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 380, 'out': 464, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
The fetched page states that Gemini 3.8 Flash is available. Implicit caching is enabled by default for Gemini 2.5 and newer models across both stateful and stateless calls, and cost savings are applied whenever a request hits the cache. For Gemini 3.8 Flash, the minimum input required to trigger context caching is 4,096 tokens. To optimize cache hits, large common content should be placed at the beginning of the prompt, and requests sharing a similar prefix should be sent close together in time. The count of cached tokens is reported in `usage.total_cached_tokens`. The document also details explicit caching, where content is sent once and referenced in subsequent requests, with a time-to-live (TTL) defaulting to 1 hour if not explicitly set.

**What it does not say**
The source does not provide the exact pricing breakdown, discount percentages, or storage fees associated with implicit versus explicit cache hits. It does not state the maximum token capacity for a cache, eviction policies beyond the default 1-hour explicit TTL, or the exact latency impact of cache hits. Furthermore, it does not define how Gemini caching maps to COSMOS agent-memory schemas, checkpoints, or ledger projection lifecycles. Any detail regarding whether caching operates identically across Vertex AI endpoints versus the Google AI Studio Gemini API is UNMEASURED.

**One consequence for a provisional COSMOS Crystals note**
Because Gemini 3.8 Flash enforces a strict 4,096-token minimum prefix before caching activates, any provisional crystal artifact formatted as a prefix note (such as demoted memory state or base schemas) must meet or exceed 4,096 tokens and be placed consistently at the front of prompt assemblies to yield cached-token savings.

**Open questions**
1. Does the 4,096-token minimum threshold apply strictly to the static prefix alone, or to the entire aggregate input prompt before eviction evaluation occurs?
2. How does the default 1-hour TTL on explicit caches align with the operational cadence of ORC boots and Spidercaster ledger write cycles?
3. What specific eviction or invalidation behavior occurs when slight variations are introduced into the front-loaded crystal prefix?
