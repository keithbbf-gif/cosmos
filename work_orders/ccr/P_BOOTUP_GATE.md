# Gitur BUILD — NO_BOOTUP gate (durable BootUP.json)

Repo: PRIVATE keithbbf-gif/cosmos. Branch ccr/bootup-gate from main.
MUST commit and open PR.

Do: cosmos/cosmos_session.py start_session writes live/state/control/BOOTUP.json
open:true. close_session sets open:false. require_bootup() raises NO_BOOTUP
if missing/closed. Wire tests/test_session.py or cosmos/_bite_bootup.py all_bite:true.

Scar: cosmos.py session start is a one-shot Kernel; in-memory Session dies on
CLI exit. CREW spawned blind. 5a --prompt-file is headless and EXITS after last
turn; 5b is grok --cwd --fullscreen -r same uuid. Never 5a twice.

Must not: cDeck mix, leftover PRs, skins, second Core.
Reuse: cosmos_clock.atomic_json, cosmos_paths.role state/control.
