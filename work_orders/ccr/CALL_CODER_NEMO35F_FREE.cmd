@echo off
REM HERO CODER Nemotron 3.5 Lightning :free — OR named pin. No :floor on :free.
cd /d V:\A\Ai\COSMOS
py -3.14 work_orders\ccr\_summon_or_hero.py --pack V:\A\Ai\COSMOS\live\work\openrouter\hero-coder-nemo35f --model nvidia/nemotron-3.5-lightning:free --routing off --out V:\A\Ai\COSMOS\work_orders\ccr\NEMO35F_HERO_last.txt
echo EXIT %ERRORLEVEL%
