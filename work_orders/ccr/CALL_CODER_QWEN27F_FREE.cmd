@echo off
REM HERO CODER Qwen 3.8 27B :free — OR named pin. No :floor on :free.
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-qwen27f --model qwen/qwen3.8-27b:free --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\QWEN27F_HERO_last.txt
echo EXIT %ERRORLEVEL%
