# 06-openai-release

Role: OPENAI-RELEASE

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 335, 'out': 333, 'cached': 0}

Provisional. Pending research, review, and improvement.

**What the source says**  
The npm page for `@openai/agents` version 0.20.0 was published approximately three days prior to the 2026-10-12 fetch. The page lists features including agents, sandbox agents, guardrails, human in the loop, sessions, and tracing. Configuration instructions specify setting `OPENAI_API_KEY` for text and sandbox agents, and using a short-lived client token for browser realtime. No feature named "crystal" appears on the page.

**What it does not say**  
The source does not mention internal architecture, storage backends, or persistence mechanisms for sessions or tracing. It does not provide implementation details for sandbox agents, guardrails, or human-in-the-loop flows. Any relationship between `@openai/agents` sessions and durable agent-memory artifacts, checkpoints, or schemas is UNMEASURED.

**One consequence for a provisional COSMOS Crystals note**  
Because `@openai/agents` provides primitive constructs like "sessions" and "tracing" without defining a formal durable memory artifact or crystal equivalent, any provisional COSMOS Crystals projection must treat external OpenAI agent sessions as unverified runtime state rather than relying on native upstream crystal abstractions.

**Open questions**  
- Do `@openai/agents` "sessions" persist state durably across execution restarts, or are they ephemeral runtime memory?  
- UNMEASURED: Does the package export serialization schemas suitable for mapping directly into a COSMOS resume checkpoint?  
- How do sandbox agent execution contexts interact with local sandbox notes read on boot by ORC?
