# LMNator session notes, through 2026-10-28

Worth keeping. No keys. No .env values.

## Site
- Live: https://lmnator.com/arcade.html
- Host: MochaHost 65.181.111.252, cPanel user papafigc, docroot /home/papafigc/lmnator.com. Never .232.
- DNS is Cloudflare, zone lmnator.com, origin that IP. CF token cannot purge cache. HTML has been DYNAMIC.
- DirectoryIndex is index.html then index.php. WordPress files stay. Do not delete them.
- Upload with Fileman/save_file_content into the docroot. Subdirs often do not exist. Put pack-*.js in the docroot, not packs/.
- Download zip: https://lmnator.com/download.php
- Install: manifest.webmanifest + sw.js, Add to Home Screen.
- Source: V:\A\Ai\COSMOS\work_orders\ccr\hero_lmnator_muse\site\
- Keys file path only: V:\Streams\webdev\keys\.env. Never source it. Never print values.

## Games
- Arcade loads many pack-*.js into window.LMN_PACK, then engines.js.
- Engines: match3, blast, runner, stack, merge, memory, snake, breakout, whack, slide, word, idle, cards, lane, board, rhythm, farm, quiz.
- Match-3 scores only a straight line of three. An L of two neighbors is not a match.
- Pay: no button. localStorage lmn-first-play. Silent for 14 days, then one line, no price.
- Runs log: /home/papafigc/lmn_runs.jsonl via queue.php op save. Read at https://lmnator.com/runs.php. No player names.
- Queue: queue.php. Human and/or AI teammate and enemy. Game ids must match ^[sm][0-9]{2}$ or higher|tiles|derby.
- Argon once set LMN_PACK to {}. That wipes the array. Publish only push().

## Seats that ship code
- Grok 4.7: one file path, do not read the tree. Shared SGH pool, about 500M until the evening of 2026-10-29. Other teams use it. Do not explore.
- Argon: gemini-4-argon, project project-cc5302c9-190c-4cdf-87d, key path V:\Research4\.secrets\vertex_medicineman_key.txt. HTTP 200 confirmed. System line must say push() and name the keys. It writes near-miss copy when shown one example.
- Luna 6 Flex: openai/gpt-5.6-luna. Rail forces openai/flex. Ask for four objects, not eight.
- Luna 6 MAX: openai/gpt-5.6-luna-pro, reasoning high, same Flex. Not a separate MAX slug.
- Both Lunas rename fields unless the example uses inspired and better. Map inspired_by and near_miss only if a mouth already shipped. Do not teach the wrong names.

## Seats that plan instead of code
- DeepSeek: deepseek/deepseek-v4.1-flash-1017. 1017 is the release date, not the score. Undated deepseek-v4.1-flash is the wrong pin. Both are in PINNED_VALUE as DS41_FLASH and DS41_FLASH_1017. Mouth is a thinking trace. Do not publish until the first characters are window.LMN_PACK. Scar COT-LEAK.
- Muse Spark 1.3: only meta/muse-spark-1.3-contributor, provider meta, no fallback. Bare muse-spark-1.3 is not pinned. No write tool. One-line system. Four objects. A long wrapper, a write tool, or a 25-object ask returns a plan or a 4000-character cut. Do not paste a prefill onto a plan. SOP: hero_teams/spark13/SOP.md. Scar SHORT-SYSTEM.
- GLM: z-ai/glm-5.3-flash, provider relace, allow_fallbacks false. CosmosPaths root must be V:\A\Ai\COSMOS\live or the call never reaches HTTP. Same 4000 cut. Judge mouth restated the rubric. Scar JUDGE-PROSE.

## Prompt that raised Argon and both Lunas
hero_teams/PROMPT_OPT.md. One example object. Keys: id, title, inspired, players, engine, better, goal, speed, lives. better is a near-miss. Four games. No price.

## Scores
- The main database is https://mdata.modelraters.com and W:\MODEL_DB. Feed and sqlite: W:\MODEL_DB\mdata (mdata.sqlite, mdata\v1\). judge_ours.jsonl is a side log. The published slice W:\MODEL_DB\mdata\v1\lmnator_grades.json read SEATING.jsonl and left judge_ours_included false.
- Append: V:\A\Ai\COSMOS\live\state\model_rater\judge_ours.jsonl
- Schema cosmos-model-rater-ours/1. Score in that file is 0-100 (ten times a 0-10).
- Copy: V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\SEATING.jsonl
- Trial: V:\A\Ai\COSMOS\live\state\porosity\trials\lmnator-contest-20261028.json
- A failed attempt is still a row. Fields used: model, axis, score, n, source, note, scar, sop.

## Search notes from the subagents
- V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\SEARCH_SEAT.md
- V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\SEARCH_PINS.md
- V:\A\Ai\COSMOS\work_orders\ccr\hero_teams\SEARCH_SCORES.md
- The loader reads judge_ours.jsonl only. SEATING.jsonl is a copy. A failed attempt still needs score 0 plus schema, at, model, axis, n, note, source, scar, and sop. A missing score stays UNMEASURED.

## Summon
py -3.14 work_orders\ccr\_summon_or_hero.py --pack <dir> --duds <dir>\DUDS.json --model <exact pin> --out <file>
Pack before the call: AGENTS.md, exact SKU, via, WRAP.md, STYLE.md, SKILL.md or none extra, tools, isolated cwd, TASK.md.
DUD what must be text, python, or no_prose. javascript is rejected.
ACTIVE is HTTP ok, first line NONE or diff --git, runtime SKU match. A 200 with a preamble is not ACTIVE.
grok.exe as a worker is a refuse. Grok in this session is the in-session seat, one file, no tree walk.
