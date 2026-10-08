# Clusters HTTP API

Bind `127.0.0.1`. Prefix `/v1`. Body and response are JSON objects. A list response is `{"items": [...]}`. Errors are HTTP 400, 403, or 409 with `{"error": "<CODE>", "detail": "..."}`.

| Method | Path | Body fields |
|---|---|---|
| GET | `/v1/health` | |
| GET | `/v1/features` | |
| POST | `/v1/projects` | `name`, `root` |
| GET | `/v1/projects` | |
| POST | `/v1/projects/{id}/shortcut` | `slot` |
| POST | `/v1/clusters` | `name`, `project_id`, `parent_id` |
| GET | `/v1/clusters` | query `project` |
| POST | `/v1/clusters/{id}/members` | `member_kind`, `member_id` |
| POST | `/v1/clusters/{id}/manager` | `session_id` |
| POST | `/v1/packs` | `scope`, `target_id`, `rules`, `skills`, `wrappers`, `environments` |
| POST | `/v1/sessions` | `project_id`, `door`, `hero`, `model`, `task`, `role`, `account_id`, `cluster_id`, `parent_id`, `title` |
| GET | `/v1/sessions` | query `project` |
| POST | `/v1/sessions/{id}/status` | `status`, `evidence` |
| POST | `/v1/sessions/{id}/title` | `title`, `evidence` |
| POST | `/v1/sessions/{id}/layout` | `view`, `bounds` |
| POST | `/v1/sessions/{id}/close` | `confirm` |
| POST | `/v1/coordinators` | `scope`, `project_id`, `hero`, `door`, `model` |
| POST | `/v1/coordinators/{id}/goal` | `text` |
| POST | `/v1/coordinators/{id}/plan` | `plan`, `evidence` |
| POST | `/v1/coordinators/{id}/report` | |
| POST | `/v1/coordinators/{id}/close-worker` | `worker_id`, `confirm` |
| POST | `/v1/comms` | `sender_id`, `target_id`, `question` |
| POST | `/v1/comms/setting` | `enabled` |
| POST | `/v1/board/tasks` | `project_id`, `title`, `body`, `column`, `door`, `hero`, `model`, `labels`, `workspace` |
| GET | `/v1/board/tasks` | query `project` |
| POST | `/v1/board/tasks/{id}/move` | `column`, `evidence` |
| POST | `/v1/board/auto` | `limit`, `project_id` |
| POST | `/v1/history/messages` | `session_id`, `role`, `kind`, `body`, `resume_of` |
| GET | `/v1/history/search` | query `q`, `project` |
| GET | `/v1/history/{session_id}/resume` | |
| POST | `/v1/changes` | `session_id`, `path`, `before`, `after`, `diff` |
| GET | `/v1/changes` | query `session` |
| POST | `/v1/git/worktree` | `session_id`, `repo` |
| POST | `/v1/git/commit-proposal` | `session_id`, `summary` |
| POST | `/v1/git/push` | `session_id`, `branch`, `confirmed` |
| POST | `/v1/policy/check` | `command`, `turbo`, `branch` |
| POST | `/v1/policy/limits` | `allow`, `deny` |
| POST | `/v1/spend/budget` | `provider`, `daily_cap_usd`, `daily_cap_tokens`, `mode`, `on_limit`, `window_days`, `day_index` |
| POST | `/v1/spend/observe` | `provider`, `usd`, `tokens`, `source`, `observed`, `day_index` |
| POST | `/v1/spend/bump` | `provider` |
| POST | `/v1/spend/check` | `provider`, `usd`, `tokens` |
| GET | `/v1/spend` | |
| GET | `/v1/doors` | |
| POST | `/v1/accounts` | `provider`, `label`, `profile_dir` |
| POST | `/v1/accounts/{id}/bind` | `session_id` |
| POST | `/v1/mcp` | `project_id`, `server_id`, `enabled` |
| POST | `/v1/mcp/enable-all` | `project_id` |
| GET | `/v1/mcp` | query `project` |
| POST | `/v1/shortcuts` | `kind`, `binding`, `target` |
| GET | `/v1/shortcuts` | |
| POST | `/v1/mobile/pair` | |
| POST | `/v1/mobile/desktop` | `online` |
| POST | `/v1/mobile/message` | `token`, `session_id`, `body` |
| GET | `/v1/notifications` | |
| POST | `/v1/notifications/{id}/see` | |
| POST | `/v1/harness/plan` | `hero`, `task`, `where`, `via`, `execute` |
| POST | `/v1/policy/matrix` | `file`, `shell`, `git`, `network`, `mcp` |
| POST | `/v1/policy/decide` | `category`, `command`, `turbo` |
| POST | `/v1/sessions/{id}/link` | `status`, `evidence`, `detail` |
| POST | `/v1/skills` | `project_id`, `path`, `enabled` |
| GET | `/v1/skills/pack` | query `project` |
| GET | `/v1/skills` | query `project` |
| POST | `/v1/quota/window` | `provider`, `limit_usd`, `period_seconds`, `resets_at`, `source`, `observed` |
| POST | `/v1/quota/used` | `provider`, `used_usd`, `source`, `observed` |
| POST | `/v1/quota/prorata` | `provider`, `now` |
| POST | `/v1/relay/worker` | `coordinator_id`, `worker_id`, `text`, `kind` |
| POST | `/v1/relay/small` | `coordinator_id`, `text` |
| POST | `/v1/relay/delegate` | `global_id`, `project_id`, `text`, `door`, `hero`, `model` |
| POST | `/v1/sessions/{id}/mode` | `mode` |
| POST | `/v1/sessions/{id}/cancel` | |
| POST | `/v1/mobile/follow` | `token` |
| POST | `/v1/shortcuts/seed` | |
| POST | `/v1/board/defaults` | `project_id`, `door`, `hero`, `model`, `reasoning`, `permission`, `workspace` |
| POST | `/v1/board/tasks/{id}/drag` | |
| POST | `/v1/board/tasks/{id}/lightning` | `door`, `hero`, `model`, `reasoning`, `permission`, `workspace` |
| POST | `/v1/board/queue` | `project_id`, `title`, `body`, `door`, `hero`, `model`, `reasoning`, `permission`, `workspace`, `labels` |
| POST | `/v1/git/classify` | `command` |
| POST | `/v1/git/message` | `session_id`, `evidence`, `style` |
| POST | `/v1/git/review` | `session_id`, `summary` |
| GET | `/v1/sessions/{id}/titles` | |
| POST | `/v1/board/tasks/{id}/subtasks` | `title`, `body` |
| GET | `/v1/board/tasks/{id}/subtasks` | |
| POST | `/v1/bookmarks` | `session_id`, `message_id`, `note` |
| POST | `/v1/bookmarks/{id}/hide` | |
| GET | `/v1/bookmarks` | query `session` |
| POST | `/v1/spend/admit` | `provider`, `now`, `usd`, `tokens` |
| POST | `/v1/git/confirm` | `session_id`, `branch`, `clean`, `evidence` |
| POST | `/v1/board/tasks/{id}/isolation` | `base_ref`, `share`, `workspace`, `why`, `paths` |
| POST | `/v1/sessions/{id}/binding` | `door`, `model` |
| GET | `/v1/sessions/{id}/binding` | |
| POST | `/v1/attention` | `session_id`, `reason` |
| GET | `/v1/attention` | query `session` |
| POST | `/v1/sessions/{id}/thread` | `state`, `until` |
| GET | `/v1/sessions/{id}/thread` | |
| POST | `/v1/projects/{id}/preset` | `colour`, `icon`, `door`, `resume`, `turbo` |
| GET | `/v1/projects/{id}/preset` | |
| POST | `/v1/board/tasks/{id}/attach` | `work_style`, `style_text`, `images` |
| POST | `/v1/sessions/{id}/seen` | `path`, `seen` |
| GET | `/v1/sessions/{id}/review` | |
| POST | `/v1/instructions` | `project_id`, `kind`, `path` |
| GET | `/v1/instructions` | query `project` |
| POST | `/v1/projects/{id}/import` | `result` |
| POST | `/v1/sessions/{id}/door-id` | `conversation_id`, `home` |
| GET | `/v1/sessions/{id}/door-id` | |
| POST | `/v1/sessions/{id}/route` | `route`, `path` |
| GET | `/v1/sessions/{id}/route` | |
| POST | `/v1/quota/shape` | `provider`, `shape`, `limit_label`, `source`, `observed` |
| POST | `/v1/quota/shape/gate` | `provider`, `shape` |
| POST | `/v1/sessions/{id}/caps` | `mode`, `provider`, `subagents`, `worktree`, `command_path` |
| GET | `/v1/sessions/{id}/caps` | |
| POST | `/v1/sessions/{id}/host` | `host`, `fact`, `enabled` |
| POST | `/v1/sessions/{id}/env` | `name` |
| POST | `/v1/conflicts` | `session_id`, `path`, `outcome` |
| GET | `/v1/conflicts` | query `session` |
| POST | `/v1/tools` | `project_id`, `server_id`, `tool`, `level` |
| GET | `/v1/tools` | query `project`, `server`, `tool` |
| POST | `/v1/sessions/{id}/headless` | `output_format`, `max_turns`, `sandbox` |
| GET | `/v1/sessions/{id}/headless` | |
| POST | `/v1/sessions/{id}/flags` | `channel`, `role`, `tool_search`, `web_fetch`, `hooks_off`, `auto_update`, `lock_path` |
| GET | `/v1/sessions/{id}/flags` | |
| POST | `/v1/quota/meter` | `provider`, `reading`, `pool`, `auto_reload`, `source`, `observed` |
| POST | `/v1/quota/meter/gate` | `provider`, `pool` |

`evidence` is an object. When a claim needs proof it must include `source` and `observed`. `execute` defaults false. `execute: true` still does not start `grok.exe`.
