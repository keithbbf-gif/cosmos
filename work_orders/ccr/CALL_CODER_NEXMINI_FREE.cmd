@echo off
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-nexmini --model nex-agi/nex-n2.5-mini:free --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\NEXMINI_HERO_last.txt
echo EXIT %ERRORLEVEL%
