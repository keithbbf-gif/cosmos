# 02-google-forum

Role: GOOGLE-FORUM

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 313, 'out': 285, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**
In the Google AI Developers Forum thread 'Context caching in Gemini', a Google reply states that both explicit and implicit caching rely on KV caching. Explicit caching allows a user to pass content once and reuse it, provides control over persistence, and is cheaper at volume. Implicit caching is enabled by default, often requires a minimum token count, and does not guarantee that the cache persists between requests.

**What it does not say**
The source does not state the exact minimum token count required for implicit caching, the specific pricing breakdown or cost differential at volume, or the exact persistence durations or TTL controls available for explicit caching. It also does not mention how Google's context caching interacts with COSMOS ledgers, the Spidercaster role, or Crystals schema design.

**One consequence for a provisional COSMOS Crystals note**
For durable agent-memory artifacts like Crystals, relying on implicit caching is insufficient for guaranteed reuse across requests, so any provisional design requiring deterministic persistence and volume cost-efficiency must specify explicit context caching.

**Open questions**
* What is the exact minimum token threshold required to trigger implicit context caching?
* UNMEASURED: What are the explicit caching TTL limits, renewal mechanisms, and precise volume thresholds where cost savings begin?
* UNMEASURED: How should Spidercaster structure Crystals schema checkpoints to align directly with Gemini's explicit KV cache boundary requirements?
