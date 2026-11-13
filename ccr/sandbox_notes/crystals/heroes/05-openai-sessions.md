# 05-openai-sessions

Role: OPENAI-SESSIONS

Model field: gemini-3.8-flash

HTTP: 200

Tokens in/out/cached: {'in': 339, 'out': 407, 'cached': 0}

Provisional. Pending research, review, and improvement.

### What the source says
A Session stores conversation history so the runner can prepend it before a run and append new items after a run. 

TypeScript ships two session types: `OpenAIConversationsSession` (backed by the Conversations API) and `MemorySession` (local, not intended for production). 

Python documents five session implementations: `SQLiteSession`, `AsyncSQLiteSession`, `RedisSession`, `SQLAlchemySession`, and `MongoDBSession`. 

A session cannot be combined in the same run with `conversation_id`, `previous_response_id`, or `auto_previous_response_id`.

### What the source does not say
The source does not provide schema specifications, storage layouts, or serialization formats for the Python session backends (SQLite, Redis, SQLAlchemy, MongoDB). It does not specify whether sessions support checkpointing, branching, pruning, or demotion to cold storage. It does not state how session eviction or retention policies are managed, nor does it define how sessions interact with external ledgers or multi-agent orchestrations beyond runner prepend/append behavior. Any other details are UNMEASURED.

### One consequence for a provisional COSMOS Crystals note
Because sessions mutate by prepending and appending history around a run and mutually exclude explicit response chaining flags (`conversation_id`, `previous_response_id`, and `auto_previous_response_id`), provisional crystal adapters representing agent memory cannot mix native session-managed persistence with explicit message-id chaining in the same run configuration.

### Open questions
- Does the OpenAI Agents SDK support deriving an immutable crystal snapshot or resume checkpoint directly from an active session instance across both TypeScript and Python runtimes?
- How does the single-ledger writer pattern map to external session stores (such as Redis or SQLite) when multiple agents share or hand off a session context?
- What are the exact serialization and recovery guarantees when converting a session's prepended/appended history into a rebuildable projection?
