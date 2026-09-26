@echo off
REM HERO CODER Gemma 4 26B :free — OpenRouter named pin. Not rotator. Not grok.exe.
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-gemma426b --model google/gemma-4-26b-a4b-it:free --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\GEMMA426B_HERO_last.txt
echo EXIT %ERRORLEVEL%
